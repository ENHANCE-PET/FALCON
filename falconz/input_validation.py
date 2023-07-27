#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# Author: Lalith Kumar Shiyam Sundar
#
# Institution: Medical University of Vienna
# Research Group: Quantitative Imaging and Medical Physics (QIMP) Team
# Date: 07.07.2023
# Version: 2.0.0
#
# Description:
# This module handles input validation for the falconz.
#
# Usage:
# The functions in this module can be imported and used in other modules within the falconz to perform image conversion.
#
# ----------------------------------------------------------------------------------------------------------------------
import os
import logging

class InputValidation:
    def __init__(self, args):
        self.args = args

    def validate(self):
        self._check_directory_exists()
        self._check_reference_frame_index()
        self._check_start_frame()
        self._check_registration_type()
        self._check_multi_resolution_iterations()
        logging.info("Input validation successful.")

    def _check_directory_exists(self):
        if not os.path.exists(self.args.main_folder):
            raise ValueError(f"The specified directory does not exist: {self.args.main_folder}")

    def _check_reference_frame_index(self):
        if not isinstance(self.args.reference_frame_index, int) or self.args.reference_frame_index < -1:
            raise ValueError(
                f"Reference frame index must be a non-negative integer or -1: {self.args.reference_frame_index}")

    def _check_start_frame(self):
        if not isinstance(self.args.start_frame, int) or self.args.start_frame < 0:
            raise ValueError(f"Start frame must be a non-negative integer: {self.args.start_frame}")

    def _check_registration_type(self):
        allowed_registration_paradigms = ["rigid", "affine", "deformable"]
        if self.args.registration not in allowed_registration_paradigms:
            raise ValueError(f"Invalid registration type. Allowed values are: {allowed_registration_paradigms}")

    def _check_multi_resolution_iterations(self):
        if not isinstance(self.args.multi_resolution_iterations, str) or not all(
                i.isdigit() for i in self.args.multi_resolution_iterations.split('x')):
            raise ValueError(
                f"Multi resolution iterations must be a 'x' separated numeric string: {self.args.multi_resolution_iterations}")
