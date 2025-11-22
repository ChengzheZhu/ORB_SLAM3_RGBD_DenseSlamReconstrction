# Building ORB_SLAM3

## Prerequisites Check

Before building, verify system dependencies:

```bash
# Check OpenCV
pkg-config --modversion opencv4 || pkg-config --modversion opencv

# Check Eigen3
pkg-config --modversion eigen3

# Check RealSense
pkg-config --modversion realsense2

# Check compiler
g++ --version  # Should support C++14
```

## Build Steps

### 1. Build ORB_SLAM3 Third-Party Libraries

```bash
cd /home/chengzhe/projects/ORB_SLAM3

# Build DBoW2
echo "Building DBoW2..."
cd Thirdparty/DBoW2
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
cd ../../..

# Build g2o
echo "Building g2o..."
cd Thirdparty/g2o
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
cd ../../..

# Build Sophus
echo "Building Sophus..."
cd Thirdparty/Sophus
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
cd ../../..
```

### 2. Build ORB_SLAM3 Core Library

```bash
cd /home/chengzhe/projects/ORB_SLAM3

# Create build directory
mkdir -p build && cd build

# Configure with CMake
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS="-O3" \
    -DBUILD_EXAMPLES=ON

# Build (this will take several minutes)
make -j$(nproc)

# Library will be created at: lib/libORB_SLAM3.so
```

### 3. Build RGB-D RealSense Example

```bash
cd /home/chengzhe/projects/ORB_SLAM3

# The RGB-D executable should be created at:
# Examples/RGB-D/rgbd_realsense_D435i
ls -lh Examples/RGB-D/rgbd_realsense_D435i
```

## Troubleshooting

### Missing Pangolin

If Pangolin is not installed:

```bash
# Install system dependencies
sudo apt-get install libglew-dev libpython2.7-dev

# Clone and build Pangolin
cd ~/Downloads
git clone https://github.com/stevenlovegrove/Pangolin.git
cd Pangolin
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
```

### OpenCV Version Mismatch

If you have multiple OpenCV versions:

```bash
# Specify OpenCV path in CMake
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DOpenCV_DIR=/usr/local/lib/cmake/opencv4
```

### RealSense SDK Issues

```bash
# Verify RealSense installation
rs-enumerate-devices

# If not found, install librealsense2
# (Already installed on your system based on previous work)
```

## Verification

After building, test ORB_SLAM3:

```bash
cd /home/chengzhe/projects/ORB_SLAM3

# Download vocabulary (if not already present)
# This is a large file (~90MB)
if [ ! -f "Vocabulary/ORBvoc.txt" ]; then
    echo "Vocabulary file missing - download from ORB_SLAM3 releases"
fi

# Test executable exists
ls -lh Examples/RGB-D/rgbd_realsense_D435i || echo "Build failed"
```

## Build Script

Use the automated build script:

```bash
# From slam_dense_reconstruction project
bash scripts/build_orbslam3.sh
```
