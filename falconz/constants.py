#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains the constants that are used in the falconz.

The variables in this module can be imported and used in other modules within the falconz.
"""

import os
from datetime import datetime

from falconz import file_utilities

# Get the root directory of the virtual environment
project_root = file_utilities.get_virtual_env_root()

# Set the path to the binary folder
BINARY_PATH = os.path.join(project_root, 'bin')

# Set the paths to the binaries based on the operating system
if file_utilities.get_system()[0] == 'windows':
    GREEDY_PATH = os.path.join(BINARY_PATH, f'falcon-{file_utilities.get_system()[0]}-{file_utilities.get_system()[1]}',
                               'greedy.exe')
    C3D_PATH = os.path.join(BINARY_PATH, f'falcon-{file_utilities.get_system()[0]}-{file_utilities.get_system()[1]}',
                            'c3d.exe')
    DCM2NIIX_PATH = os.path.join(BINARY_PATH,
                                 f'falcon-{file_utilities.get_system()[0]}-{file_utilities.get_system()[1]}',
                                 'dcm2niix.exe')
elif file_utilities.get_system()[0] in ['linux', 'mac']:
    GREEDY_PATH = os.path.join(BINARY_PATH, f'falcon-{file_utilities.get_system()[0]}-{file_utilities.get_system()[1]}',
                               'greedy')
    C3D_PATH = os.path.join(BINARY_PATH, f'falcon-{file_utilities.get_system()[0]}-{file_utilities.get_system()[1]}',
                            'c3d')
    DCM2NIIX_PATH = os.path.join(BINARY_PATH, f'falcon-{file_utilities.get_system()[0]}-{file_utilities.get_system()[1]}',
                                    'dcm2niix')
else:
    raise ValueError('Unsupported OS')

# Define color codes for console output
ANSI_ORANGE = '\033[38;5;208m'
ANSI_GREEN = '\033[32m'
ANSI_VIOLET = '\033[38;5;141m'
ANSI_RED = '\033[38;5;196m'
ANSI_RESET = '\033[0m'

# Define the allowed modalities
MODALITIES = ['PET', 'CT', 'MR']

# Define the minimum system requirements for each registration paradigm
MINIMUM_RAM_REQUIRED_RIGID = 4  # in GB
MINIMUM_RAM_REQUIRED_AFFINE = 8  # in GB
MINIMUM_RAM_REQUIRED_DEFORMABLE = 16  # in GB
MINIMUM_THREADS_REQUIRED_RIGID = 2  # in number of threads
MINIMUM_THREADS_REQUIRED_AFFINE = 4  # in number of threads
MINIMUM_THREADS_REQUIRED_DEFORMABLE = 8  # in number of threads

# Define the shrink levels supported
SHRINK_LEVEL = [2, 4, 8]

# Define the normalized cross correlation threshold and radius
NCC_THRESHOLD = 0.5
NCC_RADIUS = '4x4x4'

# Define the file names and folder names used in the FALCONZ pipeline
MOCO_PREFIX = 'moco_'
ALIGNED_PREFIX = 'aligned_'
TRANSFORMS_KEYWORD = ['*warp.nii.gz', '*rigid.mat', '*affine.mat']
MOCO_4D_FILE_NAME = 'moco_4D.nii.gz'
FALCON_WORKING_FOLDER = 'FALCONZ-V02' + '-' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
TRANSFORMS_FOLDER = 'transforms'
MOCO_FOLDER = 'Motion-corrected-images'
SPLIT_FOLDER = 'Split-Nifti-files'

# Define the hyperparameters used in the registration process
MULTI_RESOLUTION_SCHEME = '100x25x10'
MULTI_RESOLUTION_SCHEME_DASH = '100x25x10x0'
EXPECTED_DIMENSIONS = 4
ALLOWED_REGISTRATION_PARADIGMS = ["rigid", "affine", "deformable"]
IMAGE_INTERPOLATION = 'Linear'
MASK_INTERPOLATION = 'Nearest Neighbor'
COST_FUNCTION = 'NCC 2x2x2'
PROPORTION_OF_CORES = 1 / 8  # 1/8th of the available cores will be used for motion correction

# ALLOWED EXTENSIONS

VALID_EXTENSIONS = ['.nii', '.nii.gz', '.hdr', '.img', '.nrrd', '.mha', '.mhd']

# ALLOWED MODES

ALLOWED_MODES = ['cruise', 'dash']
