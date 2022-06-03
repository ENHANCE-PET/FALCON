#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **********************************************************************************************************************
# File: constants.py
# Project: FALCON
# Created: 27.03.2022
# Author: Lalith Kumar Shiyam Sundar
# Email: lalith.shiyamsundar@meduniwien.ac.at
# Institute: Quantitative Imaging and Medical Physics, Medical University of Vienna
# Description: This module contains all the constants that are being used in the FALCON project.
# License: Apache 2.0
# **********************************************************************************************************************
# Hard-coded variables

MINIMUM_RAM_REQUIRED_RIGID = 8  # in GB
MINIMUM_RAM_REQUIRED_AFFINE = 16  # in GB
MINIMUM_RAM_REQUIRED_DEFORMABLE = 32  # in GB
MINIMUM_THREADS_REQUIRED_RIGID = 4  # in number of threads
MINIMUM_THREADS_REQUIRED_AFFINE = 8  # in number of threads
MINIMUM_THREADS_REQUIRED_DEFORMABLE = 16  # in number of threads

# Shrink levels supported:
SHRINK_LEVEL_2x = 2
SHRINK_LEVEL_4x = 4
SHRINK_LEVEL_8x = 8

MI_REFERENCE_PERCENTAGE = 0.8 # in percent, only 20% of the original pet files will be used for reference MI calculation