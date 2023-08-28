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
# This module handles image processing for the falconz.
#
# Usage:
# The functions in this module can be imported and used in other modules within the falconz to perform image conversion.
#
# ----------------------------------------------------------------------------------------------------------------------

import SimpleITK as sitk
import logging
import multiprocessing
import nibabel
import os
import pandas as pd
import pathlib
import re
import subprocess
from halo import Halo
from mpire import WorkerPool
from nilearn.input_data import NiftiMasker
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm

from falconz import constants
from falconz import file_utilities as fop
from falconz.constants import GREEDY_PATH, C3D_PATH, NCC_RADIUS, NCC_THRESHOLD, COST_FUNCTION
from rich.progress import Progress, BarColumn, TextColumn
from multiprocessing import Pool
from dask import delayed, compute


class ImageRegistration:
    """
    A class for performing image registration using the Greedy method.

    Attributes:
    -----------
    fixed_img : str
        Path to the fixed/target image for registration.
    multi_resolution_iterations : str
        String specifying the number of iterations at each resolution level.
    fixed_mask : str, optional
        Path to a mask for the fixed image. If provided, only the masked region of the fixed image will be used in the registration.
    moving_img : str, optional
        Path to the moving/source image to be registered to the fixed image.
    transform_files : dict, optional
        Dictionary containing paths to the output transformation files for each registration type.
    """

    def __init__(self, fixed_img: str, multi_resolution_iterations: str, fixed_mask: str = None):
        """
        Initializes the ImageRegistration class.

        Parameters:
        -----------
        fixed_img : str
            Path to the fixed/target image.
        multi_resolution_iterations : str
            String specifying the number of iterations at each resolution level.
        fixed_mask : str, optional
            Path to the mask of the fixed image.
        """
        self.fixed_img = fixed_img
        self.fixed_mask = fixed_mask
        self.multi_resolution_iterations = multi_resolution_iterations
        self.moving_img = None
        self.transform_files = None

    def set_moving_image(self, moving_img: str, update_transforms: bool = True):
        """
        Sets the moving image for registration and updates the transform files if specified.

        Parameters:
        -----------
        moving_img : str
            Path to the moving/source image.
        update_transforms : bool, default=True
            If True, will update the paths for the transformation files based on the moving image name.
        """
        self.moving_img = moving_img
        if update_transforms:
            out_dir = pathlib.Path(self.moving_img).parent
            moving_img_filename = pathlib.Path(self.moving_img).name
            self.transform_files = {
                'rigid': os.path.join(out_dir, f"{moving_img_filename}_rigid.mat"),
                'affine': os.path.join(out_dir, f"{moving_img_filename}_affine.mat"),
                'warp': os.path.join(out_dir, f"{moving_img_filename}_warp.nii.gz"),
                'inverse_warp': os.path.join(out_dir, f"{moving_img_filename}_inverse_warp.nii.gz")
            }

    def rigid(self) -> str:
        """
        Perform rigid registration between the moving and fixed images.

        Returns:
        --------
        str
            Path to the resulting rigid transformation file.
        """
        mask_cmd = f"-gm {re.escape(self.fixed_mask)}" if self.fixed_mask else ""
        cmd_to_run = f"{GREEDY_PATH} -d 3 -a -i {re.escape(self.fixed_img)} {re.escape(self.moving_img)} " \
                     f"{mask_cmd} -ia-image-centers -dof 6 -o {re.escape(self.transform_files['rigid'])} " \
                     f"-n {self.multi_resolution_iterations} -m {COST_FUNCTION}"
        subprocess.run(cmd_to_run, shell=True, capture_output=True)
        logging.info(
            f"Rigid alignment: {pathlib.Path(self.moving_img).name} -> {pathlib.Path(self.fixed_img).name} | Aligned image: "
            f"moco-{pathlib.Path(self.moving_img).name} | Transform file: {pathlib.Path(self.transform_files['rigid']).name}")
        return self.transform_files['rigid']

    def affine(self) -> str:
        """
        Perform affine registration between the moving and fixed images.

        Returns:
        --------
        str
            Path to the resulting affine transformation file.
        """
        mask_cmd = f"-gm {re.escape(self.fixed_mask)}" if self.fixed_mask else ""
        cmd_to_run = f"{GREEDY_PATH} -d 3 -a -i {re.escape(self.fixed_img)} {re.escape(self.moving_img)} " \
                     f"{mask_cmd} -ia-image-centers -dof 12 -o {re.escape(self.transform_files['affine'])} " \
                     f"-n {self.multi_resolution_iterations} -m {COST_FUNCTION}"
        subprocess.run(cmd_to_run, shell=True, capture_output=True)
        logging.info(
            f"Affine alignment: {pathlib.Path(self.moving_img).name} -> {pathlib.Path(self.fixed_img).name} |"
            f" Aligned image: moco-{pathlib.Path(self.moving_img).name} | Transform file: {pathlib.Path(self.transform_files['affine']).name}")
        return self.transform_files['affine']

    def deformable(self) -> tuple:
        """
        Perform deformable registration between the moving and fixed images.

        Returns:
        --------
        tuple
            A tuple containing paths to the resulting affine, warp, and inverse warp transformation files.
        """
        self.affine()
        mask_cmd = f"-gm {re.escape(self.fixed_mask)}" if self.fixed_mask else ""
        cmd_to_run = f"{GREEDY_PATH} -d 3 -m {COST_FUNCTION} -i {re.escape(self.fixed_img)} {re.escape(self.moving_img)} " \
                     f"{mask_cmd} -it {re.escape(self.transform_files['affine'])} -o {re.escape(self.transform_files['warp'])} " \
                     f"-oinv {re.escape(self.transform_files['inverse_warp'])} -sv -n {self.multi_resolution_iterations}"
        subprocess.run(cmd_to_run, shell=True, capture_output=True)
        logging.info(
            f"Deformable alignment: {pathlib.Path(self.moving_img).name} -> {pathlib.Path(self.fixed_img).name} | "
            f"Aligned image: moco-{pathlib.Path(self.moving_img).name} | "
            f"Initial alignment: {pathlib.Path(self.transform_files['affine']).name}"
            f" | warp file: {pathlib.Path(self.transform_files['warp']).name}")
        return self.transform_files['affine'], self.transform_files['warp'], self.transform_files['inverse_warp']

    def registration(self, registration_type: str) -> None:
        """
        Register the moving image to the fixed image using the specified registration type.

        Parameters:
        -----------
        registration_type : str
            Type of registration to perform. Supported values are 'rigid', 'affine', and 'deformable'.
        """
        if registration_type == 'rigid':
            self.rigid()
        elif registration_type == 'affine':
            self.affine()
        elif registration_type == 'deformable':
            self.deformable()
        else:
            sys.exit("Registration type not supported!")

    def resample(self, resampled_moving_img: str, registration_type: str, segmentation="", resampled_seg="") -> None:
        """
        Resample the moving image based on the computed transformation.

        Parameters:
        -----------
        resampled_moving_img : str
            Path to save the resampled moving image.
        registration_type : str
            Type of registration used. Supported values are 'rigid', 'affine', and 'deformable'.
        segmentation : str, optional
            Path to the segmentation of the moving image.
        resampled_seg : str, optional
            Path to save the resampled segmentation.
        """
        if registration_type == 'rigid':
            cmd_to_run = self._build_cmd(resampled_moving_img, segmentation, resampled_seg,
                                         self.transform_files['rigid'])
        elif registration_type == 'affine':
            cmd_to_run = self._build_cmd(resampled_moving_img, segmentation, resampled_seg,
                                         self.transform_files['affine'])
        elif registration_type == 'deformable':
            cmd_to_run = self._build_cmd(resampled_moving_img, segmentation, resampled_seg,
                                         self.transform_files['warp'], self.transform_files['affine'])
        subprocess.run(cmd_to_run, shell=True, capture_output=True)

    def _build_cmd(self, resampled_moving_img: str, segmentation: str, resampled_seg: str,
                   *transform_files: str) -> str:
        """
        Build the command for the greedy registration tool.

        Parameters:
        -----------
        resampled_moving_img : str
            Path to save the resampled moving image.
        segmentation : str
            Path to the segmentation of the moving image.
        resampled_seg : str
            Path to save the resampled segmentation.
        *transform_files : str
            Paths to the transformation files used for resampling.

        Returns:
        --------
        str
            The command string to run.
        """
        cmd = f"{GREEDY_PATH} -d 3 -rf {re.escape(self.fixed_img)} -ri LINEAR -rm " \
              f"{re.escape(self.moving_img)} {re.escape(resampled_moving_img)}"
        if segmentation and resampled_seg:
            cmd += f" -ri LABEL 0.2vox -rm {re.escape(segmentation)} {re.escape(resampled_seg)}"
        for transform_file in transform_files:
            cmd += f" -r {re.escape(transform_file)}"
        return cmd


@delayed
def align_single_image(fixed_img, moving_img, registration_type, multi_resolution_iterations, moco_dir):
    aligner = ImageRegistration(fixed_img=fixed_img, multi_resolution_iterations=multi_resolution_iterations)
    aligner.set_moving_image(moving_img)
    aligner.registration(registration_type)
    aligner.resample(resampled_moving_img=os.path.join(moco_dir, constants.MOCO_PREFIX + os.path.basename(moving_img)),
                     registration_type=registration_type)
    return 1


def align(fixed_img=str, moving_imgs=list, registration_type=str, multi_resolution_iterations=str, moco_dir=str):
    """
    Aligns the moving_imgs to fixed_img using the specified registration_type.
    """
    tasks = [
        align_single_image(fixed_img, moving_img, registration_type, multi_resolution_iterations, moco_dir)
        for moving_img in moving_imgs
    ]

    total_images = len(moving_imgs)

    # Initialize the progress bar
    with Progress() as progress:
        task_description = f"[cyan] Aligning moving images to the reference frame [0/{total_images}]"
        task = progress.add_task(task_description, total=total_images)

        # Using dask to compute results and update the progress bar
        for count, _ in enumerate(compute(*tasks), 1):
            progress.update(task, advance=1,
                            description=f"[cyan] Aligning moving images to the reference frame [{count}/{total_images}]")

def get_dimensions(nifti_file: str) -> int:
    """
    Get the dimensions of a NIFTI image file
    :param nifti_file: NIFTI file to check
    """
    nifti_img = sitk.ReadImage(nifti_file)
    img_dim = nifti_img.GetDimension()
    return img_dim


def get_pixel_id_type(nifti_file: str) -> str:
    """
    Get the pixel id type of a NIFTI image file
    :param nifti_file: NIFTI file to check
    """
    nifti_img = sitk.ReadImage(nifti_file)
    pixel_id_type = nifti_img.GetPixelIDTypeAsString()
    return pixel_id_type


def get_intensity_statistics(nifti_file: str, multi_label_file: str) -> object:
    """
    Get the intensity statistics of a NIFTI image file
    :param nifti_file: NIFTI file to check
    :param multi_label_file: Multilabel file that is used to calculate the intensity statistics from nifti_file
    :return: stats_df, a dataframe with the intensity statistics
    """
    nifti_img = sitk.ReadImage(nifti_file)
    multi_label_img = sitk.ReadImage(multi_label_file)
    intensity_statistics = sitk.LabelIntensityStatisticsImageFilter()
    intensity_statistics.Execute(multi_label_img, nifti_img)
    stats_list = [(intensity_statistics.GetMean(i), intensity_statistics.GetStandardDeviation(i),
                   intensity_statistics.GetMedian(i), intensity_statistics.GetMaximum(i),
                   intensity_statistics.GetMinimum(i)) for i in intensity_statistics.GetLabels()]
    columns = ['Mean', 'Standard Deviation', 'Median', 'Maximum', 'Minimum']
    stats_df = pd.DataFrame(data=stats_list, index=intensity_statistics.GetLabels(), columns=columns)
    return stats_df


def get_body_mask(nifti_file: str, mask_file: str) -> str:
    """
    Get time activity curves from a 4d nifti file
    :param nifti_file: 4d nifti file to get the time activity curves from
    :param mask_file: Name of the mask file that is derived from the 4d nifti file.
    :return: path of the mask file
    """
    nifti_masker = NiftiMasker(mask_strategy='epi', memory="nilearn_cache", memory_level=2, smoothing_fwhm=8)
    nifti_masker.fit(nifti_file)
    nibabel.save(nifti_masker.mask_img_, mask_file)
    return mask_file


def mask_img(nifti_file: str, mask_file: str, masked_file: str) -> str:
    """
    Mask a NIFTI image file with a mask file
    :param nifti_file: NIFTI file to mask
    :param mask_file: Mask file to mask the nifti_file with
    :param masked_file: Name of the masked file
    :return: path of the masked nifti file
    """
    img = sitk.ReadImage(nifti_file)
    mask = sitk.ReadImage(mask_file, sitk.sitkFloat32)
    masked_img = sitk.Compose(
        [sitk.Multiply(sitk.VectorIndexSelectionCast(img, i), mask) for i in
         range(img.GetNumberOfComponentsPerPixel())])
    sitk.WriteImage(sitk.Cast(masked_img, sitk.sitkVectorFloat32), masked_file)
    return masked_file


def downscale_image(downscale_param: tuple, input_image: str) -> str:
    """
    Downscales an image based on the shrink factor and writes it to the output directory
    :param downscale_param: output_dir (str), shrink_factor (int) packed in a tuple
    :param input_image: input image to downscale
    :return: path to downscaled image
    """
    output_dir, shrink_factor = downscale_param
    input_image_name = os.path.basename(input_image)
    # Blur the input image first
    input_image_blurred = os.path.join(output_dir, f"{shrink_factor}x_blurred_{input_image_name}")
    gauss_variance = (shrink_factor / 2) ** 2
    gauss_variance = int(gauss_variance)
    cmd_to_smooth = f"{C3D_PATH} {re.escape(input_image)} -smooth-fast {gauss_variance}x{gauss_variance}x{gauss_variance}vox -o" \
                    f" {re.escape(input_image_blurred)} "
    subprocess.run(cmd_to_smooth, shell=True, capture_output=False)
    # Resample the smoothed input image later
    input_image_downscaled = os.path.join(output_dir, f"{shrink_factor}x_downscaled_{input_image_name}")
    shrink_percentage = str(int(100 / shrink_factor))
    cmd_to_downscale = f"{C3D_PATH} {re.escape(input_image_blurred)} -resample {shrink_percentage}x{shrink_percentage}x" \
                       f"{shrink_percentage}% -o {re.escape(input_image_downscaled)}"
    subprocess.run(cmd_to_downscale, shell=True, capture_output=False)
    return input_image_downscaled


# Calculate the mean intensity of an image using SimpleITK
def calc_mean_intensity(image: str) -> float:
    """
    Calculates the mean intensity of an image using SimpleITK
    :param image: path to the image
    :return: mean intensity of the image
    :rtype: float
    """
    image = sitk.ReadImage(image, sitk.sitkFloat32)
    return sitk.GetArrayFromImage(image).mean()


def calc_voxelwise_ncc_images(image1: str, image2: str, output_dir: str) -> str:
    """
    Calculates voxelwise normalized cross correlation between two images and writes it to the output directory
    :param image1: path to the first image
    :param image2: path to the second image
    :param output_dir: path to the output directory
    :return: path to the voxelwise ncc image
    """
    # get the image names without the extension '.nii.gz'
    image1_name = os.path.basename(image1).split(".")[0]
    image2_name = os.path.basename(image2).split(".")[0]
    output_image = os.path.join(output_dir, f"ncc_{image2_name}.nii.gz")
    c3d_cmd = f"{C3D_PATH} {re.escape(image1)} {re.escape(image2)} -ncc {NCC_RADIUS} -o {re.escape(output_image)}"
    subprocess.run(c3d_cmd, shell=True, capture_output=False)
    # clip the negative correlations to zero
    c3d_cmd = f"{C3D_PATH} {re.escape(output_image)} -clip 0 inf -o {re.escape(output_image)}"
    subprocess.run(c3d_cmd, shell=True, capture_output=False)
    return output_image


def determine_candidate_frames(candidate_files: list, reference_file: str, output_dir: str, njobs: int) -> int:
    """
    Determines the candidate frames of a 4D PET series on which motion correction can be performed effectively
    :param candidate_files: list of 3D candidate moving PET files
    :param reference_file: path to the reference PET file
    :param output_dir: path to the parent directory of the candidate files
    :param njobs: number of jobs to run in parallel
    :return:  Index of the starting frame from which motion correction can be performed
    :rtype: int
    """
    # Get the parent directory for pet_files
    falcon_dir = output_dir

    # Create the folder to dump the ncc images
    ncc_dir = os.path.join(falcon_dir, "ncc-images")
    fop.create_directory(ncc_dir)

    # using mpire to run the ncc calculation in parallel
    with WorkerPool(njobs) as pool:
        ncc_images = pool.map(calc_voxelwise_ncc_images, [(reference_file, file, ncc_dir) for file in candidate_files])

    ncc_images = fop.get_files(ncc_dir, "ncc_*.nii.gz")
    # calculate the mean intensity of files in the ncc folder and store it as mean_intensities
    mean_intensities = [calc_mean_intensity(ncc_image) for ncc_image in ncc_images]
    # calculate the average value of the top 3 mean intensities
    max_observed_ncc = sum(sorted(mean_intensities, reverse=True)[:3]) / 3
    # Identify the indices of the frames with mean intensity greater than NCC_THRESHOLD * max_observed_ncc
    candidate_frames = [i for i, mean_intensity in enumerate(mean_intensities) if
                        mean_intensity > NCC_THRESHOLD * max_observed_ncc]
    # return the filenames corresponding to the candidate frames
    return candidate_files[candidate_frames[0]]
