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
