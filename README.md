<p align="center">
<img src="https://github.com/LalithShiyam/FALCON/blob/main/Images/Falcon-logo.png">
</p>

## 🦅 About FALCON

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/QIMP-Team/FALCON/blob/main/Images/Falcon_story_darkmode.gif" width="500" height="500">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/QIMP-Team/FALCON/blob/main/Images/Falcon_Story_Gif.GIF" width="500" height="500">
  <img alt="Shows an illustrated MOOSE story board adopted to different themes" src="https://github.com/QIMP-Team/FALCON/blob/main/Images/white_moco.gif">
</picture>
</div>


FALCON (Fast Algorithms for motion correction) is a fully-automatic and powerful tool for performing accurate motion correction in dynamic total-body or whole-body PET imaging. Unlike many existing solutions, FALCON is designed to be vendor, tracer, and organ independent, making it a flexible and reliable choice for a wide range of applications.

Built on top of the fast and efficient greedy registration toolkit, FALCON leverages cutting-edge algorithms to quickly and accurately correct for motion artifacts and improve the quality of PET images. With FALCON, researchers and clinicians can obtain clearer, more reliable results, even in challenging imaging scenarios.

FALCON is fully-automatic, which means it requires minimal user input and can be easily integrated into existing workflows. We believe FALCON is an essential tool for anyone working with dynamic brain, total-body or whole-body PET imaging, and we hope you'll find it as useful as we do. If you appreciate the work we've put into FALCON, please consider leaving a star on our GitHub repository. Your feedback and support are greatly appreciated.

Whether you're working in research, clinical care, or industry, FALCON is the ideal choice for dynamic total-body or whole-body PET imaging motion correction. Try it today and experience the benefits of state-of-the-art image processing technology.

### 🚀 FALCON's motion correction in action

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/QIMP-Team/FALCON/blob/main/Images/black_moco.gif">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/QIMP-Team/FALCON/blob/main/Images/white_moco.gif">
  <img alt="Shows an illustrated MOOSE story board adopted to different themes" src="https://github.com/QIMP-Team/FALCON/blob/main/Images/white_moco.gif">
</picture>
</div>

In this analysis, we are examining a mean image of 20 dynamic frames of a 68Ga-PSMA study both before and after motion correction. By comparing the two mean images, we can clearly see the significant improvement that results from motion correction. The mean image after motion correction appears noticeably sharper and more defined than the one before correction.

## ⛔️ Hard requirements 

To run FALCON, you'll need a system running Linux OS (e.g.Ubuntu 20.04.4 LTS), with Python version 3.8 or higher installed. There are no special hardware requirements for running FALCON, but we recommend using a system with at least 16 GB of RAM and a modern CPU to achieve optimal performance. The speed of FALCON increases with the number of CPU cores, as the greedy registration library effectively uses all the available cores.

We're also working on adding support for macOS (both Arm and Intel) and Windows. Stay tuned for updates on these platforms.

If you have any questions or concerns about hardware or software compatibility, please don't hesitate to contact us. We're here to help ensure that you get the most out of FALCON, no matter what platform you're using.

## ⚙️ Installation

To install FALCON on Ubuntu, ensure that your system meets the software and hardware requirements (see the "Hardware Requirements" section above).
and follow these simple steps:

1.) Open a terminal and run the following command to ensure that Git is configured correctly:

```bash

sudo git config --global url."https://".insteadOf git://

```

2.) Clone the FALCON repository from GitHub by running the following command:

```bash
git clone https://github.com/LalithShiyam/FALCON.git
```

3.) Navigate to the FALCON directory:

```bash
cd FALCON
```

4.) Run the FALCON installer script to set up the necessary dependencies:

```bash
sudo bash falcon_installer.sh
```

Note: If you already have read/write access, you don't need to use ```sudo```.

The entire installation process should take approximately 5-10 minutes. Once the installation is complete, you can start using FALCON to perform motion correction in your dynamic total-body or whole-body PET images.

If you encounter any issues during the installation process, please don't hesitate to contact us for assistance. We're here to help ensure that you can use FALCON effectively and efficiently.

## 🖥 Usage

FALCON supports DICOM, Nifti, Analyze, and Metaimage file formats, whether it's a single 4D image or multiple 3D images. Simply specify the directory where the files are located and indicate the registration type. FALCON will take care of the rest.

- To use FALCON, use the following syntax:

```bash


falcon -m path_to_4d_images -r <rigid | affine | deformable> -i <number_of_iterations_per_level> -sf <starting_frame_from_which_moco_should_be_performed> -rf <reference_frame>
```
- Here's an example of using FALCON in Pro mode:

```bash

falcon -m /Documents/Sub001 -r deformable -i 100,50,25 -sf 3 -rf -1 # -1 indicates the last frame of the series
```
In the example above, FALCON is performing deformable registration with 100, 50, and 25 iterations at each level of the multi-scale registration. The registration will start from the 3rd frame and use the last frame as the reference.

- If you're in Lazy mode and don't need to specify any additional parameters, you can simply use the following command:

```bash
falcon -m /Documents/Sub001 -r deformable
```
- If you need help with FALCON or want to review the command line options, you can use the following command:

```bash
falcon --help
```
Please note that the number of iterations is specified as a string of values seperated by 'x' in the -i option. For example, to perform 50 iterations at each level, you would use -i 50x50x50.


## 🗂 Required folder structure 

FALCON only requires the dynamic PET images of a subject. Once the path is set, along with the minimalistic arguments, FALCON takes care of the rest.

Here's an example of the required folder structure:

```bash

└── PET_WB_DYNAMIC_(QC)_0005  # Main folder containing the dynamic PET images to motion correct
    └── XXX.dcm or XXX.ima or XXX.mha or XXX.nii.gz or XXX.img/hdr # The input images can be DICOM, Nifti, Analyze, or Metaimage files (and can be either a single 4D image or multiple 3D images)
        
```
In the example above, the main folder contains the dynamic PET images to be motion corrected. The input images can be DICOM, Nifti, Analyze, or Metaimage files, and they can be either a single 4D image or multiple 3D images.

## 📈 Results

At present, FALCON splits the motion-corrected images into Nifti files (.nii.gz). Work is currently underway to convert the motion-corrected images to their original file formats. The motion-corrected images will be stored in dynamic_pet_folder/nifti/split3d/moco.

Here's an example of the resulting folder structure:


```bash
└── PET_WB_DYNAMIC_(QC)_0005 # Main folder containing the dynamic PET images to motion correct
    ├── XX.dcm or XXX.ima or XXX.mha # Input images to motion correct
    ├── nifti # If the input images are non-Nifti, they will be converted to Nifti and stored here
        └── split3d # The 4D Nifti file will be split into 3D Nifti files and stored here for easy processing
            └── moco # All the motion-corrected images will be stored here
                ├── 4d-moco.nii.gz # Motion-corrected images combined into a single 4D image
                ├── moco-vol0000.nii.gz # Individual motion-corrected images are found here
                ├── moco-vol0001.nii.gz
                ├── moco-vol0002.nii.gz
                ├── ...
                ├── moco-vol000x.nii.gz
                └── transform # All the rigid/affine (*.mat) files and (*warp.nii.gz) files will be stored here
                    ├── vol0000.nii.gz_affine.mat
                    ├── vol0000.nii.gz_inverse_warp.nii.gz
                    ├── vol0000.nii.gz_warp.nii.gz
                    ├── vol0001.nii.gz_affine.mat
                    ├── vol0001.nii.gz_inverse_warp.nii.gz
                    ├── vol0001.nii.gz_warp.nii.gz
                    ├── vol0002.nii.gz_affine.mat
                    ├── vol0002.nii.gz_inverse_warp.nii.gz
                    ├── vol0002.nii.gz_warp.nii.gz
                    ├── ...
                    ├── vol000x.nii.gz_affine.mat
                    ├── vol000x.nii.gz_inverse_warp.nii.gz
                    └── vol000x.nii.gz_warp.nii.gz

```
In the example above, the resulting folder structure shows the main folder containing the dynamic PET images that have been motion corrected. The input images can be DICOM, Nifti, Analyze, or Metaimage files. If the input images are not Nifti, they will be converted to Nifti and stored in the "nifti" folder. The 4D Nifti file will be split into 3D Nifti files and stored in the "split3d" folder, with the motion-corrected images being stored in the "moco" folder. The individual motion-corrected images are stored in Nifti format, and the rigid/affine (*.mat) and (*warp.nii.gz) files will be stored in the "transform" folder.

## ❤️ Citations

In submission.

## 🙏🏽 Acknowledgements
- This research is supported through an [IBM University Cloud Award](https://www.research.ibm.com/university/). 
- The storyboard for `FALCON` was made by [Vivian Tseng](https://www.instagram.com/tsengiiii/) from the University of Applied Arts Vienna. 

## 🛠  To do

- [x] Brain MoCo evaluation [@Keyn34](https://github.com/Keyn34) 
- [x] Respiratory MoCo evaluation [@DariaFerrara](https://github.com/DariaFerrara)
- [x] Cardiac MoCo evaluation [@DrLyngby](https://github.com/DrLyngby)
- [x] Selection of the 'candidate frames' for motion correction using voxelwise NCC criteria [@LalithShiyam](https://github.com/LalithShiyam)
- [ ] FALCON for Intel Macs and Apple Silicon Macs [@LalithShiyam](https://github.com/LalithShiyam)
- [ ] Making FALCON as a python package that can be installed via pip. [@LalithShiyam](https://github.com/LalithShiyam)

## 🦅 FALCON: An ENHANCE-PET project

<p align="center">
<img src="https://github.com/LalithShiyam/FALCON/blob/main/Images/DALL·E%202022-11-01%2018.21.39%20-%20a%20moose%20with%20majestic%20horns.png">
</p>
<p align="right">Above image generated by dall-e</p>
