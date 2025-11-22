#!/bin/bash
# Build ORB_SLAM3 with required configurations

set -e

ORBSLAM3_DIR="${ORBSLAM3_DIR:-/home/chengzhe/projects/ORB_SLAM3}"

if [ ! -d "$ORBSLAM3_DIR" ]; then
    echo "ORB_SLAM3 not found at: $ORBSLAM3_DIR"
    echo "Clone it first:"
    echo "  git clone https://github.com/UZ-SLAMLab/ORB_SLAM3.git $ORBSLAM3_DIR"
    exit 1
fi

echo "Building ORB_SLAM3 at: $ORBSLAM3_DIR"
cd "$ORBSLAM3_DIR"

# Build
sudo ./build.sh

echo "✓ ORB_SLAM3 built successfully!"
