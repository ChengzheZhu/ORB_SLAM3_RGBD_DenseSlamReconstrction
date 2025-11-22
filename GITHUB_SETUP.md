# GitHub Setup Guide

## Step-by-Step Instructions

### Step 1: Create GitHub Repository (On GitHub Website)

1. Go to https://github.com/new
2. Repository name: `slam-dense-reconstruction`
3. Description: `ORB_SLAM3 + Open3D pipeline for RGB-D SLAM and dense 3D reconstruction`
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### Step 2: Initialize Local Git Repository

```bash
cd /home/chengzhe/projects/slam_dense_reconstruction

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: ORB_SLAM3 + Open3D dense reconstruction pipeline"
```

### Step 3: Connect to GitHub

Replace `YOUR_USERNAME` with your GitHub username:

```bash
# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/slam-dense-reconstruction.git

# Or using SSH (if you have SSH keys set up):
git remote add origin git@github.com:YOUR_USERNAME/slam-dense-reconstruction.git
```

### Step 4: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

### Step 5: Verify Upload

1. Go to `https://github.com/YOUR_USERNAME/slam-dense-reconstruction`
2. You should see all your files!

## Quick One-Liner (After Creating GitHub Repo)

```bash
cd /home/chengzhe/projects/slam_dense_reconstruction && \
git init && \
git add . && \
git commit -m "Initial commit: ORB_SLAM3 + Open3D dense reconstruction pipeline" && \
git remote add origin https://github.com/YOUR_USERNAME/slam-dense-reconstruction.git && \
git branch -M main && \
git push -u origin main
```

## Files That Will Be Included

✅ **bin/** - Pipeline executables
✅ **src/** - Source code modules
✅ **config/** - Configuration files
✅ **scripts/** - Utility scripts
✅ **install/** - Installation scripts
✅ **external/** - Dependency documentation
✅ **docs/** - All documentation
✅ **README.md** - Project overview
✅ **requirements.txt** - Python dependencies
✅ **.gitignore** - Ignore rules

## Files That Will Be EXCLUDED (per .gitignore)

❌ **output/** - Generated trajectories and meshes
❌ **data/** - Large bag files
❌ **\*.ply** - Mesh files
❌ **\*.log** - Log files
❌ **__pycache__/** - Python cache

## After Upload

### Clone on Another Machine
```bash
git clone https://github.com/YOUR_USERNAME/slam-dense-reconstruction.git
cd slam-dense-reconstruction
./install/install_dependencies.sh
./install/build_orbslam3.sh
pip install -r requirements.txt
```

### Update Repository After Changes
```bash
# Check status
git status

# Add changed files
git add <files>

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push
```

## Recommended Repository Settings

### Add Topics (On GitHub)
- `slam`
- `3d-reconstruction`
- `orbslam3`
- `open3d`
- `rgbd`
- `realsense`
- `computer-vision`

### Create a Good README Badge Section
Add to top of README.md:
```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
```

### Add a License
Choose a license at https://choosealicense.com/
Recommended: MIT or GPL-3.0

## Troubleshooting

### Large Files Error
If GitHub rejects push due to large files:
```bash
# Check file sizes
find . -type f -size +50M

# Add to .gitignore if needed
echo "path/to/large/file" >> .gitignore

# Remove from git tracking but keep locally
git rm --cached path/to/large/file
```

### Authentication Required
If prompted for username/password:

**Option 1: Use Personal Access Token (HTTPS)**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Use token as password when prompted

**Option 2: Use SSH Keys**
1. Generate SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
2. Add to GitHub: Settings → SSH and GPG keys
3. Use SSH URL instead of HTTPS

### Already Have a Git Repo?
```bash
# Remove existing git (if any)
rm -rf .git

# Start fresh
git init
```

## Repository URL Format

**HTTPS:**
```
https://github.com/YOUR_USERNAME/slam-dense-reconstruction.git
```

**SSH:**
```
git@github.com:YOUR_USERNAME/slam-dense-reconstruction.git
```

## Example Full Workflow

```bash
# 1. On local machine
cd /home/chengzhe/projects/slam_dense_reconstruction
git init
git add .
git commit -m "Initial commit: Complete ORB_SLAM3 + Open3D pipeline

Features:
- ORB_SLAM3 integration for sparse SLAM
- Open3D TSDF reconstruction
- Configurable pipeline system
- Viewer toggle for batch processing
- Complete documentation
"

# 2. Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/slam-dense-reconstruction.git

# 3. Push to GitHub
git branch -M main
git push -u origin main

# 4. Done! View at:
# https://github.com/YOUR_USERNAME/slam-dense-reconstruction
```

## Making Repository Discoverable

### Add to README.md

```markdown
## Citation

If you use this code in your research, please cite:

\`\`\`bibtex
@software{slam_dense_reconstruction,
  author = {Your Name},
  title = {ORB_SLAM3 + Open3D Dense Reconstruction Pipeline},
  year = {2024},
  url = {https://github.com/YOUR_USERNAME/slam-dense-reconstruction}
}
\`\`\`
```

### Add Screenshots

Create `docs/images/` directory and add:
- SLAM visualization screenshot
- Dense mesh result
- Pipeline diagram

Reference in README.md:
```markdown
## Results

![SLAM Tracking](docs/images/slam_tracking.png)
![Dense Mesh](docs/images/dense_mesh.png)
```
