#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
.. module:: input_validation
   :platform: Unix, Windows
   :synopsis: A module for input validation for the falconz.

.. moduleauthor:: Lalith Kumar Shiyam Sundar <lalith.shiyamsundar@meduniwien.ac.at>

This module handles input validation for the falconz.

Usage:
    The functions in this module can be imported and used in other modules within the falconz to perform image conversion.
"""
import logging
import os

from falconz.constants import ALLOWED_MODES


class InputValidation:
    """
    A class for input validation for the falconz.

    :param args: The arguments to validate.
    :type args: Any
    """

    def __init__(self, args):
        self.args = args

    def validate(self):
        """
        Validates the input arguments.
        """
        self._check_directory_exists()
        self._check_reference_frame_index()
        self._check_start_frame()
        self._check_registration_type()
        self._check_multi_resolution_iterations()
        self._check_operation_mode()
        logging.info("Input validation successful.")

    def _check_directory_exists(self):
        """
        Checks if the specified directory exists.
        """
        if not os.path.exists(self.args.directory):
            raise ValueError(f"The specified directory does not exist: {self.args.directory}")

    def _check_reference_frame_index(self):
        """
        Checks if the reference frame index is valid.
        """
        if not isinstance(self.args.reference_frame_index, int) or self.args.reference_frame_index < -1:
            raise ValueError(
                f"Reference frame index must be a non-negative integer or -1: {self.args.reference_frame_index}")

    def _check_start_frame(self):
        """
        Checks if the start frame is valid.
        """
        if not isinstance(self.args.start_frame, int) or self.args.start_frame < 0:
            raise ValueError(f"Start frame must be a non-negative integer: {self.args.start_frame}")

    def _check_registration_type(self):
        """
        Checks if the registration type is valid.
        """
        allowed_registration_paradigms = ["rigid", "affine", "deformable"]
        if self.args.registration not in allowed_registration_paradigms:
            raise ValueError(f"Invalid registration type. Allowed values are: {allowed_registration_paradigms}")

    def _check_multi_resolution_iterations(self):
        """
        Checks if the multi-resolution iterations are valid.
        """
        if not isinstance(self.args.multi_resolution_iterations, str) or not all(
                i.isdigit() for i in self.args.multi_resolution_iterations.split('x')):
            raise ValueError(
                f"Multi resolution iterations must be a 'x' separated numeric string: {self.args.multi_resolution_iterations}")

    def _check_operation_mode(self):
        """
        Checks if the operation mode is valid.
        """
        if self.args.mode not in ALLOWED_MODES:
            raise ValueError(f"Invalid operation mode. Allowed values are: {ALLOWED_MODES}")