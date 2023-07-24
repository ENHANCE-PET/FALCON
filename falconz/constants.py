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
GREEDY_PATH = os.path.join(BINARY_PATH, f'greedy-{file_utilities.get_system()[0]}-{file_utilities.get_system()[1]}',
                           'greedy')

# COLOR CODES
ANSI_ORANGE = '\033[38;5;208m'
ANSI_GREEN = '\033[38;5;40m'
ANSI_VIOLET = '\033[38;5;141m'
ANSI_RESET = '\033[0m'


# EXPECTED MODALITIES

MODALITIES = ['PET', 'CT']
MODALITIES_PREFIX = ['PT_ for PET', 'CT_ for CT']


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