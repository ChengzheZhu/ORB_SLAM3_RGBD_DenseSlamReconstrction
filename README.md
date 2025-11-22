# ORB_SLAM3 + Open3D Dense Reconstruction Pipeline

A complete pipeline for RGB-D SLAM and dense 3D reconstruction from RealSense bag files.

## Features

- **Sparse SLAM**: ORB_SLAM3 for robust camera trajectory estimation
- **Dense Reconstruction**: Open3D TSDF-based mesh generation
- **Flexible Configuration**: YAML-based configuration system
- **Batch Processing**: Process multiple datasets with headless mode
- **Interactive Visualization**: Real-time SLAM tracking visualization

## Installation

### Clone with Submodules

This project uses ORB_SLAM3 as a git submodule. Clone with:

```bash
git clone --recursive <your-repo-url>
cd ORB_SLAM3_RGBD_DenseSlamReconstrction
```

Or if you already cloned without `--recursive`:

```bash
git submodule update --init --recursive
```

### Build

```bash
# 1. Install system dependencies
./install/install_dependencies.sh

# 2. Set up Python environment
conda create -n rs_open3d python=3.9
conda activate rs_open3d
pip install -r requirements.txt

# 3. Install Pangolin (for ORB_SLAM3 visualization)
./scripts/install_pangolin.sh

# 4. Build ORB_SLAM3
./scripts/build_orbslam3.sh

# 5. Download ORB vocabulary
cd external/orbslam3/Vocabulary
wget https://github.com/UZ-SLAMLab/ORB_SLAM3/releases/download/v1.0-release/ORBvoc.txt.tar.gz
tar -xf ORBvoc.txt.tar.gz
cd ../../..
```

## Quick Start

```bash
# Activate environment
conda activate rs_open3d

# Run complete pipeline (extract frames from bag, run SLAM, generate mesh)
./bin/run_pipeline.py --bag /path/to/your/file.bag --extract
```

## Documentation

- [Installation Guide](docs/SETUP.md) - Detailed setup instructions
- [Usage Guide](docs/USAGE.md) - How to use the pipeline
- [Quick Start](docs/QUICK_START.md) - Get started quickly
- [Viewer Toggle](docs/VIEWER_TOGGLE.md) - Interactive vs batch mode

## Directory Structure

```
ORB_SLAM3_RGBD_DenseSlamReconstrction/
├── bin/                  # Executable scripts
│   └── run_pipeline.py   # Master pipeline script
├── scripts/              # Pipeline scripts
│   ├── 00_extract_frames.py
│   ├── 01_run_orbslam3.sh
│   ├── 02_convert_trajectory.py
│   └── 03_dense_reconstruction.py
├── config/               # Configuration files
│   ├── camera/           # Camera configs (ORB_SLAM3)
│   └── pipeline/         # Pipeline configs (YAML)
├── external/             # External dependencies
│   └── orbslam3/         # ORB_SLAM3 (git submodule)
├── install/              # Installation scripts
├── docs/                 # Documentation
├── output/               # Output directory
│   ├── sparse/           # SLAM trajectories
│   └── dense/            # 3D meshes
└── tests/                # Unit tests
```

## Requirements

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8+
- RealSense D400 series camera (for data collection)
- 8GB+ RAM recommended
- GPU recommended (for Open3D visualization)

## How It Works

1. **Frame Extraction**: Extract RGB-D frames from RealSense bag files
2. **SLAM Tracking**: ORB_SLAM3 estimates camera trajectory from RGB-D frames
3. **Trajectory Conversion**: Convert ORB_SLAM3 output to Open3D format
4. **Dense Integration**: TSDF-based volumetric integration to create dense mesh

## Configuration

Edit `config/pipeline/default.yaml` to customize:

- Dataset paths
- Frame extraction settings (stride, max frames)
- ORB_SLAM3 parameters
- Dense reconstruction settings (voxel size, depth range)
- Viewer mode (interactive vs headless)

## License

See LICENSE file.
