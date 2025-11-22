# Quick Start Guide - Multiple Bag Files

## Method 1: Using Configuration File (Recommended)

### 1. Edit the config file for your bag file

```bash
# Edit config/pipeline_config.yaml
# Change the bag_file path to your new bag file
```

Example config changes:
```yaml
dataset:
  bag_file: "/path/to/your/new_file.bag"
  frames_dir: "/path/to/your/new_file"
  intrinsic_file: "/path/to/your/new_file/intrinsic.json"
```

### 2. Run the complete pipeline

```bash
cd /home/chengzhe/projects/slam_dense_reconstruction

# If frames are NOT extracted yet:
./run_pipeline.py --config config/pipeline_config.yaml --extract

# If frames are already extracted:
./run_pipeline.py --config config/pipeline_config.yaml
```

## Method 2: Command Line Override (Quick)

Run pipeline with a different bag file without editing config:

```bash
./run_pipeline.py --bag /path/to/your/new_file.bag --extract
```

This will:
- Extract frames to `/path/to/your/new_file/` directory
- Run ORB_SLAM3
- Convert trajectory
- Generate dense mesh

## Method 3: Manual Step-by-Step

### Step 0: Extract frames from new bag file

```bash
./scripts/00_extract_frames.py \
    --bag /path/to/your/file.bag \
    --output /path/to/output/frames \
    --stride 1
```

### Step 1: Create associations

```bash
./scripts/create_associations.py \
    --dataset /path/to/output/frames \
    --output output/associations.txt
```

### Step 2: Run ORB_SLAM3

```bash
./scripts/01_run_orbslam3.sh /path/to/output/frames
```

### Step 3: Convert trajectory

```bash
./scripts/02_convert_trajectory.py
```

### Step 4: Dense reconstruction

```bash
./scripts/03_dense_reconstruction.py \
    --frames_dir /path/to/output/frames \
    --intrinsic /path/to/output/frames/intrinsic.json \
    --output output/dense/mesh.ply
```

## Resuming from a Specific Step

If a step fails, you can resume from that step:

```bash
# Resume from Step 2 (SLAM) onwards
./run_pipeline.py --start_step 2

# Resume from Step 4 (reconstruction) only
./run_pipeline.py --start_step 4
```

## Examples

### Example 1: Process a new bag file

```bash
./run_pipeline.py --bag /home/chengzhe/Data/OMS_data3/rs_bags/1102/20251102_120000.bag --extract
```

### Example 2: Rerun reconstruction with different voxel size

Edit `config/pipeline_config.yaml`:
```yaml
reconstruction:
  voxel_size: 0.005  # Changed from 0.01 to 0.005 for higher resolution
```

Then run:
```bash
./run_pipeline.py --start_step 4  # Skip SLAM, just rerun reconstruction
```

### Example 3: Extract every 3rd frame to speed up processing

Edit `config/pipeline_config.yaml`:
```yaml
extraction:
  frame_stride: 3  # Extract every 3rd frame
```

```bash
./run_pipeline.py --bag /path/to/file.bag --extract
```

## Output Structure

```
output/
├── associations.txt           # Frame associations
├── sparse/
│   ├── trajectory_tum.txt    # ORB_SLAM3 trajectory (TUM format)
│   ├── trajectory_open3d.log # Open3D trajectory (4x4 matrices)
│   └── trajectory_posegraph.json
└── dense/
    └── mesh.ply              # Final dense mesh
```

## Troubleshooting

### ORB_SLAM3 tracking failures
- Try reducing frame rate: set `frame_stride: 2` or `3` in config
- Increase ORB features in `config/RealSense_D456.yaml`: `ORBextractor.nFeatures: 3000`

### Out of memory during reconstruction
- Increase voxel size: `voxel_size: 0.02` or `0.05`
- Reduce depth range: `depth_max: 2.0`

### Frames already extracted
- Skip extraction: `./run_pipeline.py` (without --extract flag)
- Start from SLAM: `./run_pipeline.py --start_step 2`
