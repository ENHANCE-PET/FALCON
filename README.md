
<p align="center">
<img src="https://github.com/LalithShiyam/FALCON/blob/main/Images/Falcon-logo.png">

</p>

## 🦅 About FALCON 2.0
[![PyPI version](https://img.shields.io/pypi/v/falconz?color=FF1493&style=flat-square&logo=pypi)](https://pypi.org/project/falconz/) [![Documentation Status](https://readthedocs.org/projects/falconz/badge/?version=latest)](https://falconz.readthedocs.io/en/latest/?badge=latest) [![Monthly Downloads](https://img.shields.io/pypi/dm/falconz?label=Downloads%20(Monthly)&color=9400D3&style=flat-square&logo=python)](https://pypi.org/project/falconz/) [![Daily Downloads](https://img.shields.io/pypi/dd/falconz?label=Downloads%20(Daily)&color=9400D3&style=flat-square&logo=python)](https://pypi.org/project/falconz/)[![Discord](https://img.shields.io/badge/Discord-Join%20Chat-800080.svg?logo=discord&logoColor=white)](https://discord.gg/Q7ge3psMT9) [![YouTube](https://img.shields.io/badge/YouTube-MoCo%20Action-FF0000?logo=youtube&logoColor=white)](https://www.youtube.com/playlist?list=PLZQERorVWrbeNKLOdJMDi4lARvaK3ceeO)

FALCON V2 (Fast Algorithms for motion correction) is an advanced, fully-automatic tool for motion correction in dynamic total-body or whole-body PET imaging. Designed with flexibility and reliability at its core, it's now even more versatile, capable of operating across various operating systems and architectures. 🚀

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/QIMP-Team/FALCON/blob/main/Images/Falcon_story_darkmode.gif" width="500" height="500">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/QIMP-Team/FALCON/blob/main/Images/Falcon_Story_Gif.GIF" width="500" height="500">
  <img alt="Shows an illustrated MOOSE story board adopted to different themes" src="https://github.com/QIMP-Team/FALCON/blob/main/Images/white_moco.gif">
</picture>
</div>

### 🌟 Major Features

- **🐍 Now Python-Powered for Effortless Integration**: Say goodbye to cumbersome shell scripts! FALCON V2 is now a Python package, offering seamless compatibility with Python 3.9 and beyond. Integrate it effortlessly into your modern workflows and enjoy the unparalleled convenience.
- **💻🖥️ Unveiling Cross-Platform Freedom**: Break free from the Linux-only limitations! FALCON V2 now extends its robust support to Windows and Mac as well. A seamless, uniform experience across all platforms is no longer a wish—it's a reality!
- **🛠️ Universal Architecture Compatibility with a Twist**: Think you've seen FALCON V2 at its best? Wait until you experience it on ARM architecture! While designed to operate seamlessly on x86 and the latest M1 Silicon, it's on ARM where FALCON V2 truly soars. Prepare to be blown away by unparalleled performance!
- **🚀 Say Goodbye to Memory Woes and Server Farms**: Forget about expensive, beefy servers and memory constraints. With FALCON V2's optimized out-of-core computing, powered by Dask, we've redefined efficiency. Get ready to experience unparalleled speed and performance without breaking the bank or your system's RAM!
- **🌍🔬 The Ultimate Flex: Versatility Reimagined**: For the first time ever, a tool that knows no boundaries—meet FALCON V2. Whether you're dealing with any region, tracer, or modality, FALCON V2 is the only tool you'll ever need for your diagnostic and analytical adventures. Say goodbye to specialized solutions; this is the new standard - thanks to the amazing 'greedy' registration library!

## ❤️ Citations

If you find FALCON useful, please cite the following publications:

- Sundar, L. K. S., Lassen, M. L., Gutschmayer, S., Ferrara, D., Calabrò, A., Yu, J., Kluge, K., Wang, Y., Nardo, L., Hasbak, P., Kjaer, A., Abdelhafez, Y. G., Wang, G., Cherry, S. R., Spencer, B. A., Badawi, R. D., Beyer, T., & Muzik, O. (2023). Fully Automated, Fast Motion Correction of Dynamic Whole-Body and Total-Body PET/CT Imaging Studies. Journal of Nuclear Medicine: Official Publication, Society of Nuclear Medicine. https://doi.org/10.2967/jnumed.122.265362
- Gutschmayer, S., Muzik, O., Chalampalakis, Z., Ferrara, D., Yu, J., Kluge, K., Rausch, I., Boellaard, R., Golla, S. S. V., Zuehlsdorff, S., Newiger, H., Beyer, T., & Kumar Shiyam Sundar, L. (2022). A scale space theory based motion correction approach for dynamic PET brain imaging studies. Frontiers of Physics, 10. https://doi.org/10.3389/fphy.2022.1034783
- Venet, L., Pati, S., Feldman, M. D., Nasrallah, M. P., Yushkevich, P., & Bakas, S. (2021). Accurate and Robust Alignment of Differently Stained Histologic Images Based on Greedy Diffeomorphic Registration. APPS. Applied Sciences, 11(4). https://doi.org/10.3390/app11041892


## Star History 🤩

<a href="https://star-history.com/#QIMP-Team/FALCON&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ENHANCE-PET/FALCON&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ENHANCE-PET/FALCON&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=ENHANCE-PET/FALCON&type=Date" />
  </picture>
</a>

  
## 🚀 FALCON's motion correction in action

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/QIMP-Team/FALCON/blob/main/Images/black_moco.gif">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/QIMP-Team/FALCON/blob/main/Images/white_moco.gif">
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
pip install falconz # stable recommended version
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

### Required Folder Structure

FALCON accepts the following file formats for dynamic PET images: `.dcm`, `.ima`, `.nii`, `.nii.gz`, and `.img/hdr`.

Here are some examples to illustrate the accepted folder structures:

1. **For a bunch of DICOM (.dcm) or IMA (.ima) files:**

    ```
    └── PET_WB_DYNAMIC_(QC)_0005  
        ├── XXX_1.dcm
        ├── XXX_2.dcm
        └── ...
    ```

2. **For a single 4D Nifti (.nii or .nii.gz) file:**

    ```
    └── PET_WB_DYNAMIC_(QC)_0005  
        └── XXX.nii.gz
    ```

3. **For a bunch of 3D Nifti (.nii or .nii.gz) files:**

    ```
    └── PET_WB_DYNAMIC_(QC)_0005  
        ├── XXX_1.nii.gz
        ├── XXX_2.nii.gz
        └── ...
    ```

4. **For Analyze (.img/hdr) files:**

    ```
    └── PET_WB_DYNAMIC_(QC)_0005  
        ├── XXX.img
        ├── XXX.hdr
        └── ...
    ```

The main folder, `PET_WB_DYNAMIC_(QC)_0005`, should contain the dynamic PET images to be motion corrected.


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

## ❓ Frequently Asked Questions

Before raising an issue, check out our growing [Frequently Asked Questions]([./path/to/faq.md](https://github.com/ENHANCE-PET/FALCON/blob/main/Q%26A.md)) section.

## 👥 Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/LalithShiyam"><img src="https://github.com/LalithShiyam.png?s=100" width="100px;" alt="Lalith Kumar Shiyam Sundar"/><br /><sub><b>Lalith Kumar Shiyam Sundar</b></sub></a><br /><a href="https://github.com/ENHANCE-PET/FALCON/commits?author=LalithShiyam" title="Code">💻</a> <a href="https://github.com/ENHANCE-PET/FALCON/commits?author=LalithShiyam" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Keyn34"><img src="https://github.com/Keyn34.png?s=100" width="100px;" alt="Sebastian Gutschmayer"/><br /><sub><b>Sebastian Gutschmayer</b></sub></a><br /><a href="https://github.com/ENHANCE-PET/FALCON/commits?author=Keyn34" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/christanmod"><img src="https://avatars.githubusercontent.com/u/54258479?v=4?s=100" width="100px;" alt="Z.K Li"/><br /><sub><b>Z.K Li</b></sub></a><br /><a href="https://github.com/ENHANCE-PET/FALCON/commits?author=christanmod" title="Documentation">📖</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->


