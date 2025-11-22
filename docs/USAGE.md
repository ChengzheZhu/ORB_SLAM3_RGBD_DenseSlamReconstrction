# ORB_SLAM3 + Open3D Dense Reconstruction Pipeline

## Quick Start

Run the complete pipeline with three sequential steps:

### Step 1: Run ORB_SLAM3 on RealSense Bag File

```bash
cd /home/chengzhe/projects/slam_dense_reconstruction
./scripts/01_run_orbslam3.sh
```

This will:
- Run ORB_SLAM3 RGB-D SLAM on the bag file
- Display real-time visualization with map points and camera trajectory
- Export camera trajectory to `output/sparse/trajectory_tum.txt`
- Export keyframe trajectory to `output/sparse/keyframe_trajectory_tum.txt`

**Note**: The ORB_SLAM3 viewer window will show the reconstruction progress. Close it when SLAM is complete.

### Step 2: Convert Trajectory to Open3D Format

```bash
./scripts/02_convert_trajectory.py
```

This will:
- Load TUM format trajectory from ORB_SLAM3
- Convert quaternions to rotation matrices
- Output two formats:
  - `output/sparse/trajectory_open3d.log` - Simple log format (16 values per line)
  - `output/sparse/trajectory_posegraph.json` - Open3D PoseGraph format

### Step 3: Dense TSDF Reconstruction

```bash
./scripts/03_dense_reconstruction.py
```

This will:
- Load camera trajectory from Step 2
- Load camera intrinsics from dataset
- Integrate all RGB-D frames into TSDF volume using SLAM poses
- Extract triangle mesh
- Save final mesh to `output/dense/mesh.ply`

## Default Paths

The scripts use these default paths (can be changed with command-line arguments):

- **Input bag**: `/home/chengzhe/Data/OMS_data3/rs_bags/1101/20251101_235516.bag`
- **Frames directory**: `/home/chengzhe/Data/OMS_data3/rs_bags/1101/20251101_235516/`
- **Camera intrinsics**: `/home/chengzhe/Data/OMS_data3/rs_bags/1101/20251101_235516/intrinsic.json`
- **Output directory**: `./output/`

## Customization

### Step 1 - Custom bag file:
```bash
./scripts/01_run_orbslam3.sh /path/to/your/file.bag
```

### Step 2 - Custom trajectory:
```bash
./scripts/02_convert_trajectory.py --input /path/to/trajectory_tum.txt
```

### Step 3 - Custom parameters:
```bash
./scripts/03_dense_reconstruction.py \
    --frames_dir /path/to/frames \
    --intrinsic /path/to/intrinsic.json \
    --trajectory output/sparse/trajectory_open3d.log \
    --output output/dense/mesh.ply \
    --voxel_size 0.01 \
    --depth_max 3.0
```

## Parameters

### Dense Reconstruction Parameters

- `--voxel_size` (default: 0.01): TSDF voxel size in meters
  - Smaller = higher resolution but more memory
  - Recommended: 0.005-0.02m

- `--depth_max` (default: 3.0): Maximum depth in meters
  - Frames beyond this depth are truncated
  - Recommended: 2.0-4.0m for indoor scenes

## Visualization

View the final mesh:
```bash
python -c "import open3d as o3d; mesh = o3d.io.read_triangle_mesh('output/dense/mesh.ply'); o3d.visualization.draw_geometries([mesh])"
```

## Troubleshooting

### ORB_SLAM3 fails to initialize
- Ensure camera config matches your RealSense calibration
- Check that bag file contains RGB-D streams
- Verify ORB vocabulary file exists

### Dense reconstruction is empty
- Check that trajectory file has poses
- Verify frame directory has color/ and depth/ subdirectories
- Ensure intrinsic.json matches camera calibration

### Out of memory during integration
- Increase `--voxel_size` (e.g., 0.02 or 0.05)
- Reduce `--depth_max` to integrate less volume
- Process fewer frames by modifying script

## Pipeline Architecture

```
RealSense .bag file
        ↓
[Step 1] ORB_SLAM3 RGB-D SLAM
        ↓
TUM Trajectory (timestamp tx ty tz qx qy qz qw)
        ↓
[Step 2] Convert to Open3D format
        ↓
Open3D Trajectory (4x4 matrices)
        ↓
[Step 3] TSDF Integration with SLAM poses
        ↓
Dense Triangle Mesh (.ply)
```

## Advantages Over Fragment-Based Pipeline

- **Better global consistency**: ORB_SLAM3 provides globally optimized trajectory with loop closure
- **Simpler workflow**: No fragment management, single trajectory for all frames
- **CPU-based SLAM**: Can run on machines without CUDA
- **Robust to drift**: Loop closure and relocalization prevent accumulated error
- **Faster overall**: Skip fragment generation and registration steps
