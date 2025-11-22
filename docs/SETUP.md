# ORB_SLAM3 + Open3D Dense Reconstruction Pipeline

## Overview

This project combines:
- **ORB_SLAM3** (CPU): Sparse SLAM for accurate global trajectory estimation
- **Open3D**: Dense TSDF reconstruction using SLAM trajectory

## Workflow

```
RealSense .bag file
    ↓
[ORB_SLAM3] → Sparse map + Camera trajectory (TUM format)
    ↓
[Trajectory Converter] → Open3D-compatible pose format
    ↓
[Open3D TSDF Integration] → Dense 3D mesh
```

## Environment Isolation Strategy

### Option 1: Conda Environment (Recommended for Python integration)
```bash
# Create isolated environment
conda create -n slam_dense python=3.10 -y
conda activate slam_dense

# Install Open3D and Python dependencies
pip install open3d numpy opencv-python

# ORB_SLAM3 will be built separately with system dependencies
```

### Option 2: System-level Build (Best for ORB_SLAM3 performance)
```bash
# ORB_SLAM3 built with system libraries
# Python scripts use existing rs_open3d environment
```

## Dependencies

### ORB_SLAM3 Requirements
- **OpenCV** (3.2 or higher)
- **Eigen3** (3.1.0 or higher)
- **Pangolin** (for visualization)
- **RealSense SDK** (librealsense2)
- **C++ compiler** (C++14 support)

### Open3D Requirements
- **Python 3.7+**
- **Open3D** (already installed in rs_open3d)
- **NumPy**

## Build Status

- [ ] ORB_SLAM3 third-party libraries (DBoW2, g2o, Sophus)
- [ ] ORB_SLAM3 core library
- [ ] ORB_SLAM3 RGB-D examples
- [ ] Integration scripts

## Directory Structure

```
slam_dense_reconstruction/
├── scripts/
│   ├── 01_run_orbslam3.sh          # Run ORB_SLAM3 on .bag file
│   ├── 02_convert_trajectory.py     # Convert TUM trajectory to Open3D format
│   ├── 03_dense_reconstruction.py   # Open3D TSDF integration
│   └── run_full_pipeline.sh         # Complete workflow
├── config/
│   ├── orbslam3_realsense.yaml     # ORB_SLAM3 camera config
│   └── open3d_integration.yml      # Open3D TSDF parameters
├── output/
│   ├── sparse/                      # ORB_SLAM3 outputs (trajectory, map)
│   └── dense/                       # Open3D outputs (mesh, point cloud)
└── docs/
    ├── SETUP.md                     # This file
    └── BUILD_ORBSLAM3.md           # Build instructions
```

## Next Steps

1. Build ORB_SLAM3 (see BUILD_ORBSLAM3.md)
2. Configure camera parameters for RealSense D456
3. Create integration scripts
4. Test on sample data
