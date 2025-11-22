# Setup Guide

This guide will help you set up the ORB_SLAM3 + Open3D dense reconstruction pipeline.

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8+
- Conda (recommended) or system Python
- Git

## Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd ORB_SLAM3_RGBD_DenseSlamReconstrction

# Initialize and update git submodules (IMPORTANT!)
git submodule update --init --recursive
```

**Important:** The ORB_SLAM3 library is included as a git submodule. You must run `git submodule update --init --recursive` to download it.

## Step 2: Install System Dependencies

```bash
# Install build tools
sudo apt-get update
sudo apt-get install -y build-essential cmake git

# Install required libraries
sudo apt-get install -y \
    libeigen3-dev \
    libssl-dev \
    libusb-1.0-0-dev \
    pkg-config \
    libgtk-3-dev \
    libglfw3-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev

# Install RealSense SDK
sudo apt-get install -y librealsense2-dev librealsense2-utils
```

Alternatively, use the automated installation script:

```bash
./install/install_dependencies.sh
```

## Step 3: Set Up Python Environment

### Option A: Using Conda (Recommended)

```bash
# Create conda environment
conda create -n rs_open3d python=3.9
conda activate rs_open3d

# Install Python dependencies
pip install -r requirements.txt
```

### Option B: Using System Python

```bash
pip install --user -r requirements.txt
```

## Step 4: Install Pangolin

Pangolin is required for ORB_SLAM3 visualization:

```bash
./scripts/install_pangolin.sh
```

## Step 5: Build ORB_SLAM3

```bash
# Make sure you're in the conda environment (if using conda)
conda activate rs_open3d

# Build ORB_SLAM3
./scripts/build_orbslam3.sh
```

This will:
1. Build ORB_SLAM3 third-party libraries (DBoW2, g2o, Sophus)
2. Build the ORB_SLAM3 core library
3. Build RGB-D examples

## Step 6: Download ORB Vocabulary

Download the ORB vocabulary file (required for ORB_SLAM3):

```bash
cd external/orbslam3/Vocabulary
wget https://github.com/UZ-SLAMLab/ORB_SLAM3/releases/download/v1.0-release/ORBvoc.txt.tar.gz
tar -xf ORBvoc.txt.tar.gz
rm ORBvoc.txt.tar.gz
cd ../../..
```

## Step 7: Verify Installation

Check that all components are properly installed:

```bash
# Check ORB_SLAM3 library
ls -lh external/orbslam3/lib/libORB_SLAM3.so

# Check ORB_SLAM3 executable
ls -lh external/orbslam3/Examples/RGB-D/rgbd_tum

# Check vocabulary file
ls -lh external/orbslam3/Vocabulary/ORBvoc.txt

# Test Python environment
python -c "import open3d; import numpy; import cv2; import pyrealsense2; print('All Python packages OK')"
```

## Troubleshooting

### Git Submodule Issues

If you cloned the repository without `--recursive` or the submodule is empty:

```bash
git submodule update --init --recursive
```

### ORB_SLAM3 Build Fails

1. Make sure you've activated the conda environment:
   ```bash
   conda activate rs_open3d
   ```

2. Check OpenCV installation:
   ```bash
   python -c "import cv2; print(cv2.__version__)"
   ```

3. Rebuild with verbose output:
   ```bash
   cd external/orbslam3
   rm -rf build
   mkdir build && cd build
   cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="-O3" -DBUILD_EXAMPLES=ON
   make -j$(nproc) VERBOSE=1
   ```

### Pangolin Issues

If Pangolin libraries are not found:

```bash
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

Add this to your `~/.bashrc` to make it permanent:

```bash
echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

## Next Steps

After successful installation, proceed to the [Usage Guide](USAGE.md) to learn how to run the pipeline.
