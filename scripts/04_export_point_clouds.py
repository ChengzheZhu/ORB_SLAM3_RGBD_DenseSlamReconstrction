#!/usr/bin/env python3
"""
Export raw point clouds from RGB-D frames using ORB_SLAM3 trajectory.

This script generates point clouds directly from RGB-D frames without TSDF fusion.
Useful for visualization, analysis, or alternative processing pipelines.
"""

import open3d as o3d
import numpy as np
import json
import os
import sys
import argparse
from pathlib import Path


def load_trajectory(trajectory_file):
    """Load camera trajectory from Open3D log file."""
    print(f"Loading trajectory: {trajectory_file}")
    
    poses = []
    with open(trajectory_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if line.startswith('#') or not line:
                continue
            
            # Parse matrix (16 values in row-major order)
            try:
                values = [float(x) for x in line.split()]
                if len(values) == 16:
                    pose = np.array(values).reshape(4, 4)
                    poses.append(pose)
            except ValueError:
                continue
    
    print(f"✓ Loaded {len(poses)} poses")
    return poses


def load_intrinsics(intrinsic_file):
    """Load camera intrinsics from JSON file."""
    with open(intrinsic_file, 'r') as f:
        data = json.load(f)
    
    intrinsic = o3d.camera.PinholeCameraIntrinsic()
    intrinsic.set_intrinsics(
        width=data['width'],
        height=data['height'],
        fx=data['intrinsic_matrix'][0],
        fy=data['intrinsic_matrix'][4],
        cx=data['intrinsic_matrix'][6],
        cy=data['intrinsic_matrix'][7]
    )
    
    return intrinsic


def create_point_cloud_from_rgbd(color_file, depth_file, intrinsic, 
                                   depth_scale=1000.0, depth_max=3.0):
    """Create point cloud from single RGB-D frame."""
    # Read images
    color = o3d.io.read_image(color_file)
    depth = o3d.io.read_image(depth_file)
    
    # Create RGBD image
    rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color, depth,
        depth_scale=depth_scale,
        depth_trunc=depth_max,
        convert_rgb_to_intensity=False
    )
    
    # Create point cloud
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
        rgbd, intrinsic
    )
    
    return pcd


def export_point_clouds(frames_dir, intrinsic_file, trajectory_file, 
                       output_dir, depth_scale=1000.0, depth_max=3.0,
                       export_merged=True, export_individual=False,
                       downsample_voxel=0.0, frame_skip=1):
    """
    Export point clouds from RGB-D frames.
    
    Args:
        frames_dir: Directory containing color/ and depth/ subdirectories
        intrinsic_file: Camera intrinsics JSON file
        trajectory_file: Open3D trajectory log file
        output_dir: Output directory for point clouds
        depth_scale: Depth scale factor (1000.0 for mm to m)
        depth_max: Maximum depth in meters
        export_merged: Export merged point cloud
        export_individual: Export individual frame point clouds
        downsample_voxel: Voxel size for downsampling (0 = no downsampling)
        frame_skip: Process every Nth frame (1 = all frames)
    """
    
    print("="*80)
    print("Point Cloud Export")
    print("="*80)
    
    # Load trajectory
    poses = load_trajectory(trajectory_file)
    
    if len(poses) == 0:
        print("ERROR: No poses found in trajectory file!")
        return
    
    # Load intrinsics
    intrinsic = load_intrinsics(intrinsic_file)
    print(f"✓ Camera intrinsics loaded: {intrinsic.width}x{intrinsic.height}")
    
    # Get frame files
    color_dir = os.path.join(frames_dir, 'color')
    depth_dir = os.path.join(frames_dir, 'depth')
    
    color_files = sorted([f for f in os.listdir(color_dir) if f.endswith(('.png', '.jpg'))])
    depth_files = sorted([f for f in os.listdir(depth_dir) if f.endswith('.png')])
    
    n_frames = min(len(color_files), len(depth_files), len(poses))
    print(f"Processing {n_frames} frames (skip={frame_skip})")
    
    if n_frames == 0:
        print("ERROR: No frames to process!")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Process frames
    merged_pcd = o3d.geometry.PointCloud()
    
    for i in range(0, n_frames, frame_skip):
        if i % 100 == 0:
            print(f"Processing frame {i}/{n_frames}...")
        
        color_file = os.path.join(color_dir, color_files[i])
        depth_file = os.path.join(depth_dir, depth_files[i])
        
        # Create point cloud
        pcd = create_point_cloud_from_rgbd(
            color_file, depth_file, intrinsic,
            depth_scale, depth_max
        )
        
        # Transform to world coordinates
        pcd.transform(poses[i])
        
        # Downsample if requested
        if downsample_voxel > 0:
            pcd = pcd.voxel_down_sample(downsample_voxel)
        
        # Export individual frame
        if export_individual:
            frame_output = os.path.join(output_dir, 'frames', f'frame_{i:06d}.ply')
            os.makedirs(os.path.dirname(frame_output), exist_ok=True)
            o3d.io.write_point_cloud(frame_output, pcd)
        
        # Add to merged
        if export_merged:
            merged_pcd += pcd
    
    # Export merged point cloud
    if export_merged:
        merged_output = os.path.join(output_dir, 'merged_point_cloud.ply')
        
        print(f"\nMerged point cloud has {len(merged_pcd.points):,} points")
        
        # Optional: downsample merged cloud
        if downsample_voxel > 0:
            print(f"Downsampling merged cloud (voxel={downsample_voxel}m)...")
            merged_pcd = merged_pcd.voxel_down_sample(downsample_voxel)
            print(f"After downsampling: {len(merged_pcd.points):,} points")
        
        # Optional: remove statistical outliers
        if len(merged_pcd.points) > 100:  # Only if enough points
            print("Removing outliers...")
            merged_pcd, _ = merged_pcd.remove_statistical_outlier(
                nb_neighbors=20, std_ratio=2.0
            )
            print(f"After outlier removal: {len(merged_pcd.points):,} points")
        
        print(f"Saving merged point cloud: {merged_output}")
        o3d.io.write_point_cloud(merged_output, merged_pcd)
        
        # Get file size
        if os.path.exists(merged_output):
            file_size = os.path.getsize(merged_output) / (1024**2)
            
            print("\n" + "="*80)
            print("✓ Point Cloud Export Complete!")
            print("="*80)
            print(f"Output: {merged_output}")
            print(f"Points: {len(merged_pcd.points):,}")
            print(f"File size: {file_size:.1f} MB")
            
            if export_individual:
                print(f"Individual frames: {output_dir}/frames/")
        else:
            print("ERROR: Failed to save point cloud!")


def main():
    parser = argparse.ArgumentParser(
        description="Export point clouds from RGB-D frames"
    )
    parser.add_argument('--frames_dir', required=True,
                       help='Directory containing color/ and depth/ subdirectories')
    parser.add_argument('--intrinsic', required=True,
                       help='Camera intrinsics JSON file')
    parser.add_argument('--trajectory', required=True,
                       help='Open3D trajectory log file')
    parser.add_argument('--output_dir', required=True,
                       help='Output directory for point clouds')
    parser.add_argument('--depth_scale', type=float, default=1000.0,
                       help='Depth scale factor (default: 1000.0)')
    parser.add_argument('--depth_max', type=float, default=3.0,
                       help='Maximum depth in meters (default: 3.0)')
    parser.add_argument('--export_merged', action='store_true', default=True,
                       help='Export merged point cloud (default: True)')
    parser.add_argument('--export_individual', action='store_true',
                       help='Export individual frame point clouds')
    parser.add_argument('--downsample_voxel', type=float, default=0.01,
                       help='Voxel size for downsampling (0=no downsample, default: 0.01)')
    parser.add_argument('--frame_skip', type=int, default=1,
                       help='Process every Nth frame (default: 1)')
    
    args = parser.parse_args()
    
    export_point_clouds(
        frames_dir=args.frames_dir,
        intrinsic_file=args.intrinsic,
        trajectory_file=args.trajectory,
        output_dir=args.output_dir,
        depth_scale=args.depth_scale,
        depth_max=args.depth_max,
        export_merged=args.export_merged,
        export_individual=args.export_individual,
        downsample_voxel=args.downsample_voxel,
        frame_skip=args.frame_skip
    )


if __name__ == "__main__":
    main()
