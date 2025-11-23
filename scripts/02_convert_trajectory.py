#!/usr/bin/env python3
"""
Convert ORB_SLAM3 trajectory (TUM format) to Open3D-compatible format.

TUM format: timestamp tx ty tz qx qy qz qw
Open3D format: 4x4 transformation matrix per frame
"""

import numpy as np
import json
import argparse
from pathlib import Path


def quaternion_to_rotation_matrix(qx, qy, qz, qw):
    """Convert quaternion to 3x3 rotation matrix."""
    # Normalize quaternion
    norm = np.sqrt(qx*qx + qy*qy + qz*qz + qw*qw)
    qx, qy, qz, qw = qx/norm, qy/norm, qz/norm, qw/norm

    # Convert to rotation matrix
    R = np.array([
        [1 - 2*(qy*qy + qz*qz),     2*(qx*qy - qw*qz),     2*(qx*qz + qw*qy)],
        [    2*(qx*qy + qw*qz), 1 - 2*(qx*qx + qz*qz),     2*(qy*qz - qw*qx)],
        [    2*(qx*qz - qw*qy),     2*(qy*qz + qw*qx), 1 - 2*(qx*qx + qy*qy)]
    ])
    return R


def tum_to_matrix(tx, ty, tz, qx, qy, qz, qw):
    """Convert TUM pose to 4x4 transformation matrix."""
    R = quaternion_to_rotation_matrix(qx, qy, qz, qw)

    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = [tx, ty, tz]

    return T


def load_tum_trajectory(tum_file):
    """
    Load ORB_SLAM3 trajectory in TUM format.

    Returns:
        List of (timestamp, 4x4 matrix) tuples
    """
    poses = []

    with open(tum_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            if len(parts) < 8:
                continue

            timestamp = float(parts[0])
            tx, ty, tz = float(parts[1]), float(parts[2]), float(parts[3])
            qx, qy, qz, qw = float(parts[4]), float(parts[5]), float(parts[6]), float(parts[7])

            T = tum_to_matrix(tx, ty, tz, qx, qy, qz, qw)
            poses.append((timestamp, T))

    return poses


def save_open3d_trajectory(poses, output_file):
    """
    Save trajectory in Open3D log format.

    Format: One 4x4 matrix per frame, space-separated
    """
    with open(output_file, 'w') as f:
        f.write(f"# Open3D trajectory log\n")
        f.write(f"# Number of poses: {len(poses)}\n")
        f.write(f"# Format: 4x4 transformation matrix (row-major)\n")
        f.write(f"#\n")

        for timestamp, T in poses:
            # Write as single line: 16 values (4x4 matrix, row-major)
            values = T.flatten()
            f.write(' '.join(f'{v:.12f}' for v in values))
            f.write('\n')


def save_pose_graph_json(poses, output_file):
    """Save trajectory as pose graph JSON for Open3D."""
    pose_graph = {
        "class_name": "PoseGraph",
        "version_major": 1,
        "version_minor": 0,
        "nodes": [],
        "edges": []
    }

    # Add nodes (camera poses)
    for i, (timestamp, T) in enumerate(poses):
        node = {
            "class_name": "PoseGraphNode",
            "version_major": 1,
            "version_minor": 0,
            "pose": T.tolist()
        }
        pose_graph["nodes"].append(node)

    # Add edges (odometry between consecutive frames)
    for i in range(len(poses) - 1):
        T_curr = poses[i][1]
        T_next = poses[i+1][1]

        # Relative transformation
        T_rel = np.linalg.inv(T_curr) @ T_next

        edge = {
            "class_name": "PoseGraphEdge",
            "version_major": 1,
            "version_minor": 0,
            "source_node_id": i,
            "target_node_id": i + 1,
            "transformation": T_rel.tolist(),
            "information": np.eye(6).tolist(),
            "uncertain": False
        }
        pose_graph["edges"].append(edge)

    with open(output_file, 'w') as f:
        json.dump(pose_graph, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Convert ORB_SLAM3 trajectory to Open3D format")
    parser.add_argument('--input', type=str,
                       
                       help='Input TUM trajectory file from ORB_SLAM3')
    parser.add_argument('--output_log', type=str,
                       
                       help='Output Open3D trajectory log')
    parser.add_argument('--output_json', type=str,
                       
                       help='Output pose graph JSON')

    args = parser.parse_args()

    print("="*80)
    print("ORB_SLAM3 Trajectory Converter")
    print("="*80)

    # Load TUM trajectory
    print(f"\nLoading TUM trajectory: {args.input}")
    poses = load_tum_trajectory(args.input)
    print(f"✓ Loaded {len(poses)} poses")

    if len(poses) == 0:
        print("ERROR: No poses found in trajectory file!")
        return

    # Print statistics
    timestamps = [t for t, _ in poses]
    duration = timestamps[-1] - timestamps[0]
    avg_fps = len(poses) / duration if duration > 0 else 0

    print(f"\nTrajectory Statistics:")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"  Average FPS: {avg_fps:.2f}")
    print(f"  First timestamp: {timestamps[0]:.6f}")
    print(f"  Last timestamp: {timestamps[-1]:.6f}")

    # Save Open3D log format
    print(f"\nSaving Open3D trajectory log: {args.output_log}")
    save_open3d_trajectory(poses, args.output_log)
    print(f"✓ Saved trajectory log")

    # Save pose graph JSON
    print(f"\nSaving pose graph JSON: {args.output_json}")
    save_pose_graph_json(poses, args.output_json)
    print(f"✓ Saved pose graph")

    print("\n" + "="*80)
    print("Conversion Complete!")
    print("="*80)
    print(f"\nNext step: Run dense reconstruction")
    print(f"  python scripts/03_dense_reconstruction.py")


if __name__ == "__main__":
    main()
