![Falcon-logo](Images/Falcon-logo.png)

## 🦅 About FALCON
FALCON (Fast algorithms for motion correction) is a python program for performing PET motion correction (both head and total-body). We have used the fast 'greedy' registration toolkit as the registration engine and built our program around it.

## ⚙️ Installation

As of now ```FALCON``` only works on mac and linux. The entire installation should take ~15 min.
```bash
git clone https://github.com/LalithShiyam/FALCON.git
cd FALCON
sudo bash falcon_installer.sh
```
## 🖥 Usage

Inputs can be either DICOM/Nifti/Analyze/Metaimage. The provided images can be a single 4D image or multiple 3D images. Just point to the directory where the files resides and FALCON should ideally take care of the rest.

```bash

#syntax:
falcon -i path_to_4d_images -s frame_from_which_moco_needs_to_start -r rigid_affine_or_deformable -a fixed_or_rolling 

#example: 
falcon -i /Documents/Sub001 -s 3 -r deformable -a fixed

#help: 
falcon --help
```
