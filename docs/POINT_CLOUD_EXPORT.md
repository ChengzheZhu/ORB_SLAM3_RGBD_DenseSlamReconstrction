# Point Cloud Export Feature

This pipeline now supports exporting raw point clouds in addition to (or instead of) TSDF mesh reconstruction.

## Overview

The point cloud export feature allows you to:
- Export merged point clouds from all frames
- Export individual per-frame point clouds
- Control downsampling and processing options
- Choose between mesh, point cloud, or both outputs

## Comparison: Mesh vs Point Cloud

| Feature | TSDF Mesh | Raw Point Cloud |
|---------|-----------|-----------------|
| **Output** | Watertight triangle mesh | Colored 3D points |
| **Processing** | Volumetric integration | Direct projection |
| **Memory** | Lower (voxel grid) | Higher (all points) |
| **Speed** | Slower (integration) | Faster (direct export) |
| **Quality** | Smooth, complete surfaces | Raw, detailed, may have holes |
| **Use Cases** | Rendering, CAD, physics | Analysis, ML, registration |

## Configuration

Edit `config/pipeline/default.yaml`:

```yaml
reconstruction:
  # Choose mode: "mesh", "pointcloud", or "both"
  mode: "pointcloud"
  
  # Point Cloud Settings
  pointcloud:
    # Export merged point cloud from all frames
    export_merged: true
    
    # Export individual frame point clouds
    export_individual: false
    
    # Voxel size for downsampling (0 = no downsampling)
    # Smaller = more points, larger file
    downsample_voxel: 0.01
    
    # Process every Nth frame (1 = all frames)
    # Higher = faster, fewer points
    frame_skip: 1
    
    # Maximum depth in meters
    depth_max: 3.0
```

## Usage Examples

### Export Point Cloud Only

```yaml
reconstruction:
  mode: "pointcloud"
  pointcloud:
    export_merged: true
    export_individual: false
    downsample_voxel: 0.01
    frame_skip: 1
```

Run:
```bash
python bin/run_pipeline.py
```

Output: `output/dense/pointclouds/merged_point_cloud.ply`

### Export Both Mesh and Point Cloud

```yaml
reconstruction:
  mode: "both"
  mesh:
    voxel_size: 0.01
  pointcloud:
    export_merged: true
    downsample_voxel: 0.01
```

Outputs:
- `output/dense/mesh.ply` - TSDF mesh
- `output/dense/pointclouds/merged_point_cloud.ply` - Point cloud

### Export Individual Frame Point Clouds

```yaml
reconstruction:
  mode: "pointcloud"
  pointcloud:
    export_merged: true
    export_individual: true  # Export per-frame clouds
    downsample_voxel: 0.01
```

Outputs:
- `output/dense/pointclouds/merged_point_cloud.ply`
- `output/dense/pointclouds/frames/frame_000000.ply`
- `output/dense/pointclouds/frames/frame_000001.ply`
- ...

### High-Quality, Detailed Point Cloud

```yaml
reconstruction:
  mode: "pointcloud"
  pointcloud:
    export_merged: true
    downsample_voxel: 0.005  # Smaller voxel = more detail
    frame_skip: 1            # Process all frames
    depth_max: 5.0           # Include more distant points
```

### Fast, Lightweight Point Cloud

```yaml
reconstruction:
  mode: "pointcloud"
  pointcloud:
    export_merged: true
    downsample_voxel: 0.05   # Larger voxel = fewer points
    frame_skip: 5            # Every 5th frame
    depth_max: 2.0           # Closer points only
```

## Standalone Script Usage

You can also run the point cloud export script directly:

```bash
python scripts/04_export_point_clouds.py \
  --frames_dir /path/to/frames \
  --intrinsic /path/to/intrinsic.json \
  --trajectory output/sparse/trajectory_open3d.log \
  --output_dir output/dense/pointclouds \
  --downsample_voxel 0.01 \
  --frame_skip 1 \
  --depth_max 3.0 \
  --export_merged \
  --export_individual  # Optional
```

## Visualization

### Open3D Viewer

```bash
# View point cloud
python -c "import open3d as o3d; pcd = o3d.io.read_point_cloud('output/dense/pointclouds/merged_point_cloud.ply'); o3d.visualization.draw_geometries([pcd])"

# View with normals estimation
python -c "
import open3d as o3d
pcd = o3d.io.read_point_cloud('output/dense/pointclouds/merged_point_cloud.ply')
pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
o3d.visualization.draw_geometries([pcd], point_show_normal=True)
"
```

### CloudCompare

```bash
cloudcompare.CloudCompare output/dense/pointclouds/merged_point_cloud.ply
```

### MeshLab

```bash
meshlab output/dense/pointclouds/merged_point_cloud.ply
```

## Post-Processing Options

### Remove Outliers

```python
import open3d as o3d

# Load point cloud
pcd = o3d.io.read_point_cloud('output/dense/pointclouds/merged_point_cloud.ply')

# Remove statistical outliers
pcd_clean, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)

# Save cleaned cloud
o3d.io.write_point_cloud('cleaned_cloud.ply', pcd_clean)
```

### Downsample Further

```python
import open3d as o3d

pcd = o3d.io.read_point_cloud('output/dense/pointclouds/merged_point_cloud.ply')
pcd_down = pcd.voxel_down_sample(voxel_size=0.02)  # 2cm voxels
o3d.io.write_point_cloud('downsampled_cloud.ply', pcd_down)
```

### Convert to Mesh (Poisson Surface Reconstruction)

```python
import open3d as o3d

# Load and prepare point cloud
pcd = o3d.io.read_point_cloud('output/dense/pointclouds/merged_point_cloud.ply')
pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

# Poisson reconstruction
mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=9)

# Remove low-density vertices
vertices_to_remove = densities < np.quantile(densities, 0.01)
mesh.remove_vertices_by_mask(vertices_to_remove)

# Save mesh
o3d.io.write_triangle_mesh('poisson_mesh.ply', mesh)
```

## Performance Tips

1. **Memory**: Point clouds can be very large (millions of points)
   - Use `downsample_voxel` to reduce memory usage
   - Use `frame_skip` to process fewer frames

2. **Speed**: Point cloud export is faster than TSDF fusion
   - No volumetric integration overhead
   - Parallelizable per-frame processing

3. **Quality**: For best results:
   - Use `frame_skip: 1` (all frames)
   - Use small `downsample_voxel` (0.005-0.01)
   - Ensure good ORB_SLAM3 tracking

4. **Disk Space**: 
   - Typical merged cloud: 50-500 MB
   - Individual frames: 1-5 MB per frame
   - Use compression: PLY binary format (default)

## Troubleshooting

### Point cloud is empty or has few points
- Check `depth_max` - might be too restrictive
- Check camera trajectory quality
- Verify depth images are valid

### Point cloud is too large
- Increase `downsample_voxel` (0.02 or 0.05)
- Increase `frame_skip` (2, 5, or 10)
- Reduce `depth_max`

### Point cloud has noise/outliers
- Use statistical outlier removal (see post-processing)
- Increase `downsample_voxel` slightly
- Check depth image quality

## When to Use Each Mode

**Use Point Cloud when:**
- You need raw, unfiltered data
- You want to do custom processing
- You need to preserve all detail
- You're doing registration or ICP
- You're training ML models

**Use TSDF Mesh when:**
- You need watertight surfaces
- You want smooth geometry
- You need lower file sizes
- You're doing rendering or visualization
- You need CAD-compatible output

**Use Both when:**
- You want flexibility
- You're not sure which you'll need
- You have enough disk space
- You want to compare results
