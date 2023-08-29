
<p align="center">
<img src="https://github.com/LalithShiyam/FALCON/blob/main/Falcon-logo.png">

</p>

## 🦅 About FALCON V2
[![Documentation Status](https://readthedocs.org/projects/falconz/badge/?version=latest)](https://falconz.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/falconz.svg)](https://pypi.org/project/falconz/) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

FALCON V2 (Fast Algorithms for motion correction) is an advanced, fully-automatic tool for motion correction in dynamic total-body or whole-body PET imaging. Designed with flexibility and reliability at its core, it's now even more versatile, capable of operating across various operating systems and architectures. 🚀

### 🌟 Major Features

- **Cross-Platform Support**: Whether you're on Linux, Windows, or Mac, FALCON V2 has got you covered. 
- **Universal Architecture Compatibility**: Run FALCON V2 seamlessly on x86, ARM, or even the latest M1 Silicon.
- **Python-Powered**: As a Python package, FALCON V2 is compatible with Python 3.9 and beyond, ensuring smooth integration into modern workflows.
- **Versatile Application**: FALCON V2 is designed to work for any region, any tracer, and any modality, making it truly universal for all your diagnostic and analytical needs.

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
falcon -m path_to_4d_images -r <rigid | affine | deformable> -i <number_of_iterations_per_level> -sf <starting_frame_from_which_moco_should_be_performed> -rf <reference_frame>
```

Here's an example of using FALCON in Pro mode:
```
falcon -m /Documents/Sub001 -r deformable -i 100x50x25 -sf 0 -rf -1
```
In this example, FALCON is performing deformable registration with 100, 50, and 25 iterations at each level of the multi-scale registration. The registration starts from the 1st frame and uses the last frame as the reference.

Here's an example of using FALCON in lazy mode:
```
falcon -m /Documents/Sub001 -r deformable # for whole-body registration
falcon -m /Documents/Sub001 -r rigid # for brain only studies (much faster processing)
```
As shown above, you don't need to specify many additional parameters. The rest of the parameters are either inferred or set automatically based on common standards.

⚠️ **Note**:
If you're not satisfied with the 'inferred' start frame, you can always set it on your own (the internal threshold is set to be quite safe). Refer to the manuscript for more information.

If you need help with FALCON or want to review the command-line options, use:
```
falcon --help
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

## ❤️ Citations

If you find our work useful, kindly cite the following articles:

**Total-body studies evaluation (FALCON)**:
```plaintext
Lalith Kumar Shiyam Sundar, et al. “Fully-automated, fast motion correction of dynamic whole and total-body PET/CT imaging studies.” JNM, 2023.
```

**Brain studies evaluation (FALCON)**:
```plaintext
Gutschmayer S, et al. “A scale space theory based motion correction approach for dynamic PET brain imaging studies.” Frontiers in Physics, vol. 10, 2022.
```

**Greedy registration**:
```plaintext
Venet L, et al. “Accurate and Robust Alignment of Differently Stained Histologic Images Based on Greedy Diffeomorphic Registration.” Appl Sci, vol. 11, 2021.
```






Thank you for choosing FALCON V2. Let's soar to new heights together! 🦅
