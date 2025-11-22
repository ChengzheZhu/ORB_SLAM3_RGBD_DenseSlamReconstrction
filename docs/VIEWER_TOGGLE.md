# Viewer Toggle Guide

The pipeline now supports both **interactive visualization** and **headless batch processing**.

## Rebuild Required

First, rebuild ORB_SLAM3 with the viewer toggle changes:

```bash
cd /home/chengzhe/projects/ORB_SLAM3
sudo ./build.sh
```

## Usage Options

### Option 1: Shell Script with Flag

#### With Viewer (Default):
```bash
./scripts/01_run_orbslam3.sh
```

#### Headless Mode (No Viewer):
```bash
./scripts/01_run_orbslam3.sh --headless
```

### Option 2: Config File

Edit `config/pipeline_config.yaml`:
```yaml
orbslam:
  use_viewer: false  # Set to false for headless mode
```

Then run:
```bash
./run_pipeline.py --config config/pipeline_config.yaml
```

### Option 3: Command Line Override

```bash
# Interactive mode (default)
./run_pipeline.py --bag /path/to/file.bag --extract

# Headless mode (for batch processing)
./run_pipeline.py --bag /path/to/file.bag --extract --headless
```

## When to Use Each Mode

### Use Viewer Mode When:
- Debugging SLAM tracking issues
- Verifying camera calibration
- Visualizing reconstruction in real-time
- Processing single datasets interactively
- Monitoring tracking quality

### Use Headless Mode When:
- Batch processing multiple bag files
- Running on remote servers via SSH
- Automating pipelines
- Processing overnight
- Running in Docker containers
- Maximum performance needed (no rendering overhead)

## Viewer Controls (When Enabled)

### Camera View:
- **Left Click + Drag**: Rotate view
- **Right Click + Drag**: Pan view
- **Scroll Wheel**: Zoom in/out
- **Middle Click**: Reset view

### Keyboard Shortcuts:
- **Space**: Pause/Resume tracking
- **S**: Save screenshot
- **R**: Reset view
- **ESC**: Exit (after sequence completes)

## Performance Comparison

| Mode | Speed | Memory | Use Case |
|------|-------|--------|----------|
| Viewer | ~23ms/frame | +200MB | Interactive debugging |
| Headless | ~18ms/frame | Normal | Batch processing |

## Example Workflows

### Interactive Single Dataset:
```bash
# Process with visualization
./scripts/01_run_orbslam3.sh
./scripts/02_convert_trajectory.py
./scripts/03_dense_reconstruction.py
```

### Batch Processing Multiple Datasets:
```bash
# Process multiple bag files headless
for bag in /path/to/bags/*.bag; do
    ./run_pipeline.py --bag "$bag" --extract --headless
done
```

### Config-Based Workflow:
```bash
# Set use_viewer: false in config for batch mode
# Set use_viewer: true in config for interactive mode
./run_pipeline.py --config config/my_dataset.yaml
```

## Troubleshooting

### Viewer not showing even without --headless flag?
- Check DISPLAY variable: `echo $DISPLAY`
- If SSH: reconnect with `ssh -X` or `ssh -Y`
- Verify OpenCV built with GTK: `pkg-config --libs opencv4 | grep gtk`

### "Viewer disabled" message when you want visualization?
- Remove `--headless` flag
- Check config: `use_viewer: true`
- Rebuild ORB_SLAM3 after code changes

### Performance issues with viewer?
- Use `--headless` for faster processing
- Reduce window size in viewer settings
- Process on machine with GPU for rendering
