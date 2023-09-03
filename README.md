
<p align="center">
<img src="https://github.com/LalithShiyam/FALCON/blob/main/Images/Falcon-logo.png">

</p>

## 🦅 About FALCON V2
[![Documentation Status](https://readthedocs.org/projects/falconz/badge/?version=latest)](https://falconz.readthedocs.io/en/latest/?badge=latest) [![PyPI version](https://badge.fury.io/py/falconz.svg)](https://pypi.org/project/falconz/) ![Downloads](https://img.shields.io/pypi/dm/falconz?color=ff69b4) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![Discord](https://img.shields.io/badge/Discord-Join%20Chat-800080.svg?logo=discord&logoColor=white)](https://discord.gg/Q7ge3psMT9) [![YouTube](https://img.shields.io/badge/YouTube-MoCo%20Action-FF0000?logo=youtube&logoColor=white)](https://www.youtube.com/playlist?list=PLZQERorVWrbeNKLOdJMDi4lARvaK3ceeO)

FALCON V2 (Fast Algorithms for motion correction) is an advanced, fully-automatic tool for motion correction in dynamic total-body or whole-body PET imaging. Designed with flexibility and reliability at its core, it's now even more versatile, capable of operating across various operating systems and architectures. 🚀

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/QIMP-Team/FALCON/blob/main/Images/Falcon_story_darkmode.gif" width="500" height="500">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/QIMP-Team/FALCON/blob/main/Images/Falcon_Story_Gif.GIF" width="500" height="500">
  <img alt="Shows an illustrated MOOSE story board adopted to different themes" src="https://github.com/QIMP-Team/FALCON/blob/main/Images/white_moco.gif">
</picture>
</div>

### 🌟 Major Features

- **Python-Powered**: As a Python package, FALCON V2 is compatible with Python 3.9 and beyond, making it a seamless integration into modern workflows. 🐍
- **Cross-Platform Support**: No matter if you're on Linux, Windows, or Mac, FALCON V2 ensures a smooth experience across the board. 💻🖥️
- **Universal Architecture Compatibility**: Engineered for flexibility, FALCON V2 runs flawlessly on x86, ARM, or even the latest M1 Silicon chips. 🛠️
- **Optimized for Out-of-Core Computing**: With the power of Dask, FALCON V2 achieves efficient out-of-core computing, maximizing CPU utilization while minimizing memory overhead for both speed and performance. 🚀
- **Versatile Application**: Designed to be truly universal, FALCON V2 works across any region, any tracer, and any modality, making it your one-stop solution for all diagnostic and analytical needs. 🌍🔬

  
## 🚀 FALCON's motion correction in action

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/QIMP-Team/FALCON/blob/main/Images/black_moco.gif">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/QIMP-Team/FALCON/blob/main/Images/white_moco.gif" width="350" height="500">
  <img alt="Shows an illustrated MOOSE story board adopted to different themes" src="https://github.com/QIMP-Team/FALCON/blob/main/Images/white_moco.gif">
</picture>
</div>

In this analysis, we are examining the mean image of 20 dynamic frames of a 68Ga-PSMA study both before and after motion correction. By comparing the two mean images, we can clearly see the significant improvement that results from motion correction. The mean image after motion correction appears noticeably sharper and more defined than the one before correction.
## 🛠 Installation Guide

### Virtual Environment Setup

Creating a virtual environment is highly recommended to avoid any potential conflicts with other Python packages.

- **Windows**:
  ```bash
  python -m venv falconz_env
  .\falconz_env\Scripts\activate
  ```

- **Linux/Mac**:
  ```bash
  python3 -m venv falconz_env
  source falconz_env/bin/activate
  ```

### Installing FALCON V2

With your virtual environment activated, install FALCON V2 using pip:

```bash
pip install falconz
```

## 🚀 Usage

FALCON supports DICOM, Nifti, Analyze, and Metaimage file formats, whether it's a single 4D image or multiple 3D images. Simply specify the directory where the files are located and indicate the registration type. FALCON will take care of the rest.

To use FALCON, use the following syntax:
```
falconz -d path_to_4d_images -r <rigid | affine | deformable> -i <number_of_iterations_per_level> -sf <starting_frame_from_which_moco_should_be_performed> -rf <reference_frame>
```

Here's an example of using FALCON in Pro mode:
```
falconz -d /Documents/Sub001 -r deformable -i 100x50x25 -sf 0 -rf -1
```
In this example, FALCON is performing deformable registration with 100, 50, and 25 iterations at each level of the multi-scale registration. The registration starts from the 1st frame and uses the last frame as the reference.

Here's an example of using FALCON in lazy mode:
```
falconz -d /Documents/Sub001 -r deformable # for whole-body registration
falconz -d /Documents/Sub001 -r rigid # for brain only studies (much faster processing)
```
We also offer a specialized 🚀 Dash mode, engineered for rapid motion correction across total-body datasets. Execute complex whole-body registration tasks at unprecedented speeds ⚡ with a simple command! 👩‍💻👨‍💻
```
falconz -d /Documents/Sub001 -r deformable -m dash # for high-velocity whole-body registration
```
As shown above, you don't need to specify many additional parameters. The rest of the parameters are either inferred or set automatically based on common standards.

⚠️ **Note**:
If you're not satisfied with the 'inferred' start frame, you can always set it on your own (the internal threshold is set to be quite safe). Refer to the manuscript for more information.

If you need help with FALCON or want to review the command-line options, use:
```
falconz --help
```
Please note that the number of iterations is specified as a string of values separated by 'x' in the `-i` option. For example, to perform 50 iterations at each level, you would use `-i 50x50x50`.

🗂 **Required Folder Structure**:

FALCON only requires the dynamic PET images of a subject. Once the path is set, along with the minimalistic arguments, FALCON takes care of the rest.

Here's an example of the required folder structure:
```
└── PET_WB_DYNAMIC_(QC)_0005  # Main folder containing the dynamic PET images to motion correct
    └── XXX.dcm or XXX.ima or XXX.mha or XXX.nii.gz or XXX.img/hdr
```
In the example above, the main folder contains the dynamic PET images to be motion corrected. The input images can be DICOM, Nifti, Analyze, or Metaimage files, and they can be either a single 4D image or multiple 3D images.

## 🗂 Resultant Folder Structure

Upon successful execution, FALCON auto-generates an organized output directory, positioned at the same hierarchical level as your original dynamic PET image folder. This dedicated directory carries a unique naming schema that incorporates 'FALCONZ', the version number, and a timestamp for easy identification.

Here's a snapshot of the output folder structure:

```
FALCONZ-V02-2023-09-03-17-28-17/  # Automatically generated results folder
├── Motion-corrected-images       # Corrected dynamic PET images
├── ncc-images                    # Normalized Cross-Correlation images for start frame identification
├── Split-Nifti-files             # Individual 3D Nifti files
└── transforms                    # Transformation data for motion correction
```

### Folder Components

#### 🖼️ Motion-corrected-images
This is where you'll find the final dynamic PET images, now refined through motion correction procedures. 🌟

#### 📊 ncc-images
A collection of Normalized Cross-Correlation images—these serve as essential tools 🛠️ for determining the most appropriate start frame for motion correction.

#### 📁 Split-Nifti-files
This folder contains individual 3D Nifti files, which are crucial 🗝️ for conducting the motion correction operations.

#### 🔄 transforms
This section archives the warp fields in cases of deformable registration and the transformation matrices 📐 for rigid or affine registrations, allowing for transparency and potential reusability of these parameters.

FALCON doesn't just deliver high-precision motion-corrected images; it also provides a comprehensive, organized output structure 🗂️ designed for immediate utility and future analysis. 🚀




## ❤️ Citations

If you find FALCON useful, please consider citing the following publications:

```plaintext
1. Lalith Kumar Shiyam Sundar, et al. “Fully-automated, fast motion correction of dynamic whole and total-body PET/CT imaging studies.” JNM, 2023.
2. Gutschmayer S, et al. “A scale space theory based motion correction approach for dynamic PET brain imaging studies.” Frontiers in Physics, vol. 10, 2022.
3. Venet L, et al. “Accurate and Robust Alignment of Differently Stained Histologic Images Based on Greedy Diffeomorphic Registration.” Appl Sci, vol. 11, 2021.
```
Thank you for choosing FALCON V2. Let's soar to new heights together! 🦅
