#!/usr/bin/env bash

# **********************************************************************************************************************
# File: falcon_installer.sh
# Project: falcon
# Created: 27.01.2022
# Author: Lalith Kumar Shiyam Sundar
# Email: lalith.shiyamsundar@meduniwien.ac.at
# Institute: Quantitative Imaging and Medical Physics, Medical University of Vienna
# Description: Falcon_installer.sh has been particularly created for making the installation process of Falcon easier
# in linux and mac.
# License: Apache 2.0
# **********************************************************************************************************************



echo '[1] Installing python packages for running FALCON...'
pip install halo==0.0.31 SimpleITK==2.1.1
echo '[2] Downloading required files IBM cloud storage...'
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget "https://falcon.s3.eu-de.cloud-object-storage.appdomain.cloud/FALCON-files.zip"  
        sudo apt-get install cmake pkg-config
        sudo apt install git
        sudo apt install python2
elif [[ "$OSTYPE" == "darwin"* ]]; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install wget
        wget "https://falcon.s3.eu-de.cloud-object-storage.appdomain.cloud/FALCON-files.zip"  
        brew install pkg-config
        brew install git
        brew install python@2
fi
echo '[3] Unzipping FALCON files...'
unzip FALCON-files.zip
echo '[4] Removing FALCON zip files...'
rm FALCON-files.zip

# shellcheck disable=SC2006
main_dir=`pwd`
# shellcheck disable=SC2006
falcon_dir=`pwd`/'FALCON-files'
falcon_bin=$falcon_dir/'bin'
root_path='/usr/local/bin'
falcon_src=$main_dir/'src'/'run_falcon.py'

echo '[5] Setting up symlinks for dependencies...'
sudo ln -s "$falcon_bin"/'c3d' $root_path/'c3d'
sudo ln -s "$falcon_bin"/'greedy' $root_path/'greedy'
echo '[6] Building dcm2niix from source...'

git clone https://github.com/rordenlab/dcm2niix.git
# shellcheck disable=SC2164
cd dcm2niix
# shellcheck disable=SC2164
mkdir build && cd build
cmake -DZLIB_IMPLEMENTATION=Cloudflare -DUSE_JPEGLS=ON -DUSE_OPENJPEG=ON ..
sudo make install 
echo '[7] Installing fsl, please answer the required questions via the terminal...'
python2 "$falcon_bin"/fslinstaller.py
sudo chmod +x "$falcon_src"
sudo ln -s "$falcon_src" $root_path/'falcon'
