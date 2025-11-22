#!/usr/bin/env python3
"""
Master pipeline script for ORB_SLAM3 + Open3D dense reconstruction.

This script runs the complete pipeline:
0. (Optional) Extract frames from bag file
1. Create associations file
2. Run ORB_SLAM3
3. Convert trajectory to Open3D format
4. Dense TSDF reconstruction
"""

import os
import sys
import yaml
import argparse
import subprocess
from pathlib import Path


def load_config(config_file):
    """Load pipeline configuration from YAML file."""
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{'='*80}")
    print(f"{description}")
    print(f"{'='*80}")
    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=False, text=True)

    if result.returncode != 0:
        print(f"\n❌ Error: {description} failed with code {result.returncode}")
        return False

    print(f"\n✓ {description} completed successfully")
    return True


def main():
    parser = argparse.ArgumentParser(description="Run ORB_SLAM3 + Open3D pipeline")
    parser.add_argument('--config', type=str,
                       default='config/pipeline/default.yaml',
                       help='Path to pipeline configuration YAML')
    parser.add_argument('--extract', action='store_true',
                       help='Extract frames from bag file first')
    parser.add_argument('--start_step', type=int, default=1,
                       help='Start from step N (1=associations, 2=SLAM, 3=convert, 4=reconstruct)')
    parser.add_argument('--bag', type=str,
                       help='Override bag file path from config')

    args = parser.parse_args()

    # Get script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Load configuration
    print("="*80)
    print("ORB_SLAM3 + Open3D Dense Reconstruction Pipeline")
    print("="*80)

    config_path = args.config
    if not os.path.isabs(config_path):
        config_path = os.path.join(script_dir, config_path)

    print(f"\nLoading config: {config_path}")
    config = load_config(config_path)

    # Override bag file if specified
    if args.bag:
        config['dataset']['bag_file'] = args.bag
        # Update related paths
        bag_name = Path(args.bag).stem
        bag_dir = Path(args.bag).parent
        config['dataset']['frames_dir'] = str(bag_dir / bag_name)
        config['dataset']['intrinsic_file'] = str(bag_dir / bag_name / 'intrinsic.json')

    # Display configuration
    print(f"\nConfiguration:")
    print(f"  Bag file: {config['dataset']['bag_file']}")
    print(f"  Frames dir: {config['dataset']['frames_dir']}")
    print(f"  Output dir: {config['output']['base_dir']}")
    print(f"  Voxel size: {config['reconstruction']['voxel_size']}m")

    # Setup paths
    frames_dir = config['dataset']['frames_dir']
    intrinsic_file = config['dataset']['intrinsic_file']
    output_base = config['output']['base_dir']
    sparse_dir = os.path.join(output_base, config['output']['sparse_dir'])
    dense_dir = os.path.join(output_base, config['output']['dense_dir'])

    associations_file = os.path.join(output_base, 'associations.txt')
    trajectory_tum = os.path.join(sparse_dir, 'trajectory_tum.txt')
    trajectory_o3d = os.path.join(sparse_dir, 'trajectory_open3d.log')
    mesh_file = os.path.join(dense_dir, config['output']['mesh_name'])

    # Create output directories
    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)

    # Step 0: Extract frames (optional)
    if args.extract:
        if args.start_step <= 0:
            cmd = [
                'python', 'scripts/00_extract_frames.py',
                '--bag', config['dataset']['bag_file'],
                '--output', frames_dir,
                '--stride', str(config['extraction']['frame_stride']),
                '--max_frames', str(config['extraction']['max_frames'])
            ]

            if not run_command(cmd, "Step 0: Extract frames from bag file"):
                return 1

    # Check if frames exist
    if not os.path.exists(frames_dir):
        print(f"\n❌ Error: Frames directory not found: {frames_dir}")
        print("Run with --extract to extract frames from bag file first")
        return 1

    # Step 1: Create associations
    if args.start_step <= 1:
        cmd = [
            'python', 'scripts/create_associations.py',
            '--dataset', frames_dir,
            '--output', associations_file
        ]

        if not run_command(cmd, "Step 1: Create associations file"):
            return 1

    # Step 2: Run ORB_SLAM3
    if args.start_step <= 2:
        cmd = ['./scripts/01_run_orbslam3.sh', frames_dir]

        if not run_command(cmd, "Step 2: Run ORB_SLAM3"):
            return 1

        # Check if trajectory was created
        if not os.path.exists(trajectory_tum):
            print(f"\n❌ Error: ORB_SLAM3 did not generate trajectory file")
            return 1

    # Step 3: Convert trajectory
    if args.start_step <= 3:
        cmd = [
            'python', 'scripts/02_convert_trajectory.py',
            '--input', trajectory_tum,
            '--output_log', trajectory_o3d
        ]

        if not run_command(cmd, "Step 3: Convert trajectory to Open3D format"):
            return 1

    # Step 4: Dense reconstruction
    if args.start_step <= 4:
        cmd = [
            'python', 'scripts/03_dense_reconstruction.py',
            '--frames_dir', frames_dir,
            '--intrinsic', intrinsic_file,
            '--trajectory', trajectory_o3d,
            '--output', mesh_file,
            '--voxel_size', str(config['reconstruction']['voxel_size']),
            '--depth_max', str(config['reconstruction']['depth_max'])
        ]

        if not run_command(cmd, "Step 4: Dense TSDF reconstruction"):
            return 1

    # Pipeline complete!
    print("\n" + "="*80)
    print("🎉 PIPELINE COMPLETE!")
    print("="*80)
    print(f"\nOutput mesh: {mesh_file}")
    print(f"Mesh size: {os.path.getsize(mesh_file) / (1024**2):.1f} MB")

    print("\nVisualize with:")
    print(f'  python -c "import open3d as o3d; mesh = o3d.io.read_triangle_mesh(\'{mesh_file}\'); o3d.visualization.draw_geometries([mesh])"')

    return 0


if __name__ == "__main__":
    sys.exit(main())
