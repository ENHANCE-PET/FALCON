# Libraries to import

import os


# Call to greedy to perform rigid registration
def rigid(fixed_img, moving_img, cost_function):
    cmd_to_run = f"greedy -d 3 -a -i {fixed_img} {moving_img} -ia-image-centers -dof 6 -o rigid.mat -n 100x50x25 " \
                 f"-m {cost_function}"
    print("*******************************************************************************************")
    print(f"Registration type: Rigid")
    print(f"Reference image: {fixed_img}")
    print(f"Moving image: {moving_img}")
    print(f"Cost function: {cost_function}")
    print(f"Initial alignment: Image centers")
    print(f"Multiresolution level iterations: 100x50x25")
    print(f"Transform file generated: rigid.mat")
    print("*******************************************************************************************")
    os.system(cmd_to_run)
    print("Rigid registration complete")


# Call to greedy to perform affine registration

def affine(fixed_img, moving_img, cost_function):
    cmd_to_run = f"greedy -d 3 -a -i {fixed_img} {moving_img} -ia-image-centers -dof 12 -o affine.mat -n 100x50x25 " \
                 f"-m {cost_function} "
    print("*******************************************************************************************")
    print(f"- Registration type: Affine")
    print(f"- Reference image: {fixed_img}")
    print(f"- Moving image: {moving_img}")
    print(f"- Cost function: {cost_function}")
    print(f"- Initial alignment: Image centers")
    print(f"- Multiresolution level iterations: 100x50x25")
    print(f"- Transform file generated: affine.mat")
    print("*******************************************************************************************")
    os.system(cmd_to_run)
    print("Affine registration complete")


# call to greedy to perform deformable registration

def deformable(fixed_img, moving_img, cost_function):
    print("*******************************************************************************************")
    print("Performing affine registration for initial global alignment")
    affine(fixed_img, moving_img, cost_function)
    cmd_to_run = f"greedy -d 3 -m {cost_function} -i {fixed_img} {moving_img} -it affine.mat -o warp.nii.gz -oinv " \
                 f"inverse_warp.nii.gz -n 100x50x25"
    print("*******************************************************************************************")
    print(f"- Registration type: deformable")
    print(f"- Reference image: {fixed_img}")
    print(f"- Moving image: {moving_img}")
    print(f"- Cost function: {cost_function}")
    print(f"- Initial alignment: based on affine.mat")
    print(f"- Multiresolution level iterations: 100x50x25")
    print(f"- Deformation field generated: warp.nii.gz + inverse_warp.nii.gz")
    print("*******************************************************************************************")

    os.system(cmd_to_run)
    print("Deformable registration complete")


# call to greedy to perform resampling based on the deformation field

def resample(fixed_img, moving_img, resampled_moving_img, registration_type, segmentation="", resampled_seg=""):
    if registration_type == 'rigid':
        if segmentation and resampled_seg:
            cmd_to_run = f"greedy -d 3 -rf {fixed_img} -ri NN -rm {moving_img} {resampled_moving_img} -ri LABEL " \
                         f"0.2vox -rm {segmentation} {resampled_seg} -r rigid.mat"
        else:
            cmd_to_run = f"greedy -d 3 -rf {fixed_img} -ri NN -rm {moving_img} {resampled_moving_img} -r rigid.mat"
    elif registration_type == 'affine':
        if segmentation and resampled_seg:
            cmd_to_run = f"greedy -d 3 -rf {fixed_img} -ri NN -rm {moving_img} {resampled_moving_img} -ri LABEL " \
                         f"0.2vox -rm {segmentation} {resampled_seg} -r affine.mat"
        else:
            cmd_to_run = f"greedy -d 3 -rf {fixed_img} -ri NN -rm {moving_img} {resampled_moving_img} -r affine.mat"
    elif registration_type == 'deformable':
        if segmentation and resampled_seg:
            cmd_to_run = f"greedy -d 3 -rf {fixed_img} -ri NN -rm {moving_img} {resampled_moving_img} -ri LABEL " \
                         f"0.2vox -rm {segmentation} {resampled_seg} -r warp.nii.gz affine.mat"
        else:
            cmd_to_run = f"greedy -d 3 -rf {fixed_img} -ri NN -rm {moving_img} {resampled_moving_img} -r warp.nii.gz " \
                         f"affine.mat"
    os.system(cmd_to_run)
    print("*******************************************************************************************")
    print(f"Resampling parameters")
    print("*******************************************************************************************")
    print(f"- Reference image: {fixed_img}")
    print(f"- Moving image: {moving_img}")
    print(f"- Resampled moving image: {resampled_moving_img}")
    print(f"- Segmentation: {segmentation}")
    print(f"- Resampled segmentation: {resampled_seg}")
    print(f"- Interpolation scheme for resampling: Nearest neighbor for images and segmentations")
    print("*******************************************************************************************")
