#!/usr/bin/env python
# -*- coding: utf-8 -*-


# **********************************************************************************************************************
# File: greedy.py
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

import logging
import os
import pathlib
import re
import subprocess
import sys

from mpire import WorkerPool


def rigid(fixed_img: str, moving_img: str, cost_function: str, multi_resolution_iterations: str) -> str:
    """ Performs rigid registration between a fixed and moving image using the greedy registration toolkit.
    :param fixed_img: Reference image
    :param moving_img: Moving image
    :param cost_function: Cost function
    :param multi_resolution_iterations: Amount of iterations for each resolution level
    :return str
    """
    out_dir = pathlib.Path(moving_img).parent
    moving_img_filename = pathlib.Path(moving_img).name
    rigid_transform_file = os.path.join(out_dir, f"{moving_img_filename}_rigid.mat")
    cmd_to_run = f"greedy -d 3 -a -i " \
                 f"{re.escape(fixed_img)} {re.escape(moving_img)} -ia-image-centers -dof 6 -o " \
                 f"{re.escape(rigid_transform_file)} -n " \
                 f"{multi_resolution_iterations} " \
                 f"-m {cost_function}"
    subprocess.run(cmd_to_run, shell=True, capture_output=True)
    logging.info(f"Aligning: {pathlib.Path(moving_img).name} -> {pathlib.Path(fixed_img).name} | Aligned image: "
                 f"moco-{pathlib.Path(moving_img).name} | Cost function: {cost_function} | Initial alignment: Image "
                 f"centers | Transform file: {pathlib.Path(rigid_transform_file).name}")
    print(f"Rigid alignment: {pathlib.Path(moving_img).name} -> {pathlib.Path(fixed_img).name} | Aligned image: moco-"
          f"{pathlib.Path(moving_img).name} | Cost function: {cost_function} | Initial alignment: Image centers | "
          f"Transform file: {pathlib.Path(rigid_transform_file).name}")
    return rigid_transform_file


def affine(fixed_img: str, moving_img: str, cost_function: str, multi_resolution_iterations: str) -> str:
    """ Performs affine registration between a fixed and moving image using the greedy registration toolkit.
    :param fixed_img: Reference image
    :param moving_img: Moving image
    :param cost_function: Cost function
    :param multi_resolution_iterations: Amount of iterations for each resolution level
    :return str : Path of the Affine transform file generated
    """
    out_dir = pathlib.Path(moving_img).parent
    moving_img_filename = pathlib.Path(moving_img).name
    affine_transform_file = os.path.join(out_dir, f"{moving_img_filename}_affine.mat")
    cmd_to_run = f"greedy -d 3 -a -i {re.escape(fixed_img)} {re.escape(moving_img)} -ia-image-centers -dof 12 -o " \
                 f"{re.escape(affine_transform_file)} -n " \
                 f"{multi_resolution_iterations} " \
                 f"-m {cost_function} "
    subprocess.run(cmd_to_run, shell=True, capture_output=True)
    logging.info(f"Affine alignment: {pathlib.Path(moving_img).name} -> {pathlib.Path(fixed_img).name} | Aligned "
                 f"image: moco-{pathlib.Path(moving_img).name} | Cost function: {cost_function} | Initial alignment: "
                 f"Image centers | Transform file: {pathlib.Path(affine_transform_file).name}")
    print(f"Affine alignment: {pathlib.Path(moving_img).name} -> {pathlib.Path(fixed_img).name} | Aligned image: moco-"
          f"{pathlib.Path(moving_img).name} | Cost function: {cost_function} | Initial alignment: Image centers | "
          f"Transform file: {pathlib.Path(affine_transform_file).name}")
    return affine_transform_file


def deformable(fixed_img: str, moving_img: str, cost_function: str, multi_resolution_iterations: str) -> tuple:
    """
    Performs deformable registration between a fixed and moving image using the greedy registration toolkit.
    :param fixed_img: Reference image
    :param moving_img: Moving image
    :param cost_function: Cost function
    :param multi_resolution_iterations: Amount of iterations for each resolution level
    :return:
    """
    out_dir = pathlib.Path(moving_img).parent
    moving_img_filename = pathlib.Path(moving_img).name
    warp_file = os.path.join(out_dir, f"{moving_img_filename}_warp.nii.gz")
    inverse_warp_file = os.path.join(out_dir, f"{moving_img_filename}_inverse_warp.nii.gz")
    affine_transform_file = affine(fixed_img, moving_img, cost_function, multi_resolution_iterations)
    cmd_to_run = f"greedy -d 3 -m {cost_function} -i {re.escape(fixed_img)} {re.escape(moving_img)} -it " \
                 f"{re.escape(affine_transform_file)} -o " \
                 f"{re.escape(warp_file)} -oinv " \
                 f"{re.escape(inverse_warp_file)} -n {multi_resolution_iterations}"
    subprocess.run(cmd_to_run, shell=True, capture_output=True)
    logging.info(f"Deformable alignment: {pathlib.Path(moving_img).name} -> {pathlib.Path(fixed_img).name} | Aligned "
                 f"image: moco-{pathlib.Path(moving_img).name} | Cost function: {cost_function} | Initial "
                 f"alignment:{pathlib.Path(affine_transform_file).name} | warp file: {pathlib.Path(warp_file).name}")
    print(f"Deformable alignment: {pathlib.Path(moving_img).name} -> {pathlib.Path(fixed_img).name} | Aligned image: "
          f"moco-{pathlib.Path(moving_img).name} | Cost function: {cost_function} | Initial alignment:{pathlib.Path(affine_transform_file).name} | "
          f"warp file: {pathlib.Path(warp_file).name}")
    return affine_transform_file, warp_file, inverse_warp_file


def registration(fixed_img: str, moving_img: str, registration_type: str, multi_resolution_iterations: str) -> None:
    """
    Registers the fixed and the moving image using the greedy registration toolkit based on the user given cost function
    :param fixed_img: Reference image
    :param moving_img: Moving image
    :param registration_type: Type of registration ('rigid', 'affine' or 'deformable')
    :param multi_resolution_iterations: Amount of iterations for each resolution level
    :return: None
    """
    if registration_type == 'rigid':
        rigid(fixed_img, moving_img, cost_function='NMI', multi_resolution_iterations=multi_resolution_iterations)
    elif registration_type == 'affine':
        affine(fixed_img, moving_img, cost_function='NMI', multi_resolution_iterations=multi_resolution_iterations)
    elif registration_type == 'deformable':
        deformable(fixed_img, moving_img, cost_function='NCC 2x2x2',
                   multi_resolution_iterations=multi_resolution_iterations)
    else:
        sys.exit("Registration type not supported!")


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
    :return: None
    """
    moving_img_file = pathlib.Path(moving_img).name
    out_dir = pathlib.Path(moving_img).parent
    if registration_type == 'rigid':
        rigid_transform_file = os.path.join(out_dir, f"{moving_img_file}_rigid.mat")
        if segmentation and resampled_seg:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(fixed_img)} -ri LINEAR -rm {re.escape(moving_img)} " \
                         f"{re.escape(resampled_moving_img)} -ri LABEL " \
                         f"0.2vox -rm {re.escape(segmentation)} {re.escape(resampled_seg)} -r " \
                         f"{re.escape(rigid_transform_file)}"
        else:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(fixed_img)} -ri LINEAR -rm {re.escape(moving_img)} " \
                         f"{re.escape(resampled_moving_img)} -r {re.escape(rigid_transform_file)} "
    elif registration_type == 'affine':
        affine_transform_file = os.path.join(out_dir, f"{moving_img_file}_affine.mat")
        if segmentation and resampled_seg:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(fixed_img)} -ri LINEAR -rm {re.escape(moving_img)} " \
                         f"{re.escape(resampled_moving_img)} -ri LABEL " \
                         f"0.2vox -rm {re.escape(segmentation)} {re.escape(resampled_seg)} -r " \
                         f"{re.escape(affine_transform_file)}"
        else:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(fixed_img)} -ri LINEAR -rm {re.escape(moving_img)} " \
                         f"{re.escape(resampled_moving_img)} -r {re.escape(affine_transform_file)}"
    elif registration_type == 'deformable':
        warp_file = os.path.join(out_dir, f"{moving_img_file}_warp.nii.gz")
        affine_transform_file = os.path.join(out_dir, f"{moving_img_file}_affine.mat")
        if segmentation and resampled_seg:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(fixed_img)} -ri LINEAR -rm {re.escape(moving_img)} " \
                         f"{re.escape(resampled_moving_img)} -ri LABEL " \
                         f"0.2vox -rm {re.escape(segmentation)} {re.escape(resampled_seg)} -r {re.escape(warp_file)} " \
                         f"{re.escape(affine_transform_file)}"
        else:
            cmd_to_run = f"greedy -d 3 -rf {re.escape(fixed_img)} -ri LINEAR -rm {re.escape(moving_img)} " \
                         f"{re.escape(resampled_moving_img)} -r {re.escape(warp_file)} " \
                         f"{re.escape(affine_transform_file)}"
    else:
        sys.exit("Registration type not supported!")
    subprocess.run(cmd_to_run, shell=True, capture_output=True)


def align(fixed_img: str, moving_imgs: list, registration_type: str, multi_resolution_iterations: str, njobs: int,
          moco_dir: str) -> None:
    """
    Aligns the images in the moving_imgs list to a fixed image.
    :param moco_dir: Directory where the output files will be saved
    :param fixed_img: Path to the fixed image
    :param moving_imgs: List of paths to the moving images
    :param registration_type: Type of registration to be performed
    :param multi_resolution_iterations: Number of iterations for multi-resolution
    :param njobs: Number of jobs to run in parallel
    :return:
    """
    logging.info(f"Aligning images...")
    with WorkerPool(n_jobs=njobs, shared_objects=(fixed_img, registration_type, multi_resolution_iterations, moco_dir),
                    start_method='fork', ) as pool:
        pool.map(align_mp, moving_imgs, progress_bar=False)


def align_mp(align_param: tuple, moving_img: str) -> None:
    """
    Aligns a single image to a fixed image.
    :param align_param: Tuple containing the fixed image, the registration type, the number of iterations and the
    output directory
    :param moving_img: Path to the moving image
    :return:
    """
    reference_img, registration_type, multi_resolution_iterations, moco_dir = align_param
    registration(fixed_img=reference_img, moving_img=moving_img,
                 registration_type=registration_type, multi_resolution_iterations=multi_resolution_iterations)
    moving_img_filename = pathlib.Path(moving_img).name
    resample(fixed_img=reference_img, moving_img=moving_img, resampled_moving_img=os.path.join(
        moco_dir, 'moco-' + moving_img_filename), registration_type=registration_type)
