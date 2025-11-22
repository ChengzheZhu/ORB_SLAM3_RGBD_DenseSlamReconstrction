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
