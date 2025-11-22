# Project Reorganization Plan

## New Structure:
```
slam_dense_reconstruction/
├── bin/                          # Main executables
│   └── run_pipeline.py          # Master pipeline script
├── src/                          # Source code modules
│   ├── __init__.py
│   ├── frame_extraction.py      # Frame extraction from bag files
│   ├── trajectory_converter.py  # TUM to Open3D conversion
│   ├── dense_reconstruction.py  # TSDF reconstruction
│   └── utils.py                 # Common utilities
├── config/                       # Configuration files
│   ├── camera/                  # Camera calibrations
│   │   └── RealSense_D456.yaml
│   ├── pipeline/                # Pipeline configs
│   │   ├── default.yaml
│   │   └── examples/
│   └── orbslam/                 # ORB_SLAM3 configs
├── scripts/                      # Utility scripts (backward compatible)
│   ├── 00_extract_frames.py
│   ├── 01_run_orbslam3.sh
│   ├── 02_convert_trajectory.py
│   ├── 03_dense_reconstruction.py
│   └── create_associations.py
├── install/                      # Installation scripts
│   ├── install_dependencies.sh
│   ├── build_orbslam3.sh
│   └── setup_environment.sh
├── external/                     # External dependencies management
│   ├── README.md                # Dependency list and versions
│   └── orbslam3/               # ORB_SLAM3 integration
│       ├── build.sh
│       └── config.yaml
├── docs/                         # Documentation
│   ├── README.md
│   ├── SETUP.md
│   ├── USAGE.md
│   ├── QUICK_START.md
│   ├── VIEWER_TOGGLE.md
│   └── API.md
├── data/                         # Sample/test data (optional)
│   └── sample_bag/
├── output/                       # Output directory (gitignored)
│   ├── sparse/
│   └── dense/
├── tests/                        # Unit tests
│   └── test_pipeline.py
├── README.md                     # Main readme
├── requirements.txt              # Python dependencies
├── setup.py                      # Python package setup
├── .gitignore
└── LICENSE
```
