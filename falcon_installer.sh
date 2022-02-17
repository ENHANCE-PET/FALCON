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


echo '[1] Downloading required files IBM cloud storage...'
# Check if the OS is Mac or Linux and change subsequent commands accordingly
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        wget "https://falcon.s3.eu-de.cloud-object-storage.appdomain.cloud/FALCON-files.zip"  
        sudo apt-get install cmake pkg-config
        sudo apt install git
        sudo apt update
        sudo apt install python3-pip
        sudo apt install python2
        
elif [[ "$OSTYPE" == "darwin"* ]]; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install wget
        wget "https://falcon.s3.eu-de.cloud-object-storage.appdomain.cloud/FALCON-files.zip"  
        brew install pkg-config
        brew install git
        wget https://raw.githubusercontent.com/Homebrew/homebrew-core/86a44a0a552c673a05f11018459c9f5faae3becc/Formula/python@2.rb
        brew install python@2.rb
        rm python@2.rb
elif [[ "$OSTYPE" == "msys" ]]; then
        echo 'MSYS is not supported'
        exit 1
elif [[ "$OSTYPE" == "win32" ]]; then
        echo 'Windows is not supported'
        exit 1
elif [[ "$OSTYPE" == "freebsd"* ]]; then
        echo 'FreeBSD is not supported'
        exit 1
else
        echo 'Unknown OS'
        exit 1
fi

echo '[2] Installing python packages for running FALCON...'
pip install -r requirements.txt

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
sudo python2 "$falcon_bin"/fslinstaller.py
sudo chmod +x "$falcon_src"
sudo ln -s "$falcon_src" $root_path/'falcon'

echo '[8] Setting up fsl environment variables in the .bashrc'
{
  echo "FSLDIR=/usr/local/fsl"
  echo ". ${FSLDIR}/etc/fslconf/fsl.sh"
  echo "PATH=${FSLDIR}/bin:${PATH}"
  echo "export FSLDIR PATH"
}   >> ~/.bashrc

echo '[9] Building ITK from source...'
git clone https://github.com/InsightSoftwareConsortium/ITK.git
# shellcheck disable=SC2164
mkdir ITK-build && cd ITK-build
ccmake ../ITK
sudo make -j4
sudo make install

echo '[11] Finished installing FALCON!'

