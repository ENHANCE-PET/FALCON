#!/usr/bin/env python
# -*- coding: utf-8 -*-


# **********************************************************************************************************************
# File: run_falcon.py
# Project: falcon
# Created: 27.01.2022
# Author: Lalith Kumar Shiyam Sundar
# Email: lalith.shiyamsundar@meduniwien.ac.at
# Institute: Quantitative Imaging and Medical Physics, Medical University of Vienna
# Description: Falcon (FALCON) is a tool for the performing dynamic PET motion correction. It is based on the greedy
# algorithm developed by the Paul Yushkevich. The algorithm is capable of performing fast rigid/affine/deformable
# registration.
# License: Apache 2.0
# **********************************************************************************************************************


# Libraries to import

import os
import re


# Functions that call greedy


def rigid(fixed_img: str, moving_img: str, cost_function: str) -> None:
    """ Performs rigid registration between a fixed and moving image using the greedy registration toolkit.
    :param fixed_img: Reference image
    :param moving_img: Moving image
    :param cost_function: Cost function
    :return none
    """
    cmd_to_run = f"greedy -d 3 -a -i " \
                 f"{re.escape(fixed_img)} {re.escape(moving_img)} -ia-image-centers -dof 6 -o rigid.mat -n 100x50x25 " \
                 f"-m {cost_function}"
    print("*******************************************************************************************")
    print(f"Registration type: Rigid")
    print(f"Reference image: {re.escape(fixed_img)}")
    print(f"Moving image: {re.escape(moving_img)}")
    print(f"Cost function: {cost_function}")
    print(f"Initial alignment: Image centers")
    print(f"Multi-resolution level iterations: 100x50x25")
    print(f"Transform file generated: rigid.mat")
    print("*******************************************************************************************")
    os.system(cmd_to_run)
    print("Rigid registration complete")


def affine(fixed_img: str, moving_img: str, cost_function: str) -> None:
    """ Performs affine registration between a fixed and moving image using the greedy registration toolkit.
    :param fixed_img: Reference image
    :param moving_img: Moving image
    :param cost_function: Cost function
    :return none
    """
    cmd_to_run = f"greedy -d 3 -a -i {re.escape(fixed_img)} {re.escape(moving_img)} -ia-image-centers -dof 12 -o " \
                 f"affine.mat -n " \
                 f"100x50x25 " \
                 f"-m {cost_function} "
    print("*******************************************************************************************")
    print(f"- Registration type: Affine")
    print(f"- Reference image: {re.escape(fixed_img)}")
    print(f"- Moving image: {re.escape(moving_img)}")
    print(f"- Cost function: {cost_function}")
    print(f"- Initial alignment: Image centers")
    print(f"- Multi-resolution level iterations: 100x50x25")
    print(f"- Transform file generated: affine.mat")
    print("*******************************************************************************************")
    os.system(cmd_to_run)
    print("Affine registration complete")


def deformable(fixed_img: str, moving_img: str, cost_function: str) -> None:
    """
    Performs deformable registration between a fixed and moving image using the greedy registration toolkit.
    :param fixed_img: Reference image
    :param moving_img: Moving image
    :param cost_function: Cost function
    :return:
    """
    print("*******************************************************************************************")
    print("Performing affine registration for initial global alignment")
    affine(fixed_img, moving_img, cost_function)
    cmd_to_run = f"greedy -d 3 -m {cost_function} -i {re.escape(fixed_img)} {re.escape(moving_img)} -it affine.mat -o " \
                 f"warp.nii.gz -oinv " \
                 f"inverse_warp.nii.gz -n 100x50x25"
    print("*******************************************************************************************")
    print(f"- Registration type: deformable")
    print(f"- Reference image: {re.escape(fixed_img)}")
    print(f"- Moving image: {re.escape(moving_img)}")
    print(f"- Cost function: {cost_function}")
    print(f"- Initial alignment: based on affine.mat")
    print(f"- Multiresolution level iterations: 100x50x25")
    print(f"- Deformation field generated: warp.nii.gz + inverse_warp.nii.gz")
    print("*******************************************************************************************")

    os.system(cmd_to_run)
    print("Deformable registration complete")


def resample(fixed_img: str, moving_img: str, resampled_moving_img: str, registration_type: str, segmentation="",
             resampled_seg="") -> None:
    """
    Resamples a moving image to match the resolution of a fixed image.
    :param fixed_img: Reference image
    :param moving_img: Moving image
    :param resampled_moving_img: Resampled moving image
    :param registration_type: 'rigid', 'affine', or 'deformable'
    :param segmentation: Mask image corresponding to moving image that needs to be resampled to match reference image
    :param resampled_seg: Resampled mask image
    :return:
    """
    if registration_type == 'rigid':
        if segmentation and resampled_seg:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(fixed_img)} -ri NN -rm {re.escape(moving_img)} " \
                         f"{re.escape(resampled_moving_img)} -ri LABEL " \
                         f"0.2vox -rm {re.escape(segmentation)} {re.escape(resampled_seg)} -r rigid.mat"
        else:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(fixed_img)} -ri NN -rm {re.escape(moving_img)} " \
                         f"{re.escape(resampled_moving_img)} -r rigid.mat "
    elif registration_type == 'affine':
        if segmentation and resampled_seg:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(fixed_img)} -ri NN -rm {re.escape(moving_img)} " \
                         f"{re.escape(resampled_moving_img)} -ri LABEL " \
                         f"0.2vox -rm {re.escape(segmentation)} {re.escape(resampled_seg)} -r affine.mat"
        else:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(fixed_img)} -ri NN -rm {re.escape(moving_img)} " \
                         f"{re.escape(resampled_moving_img)} -r affine.mat"
    elif registration_type == 'deformable':
        if segmentation and resampled_seg:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(fixed_img)} -ri NN -rm {re.escape(moving_img)} " \
                         f"{re.escape(resampled_moving_img)} -ri LABEL " \
                         f"0.2vox -rm {re.escape(segmentation)} {re.escape(resampled_seg)} -r warp.nii.gz affine.mat"
        else:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(fixed_img)} -ri NN -rm {re.escape(moving_img)} " \
                         f"{re.escape(resampled_moving_img)} -r warp.nii.gz " \
                         f"affine.mat"
    os.system(cmd_to_run)
    print("*******************************************************************************************")
    print(f"Resampling parameters")
    print("*******************************************************************************************")
    print(f"- Reference image: {re.escape(fixed_img)}")
    print(f"- Moving image: {re.escape(moving_img)}")
    print(f"- Resampled moving image: {resampled_moving_img}")
    print(f"- Segmentation: {segmentation}")
    print(f"- Resampled segmentation: {resampled_seg}")
    print(f"- Interpolation scheme for resampling: Nearest neighbor for images and segmentations")
    print("*******************************************************************************************")
