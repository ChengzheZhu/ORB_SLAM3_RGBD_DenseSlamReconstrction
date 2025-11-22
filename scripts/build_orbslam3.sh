#!/bin/bash
set -e  # Exit on error

echo "================================================================================"
echo "ORB_SLAM3 Build Script"
echo "================================================================================"

ORB_SLAM3_DIR="/home/chengzhe/projects/ORB_SLAM3"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check dependencies
echo -e "${YELLOW}[1/5] Checking dependencies...${NC}"

# Check Eigen3
if pkg-config --exists eigen3; then
    echo -e "${GREEN}✓ Eigen3: $(pkg-config --modversion eigen3)${NC}"
else
    echo -e "${RED}✗ Eigen3 not found${NC}"
    echo "Install: sudo apt-get install libeigen3-dev"
    exit 1
fi

# Check RealSense
if pkg-config --exists realsense2; then
    echo -e "${GREEN}✓ RealSense2: $(pkg-config --modversion realsense2)${NC}"
else
    echo -e "${RED}✗ RealSense2 not found${NC}"
    exit 1
fi

# Check OpenCV (from conda env or system)
if /home/chengzhe/.conda/envs/rs_open3d/bin/python -c "import cv2" 2>/dev/null; then
    CV_VERSION=$(/home/chengzhe/.conda/envs/rs_open3d/bin/python -c "import cv2; print(cv2.__version__)")
    echo -e "${GREEN}✓ OpenCV: $CV_VERSION (conda env)${NC}"
    # Export OpenCV path for CMake
    export OpenCV_DIR="/home/chengzhe/.conda/envs/rs_open3d/lib/cmake/opencv4"
elif pkg-config --exists opencv4; then
    echo -e "${GREEN}✓ OpenCV: $(pkg-config --modversion opencv4)${NC}"
else
    echo -e "${YELLOW}⚠ OpenCV not found - ORB_SLAM3 may fail to build${NC}"
fi

# Check Pangolin
echo -e "${YELLOW}Checking Pangolin...${NC}"
if ldconfig -p | grep -q libpangolin; then
    echo -e "${GREEN}✓ Pangolin found${NC}"
else
    echo -e "${YELLOW}⚠ Pangolin not found - installing...${NC}"
    bash "$(dirname "$0")/install_pangolin.sh"
fi

# Build third-party libraries
echo ""
echo -e "${YELLOW}[2/5] Building ORB_SLAM3 third-party libraries...${NC}"
cd "$ORB_SLAM3_DIR"

# DBoW2
echo "Building DBoW2..."
cd Thirdparty/DBoW2
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
echo -e "${GREEN}✓ DBoW2 built${NC}"
cd ../../..

# g2o
echo "Building g2o..."
cd Thirdparty/g2o
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
echo -e "${GREEN}✓ g2o built${NC}"
cd ../../..

# Sophus (may have been built already)
if [ -d "Thirdparty/Sophus/build" ]; then
    echo -e "${GREEN}✓ Sophus already built${NC}"
else
    echo "Building Sophus..."
    cd Thirdparty/Sophus
    mkdir -p build && cd build
    cmake .. -DCMAKE_BUILD_TYPE=Release
    make -j$(nproc)
    echo -e "${GREEN}✓ Sophus built${NC}"
    cd ../../..
fi

# Build ORB_SLAM3
echo ""
echo -e "${YELLOW}[3/5] Building ORB_SLAM3 core library...${NC}"
cd "$ORB_SLAM3_DIR"
mkdir -p build && cd build

# Use system OpenCV or conda OpenCV
if [ -n "$OpenCV_DIR" ]; then
    echo "Using OpenCV from conda environment"
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_CXX_FLAGS="-O3" \
        -DBUILD_EXAMPLES=ON \
        -DOpenCV_DIR="$OpenCV_DIR"
else
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_CXX_FLAGS="-O3" \
        -DBUILD_EXAMPLES=ON
fi

make -j$(nproc)
echo -e "${GREEN}✓ ORB_SLAM3 core library built${NC}"

# Verify build
echo ""
echo -e "${YELLOW}[4/5] Verifying build...${NC}"

if [ -f "$ORB_SLAM3_DIR/lib/libORB_SLAM3.so" ]; then
    echo -e "${GREEN}✓ libORB_SLAM3.so created${NC}"
else
    echo -e "${RED}✗ libORB_SLAM3.so not found - build failed${NC}"
    exit 1
fi

if [ -f "$ORB_SLAM3_DIR/Examples/RGB-D/rgbd_realsense_D435i" ]; then
    echo -e "${GREEN}✓ rgbd_realsense_D435i executable created${NC}"
else
    echo -e "${RED}✗ rgbd_realsense_D435i not found - build failed${NC}"
    exit 1
fi

# Check vocabulary
echo ""
echo -e "${YELLOW}[5/5] Checking ORB vocabulary...${NC}"
if [ -f "$ORB_SLAM3_DIR/Vocabulary/ORBvoc.txt" ]; then
    echo -e "${GREEN}✓ ORB vocabulary found${NC}"
else
    echo -e "${YELLOW}⚠ ORB vocabulary (ORBvoc.txt) not found${NC}"
    echo "  Download from: https://github.com/UZ-SLAMLab/ORB_SLAM3/releases"
    echo "  Place in: $ORB_SLAM3_DIR/Vocabulary/"
fi

echo ""
echo -e "${GREEN}================================================================================${NC}"
echo -e "${GREEN}ORB_SLAM3 Build Complete!${NC}"
echo -e "${GREEN}================================================================================${NC}"
echo ""
echo "Library: $ORB_SLAM3_DIR/lib/libORB_SLAM3.so"
echo "RGB-D Executable: $ORB_SLAM3_DIR/Examples/RGB-D/rgbd_realsense_D435i"
echo ""
echo "Next steps:"
echo "1. Download ORB vocabulary if missing"
echo "2. Configure camera parameters for RealSense D456"
echo "3. Test with: cd $ORB_SLAM3_DIR && ./Examples/RGB-D/rgbd_realsense_D435i"
