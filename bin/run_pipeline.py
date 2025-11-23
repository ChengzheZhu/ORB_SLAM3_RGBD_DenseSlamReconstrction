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

    # Get project root (parent of bin directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    # Load configuration
    print("="*80)
    print("ORB_SLAM3 + Open3D Dense Reconstruction Pipeline")
    print("="*80)

    config_path = args.config
    if not os.path.isabs(config_path):
        config_path = os.path.join(project_root, config_path)

    print(f"\nProject root: {project_root}")
    print(f"Loading config: {config_path}")
    config = load_config(config_path)

    # Resolve relative paths in config to absolute paths
    for key in ['slam_dir', 'camera_config', 'vocab_file']:
        if key in config.get('orbslam', {}):
            path = config['orbslam'][key]
            if not os.path.isabs(path):
                config['orbslam'][key] = os.path.join(project_root, path)

    if 'base_dir' in config.get('output', {}):
        path = config['output']['base_dir']
        if not os.path.isabs(path):
            config['output']['base_dir'] = os.path.join(project_root, path)

    # Override bag file if specified
    if args.bag:
        config['dataset']['bag_file'] = args.bag
        # Update related paths
        bag_name = Path(args.bag).stem
        bag_dir = Path(args.bag).parent
        config['dataset']['frames_dir'] = str(bag_dir / bag_name)
        config['dataset']['intrinsic_file'] = str(bag_dir / bag_name / 'intrinsic.json')

    # Display configuration
    recon_mode = config.get('reconstruction', {}).get('mode', 'mesh')
    print(f"\nConfiguration:")
    print(f"  Bag file: {config['dataset']['bag_file']}")
    print(f"  Frames dir: {config['dataset']['frames_dir']}")
    print(f"  Output dir: {config['output']['base_dir']}")
    print(f"  Reconstruction mode: {recon_mode}")
    if recon_mode in ['mesh', 'both']:
        print(f"  Mesh voxel size: {config['reconstruction']['mesh']['voxel_size']}m")
    if recon_mode in ['pointcloud', 'both']:
        print(f"  Point cloud voxel size: {config['reconstruction']['pointcloud']['downsample_voxel']}m")

    # Setup paths
    frames_dir = config['dataset']['frames_dir']
    intrinsic_file = config['dataset']['intrinsic_file']
    output_base = config['output']['base_dir']
    sparse_dir = os.path.join(output_base, config['output']['sparse_dir'])
    dense_dir = os.path.join(output_base, config['output']['dense_dir'])

    associations_file = os.path.join(output_base, 'associations.txt')
    trajectory_tum = os.path.join(sparse_dir, 'CameraTrajectory.txt')
    trajectory_o3d = os.path.join(sparse_dir, 'trajectory_open3d.log')
    mesh_file = os.path.join(dense_dir, config['output']['mesh_name'])

    trajectory_json = os.path.join(sparse_dir, "trajectory_posegraph.json")
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
        # Add headless flag based on config
        headless_flag = [] if config['orbslam'].get('use_viewer', True) else ['--headless']
        cmd = ['./scripts/01_run_orbslam3.sh'] + headless_flag + [frames_dir]

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
            '--output_log', trajectory_o3d,
            '--output_json', trajectory_json
        ]

        if not run_command(cmd, "Step 3: Convert trajectory to Open3D format"):
            return 1

    # Step 4: Dense reconstruction
    recon_mode = config.get('reconstruction', {}).get('mode', 'mesh')
    
    if args.start_step <= 4:
        # Create pointcloud output directory if needed
        if recon_mode in ['pointcloud', 'both']:
            pointcloud_dir = os.path.join(dense_dir, config['output'].get('pointcloud_dir', 'pointclouds'))
            os.makedirs(pointcloud_dir, exist_ok=True)
        
        # Run TSDF mesh reconstruction
        if recon_mode in ['mesh', 'both']:
            mesh_config = config['reconstruction']['mesh']
            cmd = [
                'python', 'scripts/03_dense_reconstruction.py',
                '--frames_dir', frames_dir,
                '--intrinsic', intrinsic_file,
                '--trajectory', trajectory_o3d,
                '--output', mesh_file,
                '--voxel_size', str(mesh_config['voxel_size']),
                '--depth_max', str(mesh_config['depth_max'])
            ]
            
            if not run_command(cmd, "Step 4a: TSDF mesh reconstruction"):
                return 1
        
        # Run point cloud export
        if recon_mode in ['pointcloud', 'both']:
            pc_config = config['reconstruction']['pointcloud']
            cmd = [
                'python', 'scripts/04_export_point_clouds.py',
                '--frames_dir', frames_dir,
                '--intrinsic', intrinsic_file,
                '--trajectory', trajectory_o3d,
                '--output_dir', pointcloud_dir,
                '--depth_scale', '1000.0',
                '--depth_max', str(pc_config['depth_max']),
                '--downsample_voxel', str(pc_config['downsample_voxel']),
                '--frame_skip', str(pc_config['frame_skip'])
            ]
            
            if pc_config.get('export_individual', False):
                cmd.append('--export_individual')
            
            step_name = "Step 4b: Point cloud export" if recon_mode == 'both' else "Step 4: Point cloud export"
            if not run_command(cmd, step_name):
                return 1

    # Pipeline complete!
    print("\n" + "="*80)
    print("🎉 PIPELINE COMPLETE!")
    print("="*80)
    
    recon_mode = config.get('reconstruction', {}).get('mode', 'mesh')
    
    # Display mesh output
    if recon_mode in ['mesh', 'both']:
        if os.path.exists(mesh_file):
            print(f"\nMesh output: {mesh_file}")
            print(f"Mesh size: {os.path.getsize(mesh_file) / (1024**2):.1f} MB")
            print("\nVisualize mesh:")
            print(f'  python -c "import open3d as o3d; mesh = o3d.io.read_triangle_mesh(\'{mesh_file}\'); o3d.visualization.draw_geometries([mesh])"')
    
    # Display point cloud output
    if recon_mode in ['pointcloud', 'both']:
        pointcloud_dir = os.path.join(dense_dir, config['output'].get('pointcloud_dir', 'pointclouds'))
        merged_pc = os.path.join(pointcloud_dir, 'merged_point_cloud.ply')
        if os.path.exists(merged_pc):
            print(f"\nPoint cloud output: {merged_pc}")
            print(f"Point cloud size: {os.path.getsize(merged_pc) / (1024**2):.1f} MB")
            print("\nVisualize point cloud:")
            print(f'  python -c "import open3d as o3d; pcd = o3d.io.read_point_cloud(\'{merged_pc}\'); o3d.visualization.draw_geometries([pcd])"')

    return 0


if __name__ == "__main__":
    sys.exit(main())
