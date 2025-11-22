#!/usr/bin/env python3
"""
Create TUM-format association file for ORB_SLAM3.

Association format:
timestamp1 rgb/filename.jpg timestamp2 depth/filename.png
"""

import os
import argparse
from pathlib import Path


def create_associations(dataset_dir, output_file):
    """Create association file from extracted RealSense frames."""
    color_dir = os.path.join(dataset_dir, 'color')
    depth_dir = os.path.join(dataset_dir, 'depth')

    # Get sorted lists of frames
    color_files = sorted([f for f in os.listdir(color_dir)
                         if f.endswith('.jpg') or f.endswith('.png')])
    depth_files = sorted([f for f in os.listdir(depth_dir)
                         if f.endswith('.png')])

    print(f"Found {len(color_files)} color frames")
    print(f"Found {len(depth_files)} depth frames")

    if len(color_files) != len(depth_files):
        print(f"WARNING: Mismatch in frame counts!")

    n_frames = min(len(color_files), len(depth_files))
    print(f"Creating associations for {n_frames} frames")

    with open(output_file, 'w') as f:
        for i in range(n_frames):
            # Use frame index as timestamp (ORB_SLAM3 only needs relative timing)
            timestamp = float(i) / 30.0  # Assuming 30 FPS

            # Write: timestamp rgb_path timestamp depth_path
            f.write(f"{timestamp:.6f} color/{color_files[i]} ")
            f.write(f"{timestamp:.6f} depth/{depth_files[i]}\n")

    print(f"\n✓ Association file created: {output_file}")
    print(f"  Frames: {n_frames}")
    print(f"  Duration: {n_frames/30.0:.2f} seconds (at 30 FPS)")


def main():
    parser = argparse.ArgumentParser(description="Create TUM association file")
    parser.add_argument('--dataset', type=str,
                       default='/home/chengzhe/Data/OMS_data3/rs_bags/1101/20251101_235516',
                       help='Dataset directory containing color/ and depth/ folders')
    parser.add_argument('--output', type=str,
                       default='/home/chengzhe/projects/slam_dense_reconstruction/output/associations.txt',
                       help='Output association file')

    args = parser.parse_args()

    print("="*80)
    print("Creating TUM Association File")
    print("="*80)
    print(f"\nDataset: {args.dataset}")
    print(f"Output: {args.output}")
    print()

    # Create output directory
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    create_associations(args.dataset, args.output)


if __name__ == "__main__":
    main()
