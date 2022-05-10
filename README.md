![Falcon-logo](Images/Falcon-logo.png)

## 🦅 About FALCON
FALCON (Fast algorithms for motion correction) is a python wrapper program for performing PET motion correction (both head and total-body). We have used the fast 'greedy' registration toolkit as the registration engine and built our program around it.

## 🗂 Required folder structure 

```falcon``` just requires only the dynamic PET images of a subject, once the path is set (along with the minimalistic arguments), it takes care of the rest. 

**Expected folder structure:**

```bash

└── PET_WB_DYNAMIC_(QC)_0005  # Main folder containing the dynamic PET images to motion correct
    └── XXX.dcm or XXX.ima or XXX.mha or XXX.nii.gz or XXX.img/hdr # The input images can be DICOM/Nifti/Analyze/Metaimage (can be single 4d or multiple 3d files) 
        
```
**Folder structure after running FALCON:**

```bash
└── PET_WB_DYNAMIC_(QC)_0005 # Main folder containing the dynamic PET images to motion correct
    └── XX.dcm or XXX.ima or XXX.mha # Input images to motion correct
    └── nifti # If the input images are non-nifti, they will be converted to nifti and will be stored here
        └── split3d # The 4d-nifti file will be split into 3d nifti files and stored here for easy processing
            └── moco # All the motion corrected images will be stored here. 
                └── transform # All the rigid/affine (*.mat) files and (*warp.nii.gz) files will be stored here.
```

## ⛔️ Hard requirements 

The entire program has been *ONLY* tested on **Ubuntu linux OS and Mac OS**. There are no special hardware requirements for running falcon. Just remember that the speed of ```falcon``` increases with the number of CPU cores, as greedy registration library effectively uses all the available cores.

## ⚙️ Installation

As of now ```falcon``` only works on mac and linux. The entire installation should take ~15 min. 
```bash
git config --global url."https://".insteadOf git://
git clone https://github.com/LalithShiyam/FALCON.git
cd FALCON
sudo bash falcon_installer.sh
```
## 🖥 Usage

Inputs can be either DICOM/Nifti/Analyze/Metaimage. The provided images can be a single 4D image or multiple 3D images. Just point to the directory where the files resides and FALCON should ideally take care of the rest.

```bash

#syntax:
falcon -m path_to_4d_images -s frame_from_which_moco_needs_to_start -r rigid_affine_or_deformable -a fixed_or_rolling -i multilevel_iterations

#example: 
falcon -m /Documents/Sub001 -s 3 -r deformable -a fixed -i 100x25x10

#help: 
falcon --help
```
## 📈 Results

As of now ```falcon``` splits the motion-corrected images as nifti files (.nii.gz). Currently work is being done to convert the motion corrected images to their respective formats. The motion corrected images will be stored in dynamic_pet_folder/nifti/split3d/moco.
