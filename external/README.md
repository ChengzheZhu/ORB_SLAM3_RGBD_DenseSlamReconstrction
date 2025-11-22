# External Dependencies

This project requires the following external dependencies:

## Required

### 1. ORB_SLAM3
- **Version**: Latest (tested with commit fb7088c)
- **Location**: `/home/chengzhe/projects/ORB_SLAM3` (configurable)
- **Purpose**: Sparse visual SLAM for camera trajectory estimation
- **Build**: See `install/build_orbslam3.sh`

### 2. Open3D
- **Version**: >= 0.17.0
- **Install**: `pip install open3d`
- **Purpose**: Dense TSDF reconstruction and mesh generation

### 3. Intel RealSense SDK
- **Version**: >= 2.50.0
- **Install**: `sudo apt install librealsense2-dev`
- **Purpose**: Reading RealSense .bag files and extracting frames

### 4. OpenCV
- **Version**: >= 4.5.0 with GTK support
- **Install**: See `install/install_dependencies.sh`
- **Purpose**: Image processing and visualization

### 5. Eigen3
- **Version**: >= 3.3.0
- **Install**: `sudo apt install libeigen3-dev`
- **Purpose**: Linear algebra for ORB_SLAM3

### 6. Pangolin
- **Version**: >= 0.6
- **Install**: See `install/install_dependencies.sh`
- **Purpose**: Visualization for ORB_SLAM3

## Optional

### Python Dependencies
See `requirements.txt` for Python package versions.

## Dependency Graph

```
slam_dense_reconstruction
├── ORB_SLAM3 (C++)
│   ├── OpenCV (with GTK)
│   ├── Eigen3
│   ├── Pangolin
│   └── DBoW2, g2o (bundled)
├── Open3D (Python)
├── pyrealsense2 (Python)
└── NumPy, PyYAML (Python)
```

## Installation Order

1. System dependencies (Eigen3, GTK, etc.)
2. OpenCV with GTK support
3. Pangolin
4. ORB_SLAM3
5. Python packages

Run `install/install_dependencies.sh` for automated installation.
