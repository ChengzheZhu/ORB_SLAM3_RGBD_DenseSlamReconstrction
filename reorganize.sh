#!/bin/bash
# Reorganize project structure for standalone deployment

set -e

PROJECT_ROOT="/home/chengzhe/projects/slam_dense_reconstruction"
cd "$PROJECT_ROOT"

echo "Reorganizing slam_dense_reconstruction project..."
echo "Creating new directory structure..."

# Create new directories
mkdir -p bin
mkdir -p src/slam_reconstruction
mkdir -p config/{camera,pipeline/examples,orbslam}
mkdir -p install
mkdir -p external/orbslam3
mkdir -p tests
mkdir -p data

# Move existing files to new locations

echo "Moving configuration files..."
# Move camera configs
if [ -f "config/RealSense_D456.yaml" ]; then
    mv config/RealSense_D456.yaml config/camera/
fi

# Move pipeline configs
if [ -f "config/pipeline_config.yaml" ]; then
    mv config/pipeline_config.yaml config/pipeline/default.yaml
fi

# Move example configs
if [ -d "config/example_configs" ]; then
    mv config/example_configs/* config/pipeline/examples/ 2>/dev/null || true
    rmdir config/example_configs 2>/dev/null || true
fi

echo "Moving executables..."
# Move main pipeline script
if [ -f "run_pipeline.py" ]; then
    mv run_pipeline.py bin/
fi

echo "Moving documentation..."
# Move docs
if [ -f "USAGE.md" ]; then
    mv USAGE.md docs/
fi
if [ -f "QUICK_START.md" ]; then
    mv QUICK_START.md docs/
fi
if [ -f "VIEWER_TOGGLE.md" ]; then
    mv VIEWER_TOGGLE.md docs/
fi

echo "Creating Python package structure..."
# Create src package
cat > src/slam_reconstruction/__init__.py << 'EOF'
"""
ORB_SLAM3 + Open3D Dense Reconstruction Pipeline

A complete pipeline for RGB-D SLAM and dense 3D reconstruction using
ORB_SLAM3 for sparse SLAM and Open3D for TSDF-based dense reconstruction.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .frame_extraction import extract_frames_from_bag
from .trajectory_converter import convert_trajectory
from .dense_reconstruction import dense_tsdf_reconstruction

__all__ = [
    'extract_frames_from_bag',
    'convert_trajectory',
    'dense_tsdf_reconstruction',
]
EOF

# Create external dependencies README
cat > external/README.md << 'EOF'
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
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Python dependencies for slam_dense_reconstruction

# Core dependencies
open3d>=0.17.0
numpy>=1.21.0
opencv-python>=4.5.0
pyrealsense2>=2.50.0
pyyaml>=6.0

# Optional dependencies
matplotlib>=3.5.0  # For visualization
tqdm>=4.60.0       # Progress bars
pytest>=7.0.0      # Testing
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Output directories
output/
*.ply
*.pcd

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Data
data/*
!data/.gitkeep

# Temporary files
*.log
*.tmp
.cache/
EOF

# Create data placeholder
touch data/.gitkeep

# Create README.md
cat > README.md << 'EOF'
# ORB_SLAM3 + Open3D Dense Reconstruction Pipeline

A complete pipeline for RGB-D SLAM and dense 3D reconstruction from RealSense bag files.

## Features

- **Sparse SLAM**: ORB_SLAM3 for robust camera trajectory estimation
- **Dense Reconstruction**: Open3D TSDF-based mesh generation
- **Flexible Configuration**: YAML-based configuration system
- **Batch Processing**: Process multiple datasets with headless mode
- **Interactive Visualization**: Real-time SLAM tracking visualization

## Quick Start

```bash
# 1. Install dependencies
./install/install_dependencies.sh

# 2. Build ORB_SLAM3
./install/build_orbslam3.sh

# 3. Run pipeline
./bin/run_pipeline.py --bag /path/to/your/file.bag --extract
```

## Documentation

- [Installation Guide](docs/SETUP.md)
- [Usage Guide](docs/USAGE.md)
- [Quick Start](docs/QUICK_START.md)
- [Viewer Toggle](docs/VIEWER_TOGGLE.md)

## Directory Structure

```
slam_dense_reconstruction/
├── bin/                  # Executable scripts
├── src/                  # Source code modules
├── config/               # Configuration files
├── scripts/              # Utility scripts
├── install/              # Installation scripts
├── external/             # External dependencies info
├── docs/                 # Documentation
├── output/               # Output directory
└── tests/                # Unit tests
```

## Requirements

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8+
- RealSense D400 series camera (for data collection)
- 8GB+ RAM recommended
- GPU recommended (for Open3D visualization)

## License

See LICENSE file.
EOF

echo "Creating installation scripts..."
# Create install script
cat > install/install_dependencies.sh << 'EOF'
#!/bin/bash
# Install all dependencies for slam_dense_reconstruction

set -e

echo "Installing system dependencies..."

# Update package list
sudo apt-get update

# Install build essentials
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    pkg-config

# Install Eigen3
sudo apt-get install -y libeigen3-dev

# Install RealSense
sudo apt-get install -y \
    librealsense2-dev \
    librealsense2-utils

# Install GTK for OpenCV
sudo apt-get install -y \
    libgtk2.0-dev \
    libgtk-3-dev

# Install Pangolin dependencies
sudo apt-get install -y \
    libglew-dev \
    libboost-dev \
    libboost-thread-dev \
    libboost-filesystem-dev \
    ffmpeg \
    libavcodec-dev \
    libavutil-dev \
    libavformat-dev \
    libswscale-dev \
    libdc1394-dev \
    libraw1394-dev

# Install Python dependencies
echo "Installing Python packages..."
pip install -r ../requirements.txt

echo "✓ All dependencies installed successfully!"
echo "Next: Run ./build_orbslam3.sh to build ORB_SLAM3"
EOF

chmod +x install/install_dependencies.sh

# Create ORB_SLAM3 build reference
cat > install/build_orbslam3.sh << 'EOF'
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
EOF

chmod +x install/build_orbslam3.sh

echo ""
echo "✓ Reorganization complete!"
echo ""
echo "New structure created. Key changes:"
echo "  - Executables moved to bin/"
echo "  - Configs organized in config/{camera,pipeline,orbslam}/"
echo "  - Documentation moved to docs/"
echo "  - Created src/ for Python modules"
echo "  - Created install/ for setup scripts"
echo "  - Created external/ for dependency info"
echo "  - Created requirements.txt and .gitignore"
echo ""
echo "The 'scripts/' directory is kept for backward compatibility."
echo ""
echo "To use the reorganized structure:"
echo "  ./bin/run_pipeline.py --config config/pipeline/default.yaml"
echo ""
