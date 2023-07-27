#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# Author: Lalith Kumar Shiyam Sundar
# Institution: Medical University of Vienna
# Research Group: Quantitative Imaging and Medical Physics (QIMP) Team
# Date: 04.07.2023
# Version: 0.1.0
#
# Description:
# This module contains the constants that are used in the falconz.
#
# Usage:
# The variables in this module can be imported and used in other modules within the falconz.
#
# ----------------------------------------------------------------------------------------------------------

import os
from falconz import file_utilities
from datetime import datetime

project_root = file_utilities.get_virtual_env_root()
BINARY_PATH = os.path.join(project_root, 'bin')

# SET PATHS TO BINARIES

if file_utilities.get_system()[0] == 'windows':
    GREEDY_PATH = os.path.join(BINARY_PATH, f'greedy-{file_utilities.get_system()[0]}-{file_utilities.get_system()[1]}',
                               'greedy.exe')
elif file_utilities.get_system()[0] in ['linux', 'mac']:
    GREEDY_PATH = os.path.join(BINARY_PATH, f'greedy-{file_utilities.get_system()[0]}-{file_utilities.get_system()[1]}',
                               'greedy')
else:
    raise ValueError('Unsupported OS')


# COLOR CODES
ANSI_ORANGE = '\033[38;5;208m'
ANSI_GREEN = '\033[38;5;40m'
ANSI_VIOLET = '\033[38;5;141m'
ANSI_RESET = '\033[0m'


# ALLOWED MODALITIES

MODALITIES = ['PET', 'CT', 'MR']

# SYSTEM REQUIREMENTS

MINIMUM_RAM_REQUIRED_RIGID = 4  # in GB
MINIMUM_RAM_REQUIRED_AFFINE = 8  # in GB
MINIMUM_RAM_REQUIRED_DEFORMABLE = 16  # in GB
MINIMUM_THREADS_REQUIRED_RIGID = 2  # in number of threads
MINIMUM_THREADS_REQUIRED_AFFINE = 4  # in number of threads
MINIMUM_THREADS_REQUIRED_DEFORMABLE = 8  # in number of threads

# Shrink levels supported:
SHRINK_LEVEL = [2, 4, 8]
NCC_THRESHOLD = 0.6  # Normalized cross correlation threshold
NCC_RADIUS = '4x4x4'  # Normalized cross correlation radius

# FILE NAMES

MOCO_PREFIX = 'moco_'
ALIGNED_PREFIX = 'aligned_'


# FOLDER NAMES

FALCON_WORKING_FOLDER = 'FALCONZ-V02'+'-' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
TRANSFORMS_FOLDER = 'transforms'
MOCO_FOLDER = 'Motion-corrected-images'

# HYPERPARAMETERS

MULTI_RESOLUTION_SCHEME = '100x25x10'
EXPECTED_DIMENSIONS = 4
ALLOWED_REGISTRATION_PARADIGMS = ["rigid", "affine", "deformable"]
IMAGE_INTERPOLATION = 'Linear'
MASK_INTERPOLATION = 'Nearest Neighbor'