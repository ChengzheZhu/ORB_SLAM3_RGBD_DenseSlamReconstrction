#!/bin/bash
set -e

# ORB_SLAM3 RGB-D Pipeline for RealSense .bag files
# This script runs ORB_SLAM3 on a RealSense bag file and exports trajectory

# Configuration
ORB_SLAM3_DIR="/home/chengzhe/projects/ORB_SLAM3"
PROJECT_DIR="/home/chengzhe/projects/slam_dense_reconstruction"
VOCAB_FILE="$ORB_SLAM3_DIR/Vocabulary/ORBvoc.txt"
CONFIG_FILE="$PROJECT_DIR/config/camera/RealSense_D456.yaml"

# Parse arguments
HEADLESS_MODE=""
DATASET_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --headless)
            HEADLESS_MODE="no_viewer"
            shift
            ;;
        *)
            DATASET_DIR="$1"
            shift
            ;;
    esac
done

# Set default dataset if not provided
DATASET_DIR="${DATASET_DIR:-/home/chengzhe/Data/OMS_data3/rs_bags/1101/20251101_235516}"

# Input/Output
ASSOCIATIONS_FILE="$PROJECT_DIR/output/associations.txt"
OUTPUT_DIR="$PROJECT_DIR/output/sparse"
TRAJECTORY_FILE="$OUTPUT_DIR/trajectory_tum.txt"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "================================================================================"
echo "ORB_SLAM3 RGB-D SLAM Pipeline"
echo "================================================================================"

# Validate inputs
if [ ! -f "$VOCAB_FILE" ]; then
    echo "ERROR: ORB vocabulary not found: $VOCAB_FILE"
    echo "Download from: https://github.com/UZ-SLAMLab/ORB_SLAM3/releases"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Camera config not found: $CONFIG_FILE"
    exit 1
fi

if [ ! -d "$DATASET_DIR" ]; then
    echo "ERROR: Dataset directory not found: $DATASET_DIR"
    echo "Usage: $0 <path_to_dataset_directory>"
    exit 1
fi

if [ ! -f "$ASSOCIATIONS_FILE" ]; then
    echo "ERROR: Association file not found: $ASSOCIATIONS_FILE"
    echo "Create it first by running: ./scripts/create_associations.py"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "  Vocabulary: $VOCAB_FILE"
echo "  Camera Config: $CONFIG_FILE"
echo "  Dataset: $DATASET_DIR"
echo "  Associations: $ASSOCIATIONS_FILE"
echo "  Output Dir: $OUTPUT_DIR"
echo ""

# Run ORB_SLAM3
echo -e "${YELLOW}Running ORB_SLAM3...${NC}"
cd "$ORB_SLAM3_DIR"

# Set library path for Pangolin
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Run with trajectory export
# Usage: ./rgbd_tum vocabulary settings sequence_path associations_file [no_viewer]
if [ -n "$HEADLESS_MODE" ]; then
    echo "Running in headless mode (no visualization)"
    ./Examples/RGB-D/rgbd_tum \
        "$VOCAB_FILE" \
        "$CONFIG_FILE" \
        "$DATASET_DIR" \
        "$ASSOCIATIONS_FILE" \
        "$HEADLESS_MODE"
else
    echo "Running with visualization enabled"
    ./Examples/RGB-D/rgbd_tum \
        "$VOCAB_FILE" \
        "$CONFIG_FILE" \
        "$DATASET_DIR" \
        "$ASSOCIATIONS_FILE"
fi

echo ""
echo -e "${GREEN}ORB_SLAM3 Complete!${NC}"

# Move trajectory to output directory
if [ -f "CameraTrajectory.txt" ]; then
    mv CameraTrajectory.txt "$TRAJECTORY_FILE"
    echo -e "${GREEN}✓ Trajectory saved: $TRAJECTORY_FILE${NC}"
fi

if [ -f "KeyFrameTrajectory.txt" ]; then
    mv KeyFrameTrajectory.txt "$OUTPUT_DIR/keyframe_trajectory_tum.txt"
    echo -e "${GREEN}✓ Keyframe trajectory saved${NC}"
fi

# Count trajectory poses
if [ -f "$TRAJECTORY_FILE" ]; then
    POSE_COUNT=$(wc -l < "$TRAJECTORY_FILE")
    echo ""
    echo "Trajectory poses: $POSE_COUNT"
    echo "Next step: Convert trajectory to Open3D format"
    echo "  Run: python scripts/02_convert_trajectory.py"
fi
