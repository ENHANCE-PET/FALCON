#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ***********************************************************************************************************************
# File: imageOP.py
# Project: falcon
# Created: 27.01.2022
# Author: Lalith Kumar Shiyam Sundar
# Email: Lalith.Shiyamsundar@meduniwien.ac.at
# Institute: Quantitative Imaging and Medical Physics, Medical University of Vienna
# Description: Falcon (FALCON) is a tool for the performing dynamic PET motion correction. It is based on the greedy
# algorithm developed by the Paul Yushkevich. The algorithm is capable of performing fast rigid/affine/deformable
# registration.
# License: Apache 2.0
# **********************************************************************************************************************
import subprocess

import SimpleITK
import nibabel
import pandas as pd
from nilearn.input_data import NiftiMasker
import fileOP as fop

def get_dimensions(nifti_file: str) -> int:
    """
    Get the dimensions of a NIFTI image file
    :param nifti_file: NIFTI file to check
    """
    nifti_img = SimpleITK.ReadImage(nifti_file)
    img_dim = nifti_img.GetDimension()
    return img_dim


def get_pixel_id_type(nifti_file: str) -> str:
    """
    Get the pixel id type of a NIFTI image file
    :param nifti_file: NIFTI file to check
    """
    nifti_img = SimpleITK.ReadImage(nifti_file)
    pixel_id_type = nifti_img.GetPixelIDTypeAsString()
    return pixel_id_type


def get_intensity_statistics(nifti_file: str, multi_label_file: str) -> object:
    """
    Get the intensity statistics of a NIFTI image file
    :param nifti_file: NIFTI file to check
    :param multi_label_file: Multilabel file that is used to calculate the intensity statistics from nifti_file
    :return: stats_df, a dataframe with the intensity statistics
    """
    nifti_img = SimpleITK.ReadImage(nifti_file)
    multi_label_img = SimpleITK.ReadImage(multi_label_file)
    intensity_statistics = SimpleITK.LabelIntensityStatisticsImageFilter()
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
    img = SimpleITK.ReadImage(nifti_file)
    mask = SimpleITK.ReadImage(mask_file, SimpleITK.sitkFloat32)
    masked_img = SimpleITK.Compose(
        [SimpleITK.Multiply(SimpleITK.VectorIndexSelectionCast(img, i), mask) for i in
         range(img.GetNumberOfComponentsPerPixel())])
    SimpleITK.WriteImage(SimpleITK.Cast(masked_img, SimpleITK.sitkVectorFloat32), masked_file)
    return masked_file


def get_average_warps(warp_dir: str, w_card: str, out_dir: str = None) -> sitk.Image:
    """
    Computes the average of multiple warp images. The images must be multi-component ones.

    :rtype: sitk.Image
    :param warp_dir: 
    :param w_card: 
    :param out_dir: 
    :return: The average multi-component warp image.
    """
    image_paths = fop.get_files(warp_dir, w_card)

    print(f"Starting with {image_paths[0]}")
    summed_image = sitk.ReadImage(image_paths[0], sitk.sitkVectorFloat64)

    # Sum all other images
    for image_index in range(1, len(image_paths)):
        print(f"       Adding {image_paths[image_index]} to the image stack.")
        current_image = sitk.ReadImage(image_paths[image_index], sitk.sitkVectorFloat64)
        summed_image = summed_image + current_image

    # Compute the mean
    number_of_images = len(image_paths)
    avg_val = 1 / number_of_images
    average_image = sitk.Compose([sitk.VectorIndexSelectionCast(summed_image, i) * avg_val for i in
                                  range(summed_image.GetNumberOfComponentsPerPixel())])

    if out_dir is not None:
        sitk.WriteImage(average_image, os.path.join(out_dir, "average_warp.nii.gz"))
    return average_image


def get_magnitude_warp(input_warp_path: str, magnitude_warp_path: str = None) -> sitk.Image:
    """
    Computes the voxel wise magnitude of a multi-component warp image.

    :rtype: sitk.Image
    :param input_warp_path: The path to the warp image
    :param magnitude_warp_path: The (optional) desired path where the magnitude image will be stored
    :return: The magnitude image.
    """
    # Read multi component image
    image = sitk.ReadImage(input_warp_path, sitk.sitkVectorFloat64)
    # Compute magnitude image
    magnitude_image = sitk.VectorMagnitude(image)
    # Write to location is specified
    if magnitude_warp_path is not None:
        sitk.WriteImage(magnitude_image, magnitude_warp_path)
    return magnitude_image


def get_mean_std_magnitude(magnitude_dir: str, w_card: str, out_dir: str = None) -> (sitk.Image, sitk.Image):
    """
    Computes the mean and std of multiple magnitude images. The images must be single-component ones.

    :rtype: (sitk.Image, sitk.Image)
    :param magnitude_dir: The directory where all magnitude images are located
    :param w_card: The pattern to retrieve the magnitude images from the folder at magnitude_dir
    :param out_dir: The (optional) desired path where the mean and std image will be stored.
    :return: The mean and the std image.
    """
    image_paths = fop.get_files(magnitude_dir, w_card)

    # Compute the mean
    print(f"Computing the Mean")
    print(f"Starting with {image_paths[0]}")
    summed_image = sitk.ReadImage(image_paths[0])

    # Sum all other images
    for image_index in range(1, len(image_paths)):
        print(f"       Adding {image_paths[image_index]} to the image stack.")
        current_image = sitk.ReadImage(image_paths[image_index])
        summed_image = summed_image + current_image

    number_of_images = len(image_paths)
    avg_val = 1 / number_of_images
    mean_image = summed_image * avg_val

    # Compute the STD
    print(f"Computing the STD.")
    print(f"Starting with {image_paths[0]}")
    diff_image = sitk.ReadImage(image_paths[0]) - mean_image
    summed_image = diff_image * diff_image

    # Process all other images
    for image_index in range(1, len(image_paths)):
        print(f"       Adding {image_paths[image_index]} to the image stack.")
        diff_image = sitk.ReadImage(image_paths[0]) - mean_image
        summed_image = summed_image + diff_image
    std_image = pow(summed_image * 1 / number_of_images, 1/2)

    if out_dir is not None:
        print(f"Writing mean and std image at {out_dir}.")
        sitk.WriteImage(mean_image, os.path.join(out_dir, "mean_warp.nii.gz"))
        sitk.WriteImage(std_image, os.path.join(out_dir, "std_warp.nii.gz"))

    return mean_image, std_image


def get_mean_std_magnitude_warps(input_directory: str, wildcard: str = "*warp.nii.gz") -> (sitk.Image, sitk.Image):
    """
    Computes a magnitude image for each file that is matched by wildcard in input_directory together with the mean 
    and std of all images. 

    :rtype: (sitk.Image, sitk.Image)
    :param input_directory: The path to the directory where all warps are located
    :param wildcard: The pattern to retrieve the magnitude images from the folder at input_directory
    :return: The mean and std image.
    """
    # Get files
    files = fop.get_files(input_directory, wildcard)

    # Get magnitude for each file
    for file in files:
        magnitude_file_name = os.path.basename(file)
        print(f"Computing magnitude image ({magnitude_file_name}) for {file}")
        get_magnitude_warp(file, os.path.join(input_directory, f"{magnitude_file_name}_magnitude.nii.gz"))

    # Get mean and std magnitude images
    mean_magnitude, std_magnitude = get_mean_std_magnitude(input_directory, "*_magnitude.nii.gz", input_directory)
    return mean_magnitude, std_magnitude
