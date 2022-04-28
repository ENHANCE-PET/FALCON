#!/usr/bin/env python
# -*- coding: utf-8 -*-

import SimpleITK
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
import pandas as pd


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

