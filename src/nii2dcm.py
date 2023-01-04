import argparse
import os
import pathlib

import SimpleITK as sitk
import numpy as np
import pydicom as dicom
from pydicom.uid import generate_uid
from tqdm import tqdm

import fileOp as fop

# Inputs

dicom_dir = '/Users/lalithsimac/Downloads/Fluciclovine_11Subs_Batch1/147006_Sub0203_DD/pet'
nifti_dir = '/Users/lalithsimac/Downloads/Fluciclovine_11Subs_Batch1/147006_Sub0203_DD/moco_nifti'
out_dir = '/Users/lalithsimac/Downloads/Fluciclovine_11Subs_Batch1/147006_Sub0203_DD/dcm_pt_nii'


# Local functions

# function to display the maximum and minimum intensity of the nifti file
def display_nii_min_max(nifti_file_3d: str):
    """
    Displays the maximum and minimum intensity of the nifti file
    :param nifti_file_3d: Path to the 3d nifti file
    """
    nii_img = sitk.ReadImage(nifti_file_3d, sitk.sitkFloat32)
    nii_array = sitk.GetArrayFromImage(nii_img)
    print(f"Minimum intensity of nifti file: {np.min(nii_array)}")
    print(f"Maximum intensity of nifti file: {np.max(nii_array)}")


# Function push 3d nifti pixel data to dicom files

def push_nii_pixel_data_to_dcm(nifti_file_3d: str, dicom_files: list, out_dir: str, series_uid) -> str:
    """
    Pushes the pixel data from a nifti file to the DICOM files in a directory. The DICOM tags are preserved while the
    pixel data is replaced.
    :param nifti_file_3d: Path to the 3d nifti file
    :param dicom_files: List of dicom files to which the 3d nifti file needs to be pushed
    :param out_dir: Path to the output directory
    :param series_uid: Series UID to be used for the output DICOM files
    :return out_dir: Path to the output directory
    """
    print("Reading nifti file as float 32...")
    nii_img = sitk.ReadImage(nifti_file_3d, sitk.sitkFloat32)
    print("Flipping the nifti image to match the dicom orientation...")
    nii_img = sitk.Flip(nii_img, [False, True, True])
    nii_array = sitk.GetArrayFromImage(nii_img)
    if np.shape(nii_array)[0] != len(dicom_files):
        raise Exception("Number of slices in nifti file and dicom directory do not match")
    counter = 0
    for dicom_file in tqdm(dicom_files):
        dcm = dicom.read_file(dicom_file)
        dicom_file_name = pathlib.Path(dicom_file).name
        # inverse rescale slope and intercept
        nii_array[counter, :, :] = np.subtract(nii_array[counter, :, :], int(dcm.RescaleIntercept))
        nii_array[counter, :, :] = np.divide(nii_array[counter, :, :], dcm.RescaleSlope,
                                             out=np.zeros_like(nii_array[counter, :, :]),
                                             where=dcm.RescaleSlope != 0)
        
        # map the intensity to the range between 0 and 65535
        # nii_array[counter, :, :] = np.subtract(nii_array[counter, :, :], np.min(nii_array[counter, :, :]))
        # nii_array[counter, :, :] = np.divide(nii_array[counter, :, :], np.max(nii_array[counter, :, :]))
        # nii_array[counter, :, :] = np.multiply(nii_array[counter, :, :], 65535)
        # nii_array[counter, :, :] = np.round(nii_array[counter, :, :])
        dcm.PixelData = nii_array[counter, :, :].astype(dcm.pixel_array.dtype).tobytes()
        dcm.SeriesDescription = "Motion corrected by FALCON v0.1 [QIMP]"
        # set the new series UID
        dcm.SeriesInstanceUID = series_uid
        dcm.save_as(os.path.join(out_dir, dicom_file_name))
        counter += 1

    print(f"Pushing pixel data from {nifti_file_3d} to dicom files complete!")

    return out_dir


dicom_files = fop.get_files(dicom_dir, wildcard='*.IMA')
if len(dicom_files) == 0:
    dicom_files = fop.get_files(dicom_dir, wildcard='*.dcm')

# get the number of slices in each 3d frame
z_dim = int(dicom.dcmread(dicom_files[0]).get('NumberOfSlices'))

# sort the dicom files by ImageIndex and AcquisitionTime
dicom_files.sort(key=lambda x: (dicom.dcmread(x).get('ImageIndex'), dicom.dcmread(x).get('AcquisitionTime')))

# Isolate the 4d dicom files into a list of 3d dicom files using the z_dim

dicom_files_3d = [dicom_files[i:i + z_dim] for i in range(0, len(dicom_files), z_dim)]

# Read the 3d nifti files
nifti_files = fop.get_files(nifti_dir, wildcard='*.nii*')
# nifti_files.reverse()

# push 3d nifti pixel data to dicom files
series_uid = generate_uid()
for i in range(len(nifti_files)):
    push_nii_pixel_data_to_dcm(nifti_files[i], dicom_files_3d[i], os.path.join(out_dir), series_uid)


