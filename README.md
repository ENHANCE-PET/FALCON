<p align="center">
<img src="https://github.com/LalithShiyam/FALCON/blob/main/Images/Falcon-logo.png">
</p>

## 🦅 About FALCON
<p align="center">
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/LalithShiyam/FALCON/blob/main/Images/Falcon_story_darkmode.gif" width="500" height="500">
  <img alt="Shows an illustrated storyboard in light color mode and an inverted storyboard in dark color mode." src="https://github.com/LalithShiyam/FALCON/blob/main/Images/Falcon_story_darkmode.gif" width="500" height="500">
</p>


`FALCON` (Fast algorithms for motion correction) is a python wrapper program for the ITK based 'greedy' diffeomorphism registration binaries (LDDMM and Sym Diff Demons) to perform image-based PET motion correction (both head and total-body). It uses diffemorphisms that are 'almost' inverse consistent to rapidly align dynamic PET images. 

## ⛔️ Hard requirements 

The software has only been tested on Ubuntu 20.04.4 LTS.

- Python version >= 3.8

There are no special hardware requirements for running falcon. Just remember that the speed of ```falcon``` increases with the number of CPU cores, as greedy registration library effectively uses all the available cores.

## ⚙️ Installation

As of now ```falcon``` only works on linux (Ubuntu). The entire installation should take ~5-10 min. 
```bash
sudo git config --global url."https://".insteadOf git://
git clone https://github.com/LalithShiyam/FALCON.git
cd FALCON
sudo bash falcon_installer.sh
```
## 🖥 Usage

Inputs can be either DICOM/Nifti/Analyze/Metaimage. The provided images can be a single 4D image or multiple 3D images. Just point to the directory where the files resides and FALCON should ideally take care of the rest.

```bash

#syntax:
falcon -m path_to_4d_images -r <rigid | affine | deformable> -i <100x50x25> -s <0 | 1 | 2>

#example: 
falcon -m /Documents/Sub001 -r deformable -i 100x25x10 -s 3

#help: 
falcon --help

```

## 🗂 Required folder structure 

```falcon``` just requires only the dynamic PET images of a subject, once the path is set (along with the minimalistic arguments), it takes care of the rest. 

```bash

└── PET_WB_DYNAMIC_(QC)_0005  # Main folder containing the dynamic PET images to motion correct
    └── XXX.dcm or XXX.ima or XXX.mha or XXX.nii.gz or XXX.img/hdr # The input images can be DICOM/Nifti/Analyze/Metaimage (can be single 4d or multiple 3d files) 
        
```
## 📈 Results

As of now ```falcon``` splits the motion-corrected images as nifti files (.nii.gz). Currently work is being done to convert the motion corrected images to their respective formats. The motion corrected images will be stored in dynamic_pet_folder/nifti/split3d/moco. 


```bash
└── PET_WB_DYNAMIC_(QC)_0005 # Main folder containing the dynamic PET images to motion correct
    └── XX.dcm or XXX.ima or XXX.mha # Input images to motion correct
    └── nifti # If the input images are non-nifti, they will be converted to nifti and will be stored here
        └── split3d # The 4d-nifti file will be split into 3d nifti files and stored here for easy processing
            └── moco # All the motion corrected images will be stored here. 
                ├── 4d-moco.nii.gz # Motion corrected images combined to a single 4d-image.
                ├── moco-vol0000.nii.gz # Individual motion corrected images are found here.
                ├── moco-vol0001.nii.gz
                ├── moco-vol0002.nii.gz
                ├── .
                ├── .
                ├── .
                ├── moco-vol000x.nii.gz
                └── transform # All the rigid/affine (*.mat) files and (*warp.nii.gz) files will be stored here.
                    ├── vol0000.nii.gz_affine.mat
                    ├── vol0000.nii.gz_inverse_warp.nii.gz
                    ├── vol0000.nii.gz_warp.nii.gz
                    ├── vol0001.nii.gz_affine.mat
                    ├── vol0001.nii.gz_inverse_warp.nii.gz
                    ├── vol0001.nii.gz_warp.nii.gz
                    ├── vol0002.nii.gz_affine.mat
                    ├── vol0002.nii.gz_inverse_warp.nii.gz
                    ├── vol0002.nii.gz_warp.nii.gz
                    ├── .
                    ├── .
                    ├── .
                    ├── vol000x.nii.gz_affine.mat
                    ├── vol000x.nii.gz_inverse_warp.nii.gz
                    └── vol000x.nii.gz_warp.nii.gz

```


## 🙏🏽 Acknowledgements
- This research is supported through an [IBM University Cloud Award](https://www.research.ibm.com/university/). 
- The storyboard for `FALCON` was made by [Vivian Tseng](https://www.instagram.com/tsengiiii/) from the University of Applied Arts Vienna. 

## 🛠  To do

- [x] Brain MoCo evaluation [@Keyn34](https://github.com/Keyn34) 
- [x] Respiratory MoCo evaluation [@DariaFerrara](https://github.com/DariaFerrara)
- [x] Cardiac MoCo evaluation [@DrLyngby](https://github.com/DrLyngby)
- [ ] Selection of the 'candidate frames' for motion correction using voxelwise NCC criteria [@LalithShiyam](https://github.com/LalithShiyam)

## 🦅 FALCON: An ENHANCE-PET project

<p align="center">
<img src="https://github.com/LalithShiyam/FALCON/blob/main/Images/DALL·E%202022-11-01%2018.21.39%20-%20a%20moose%20with%20majestic%20horns.png">
</p>
<p align="right">Above image generated by dall-e</p>
