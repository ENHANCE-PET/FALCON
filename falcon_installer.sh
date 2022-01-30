#!/usr/bin/env bash
echo '[1] Installing python packages for running FALCON...'
pip install halo==0.0.31 SimpleITK==2.1.1
echo '[2] Downloading required files IBM cloud storage...'
wget "https://moose-files.s3.eu-de.cloud-object-storage.appdomain.cloud/MOOSE-files.zip"
echo '[3] Unzipping FALCON files...'
unzip FALCON-files.zip
echo '[4] Removing FALCON zip files...'
rm FALCON-files.zip

main_dir=`pwd`
falcon_dir=`pwd`/'FALCON-files'
falcon_bin=$falcon_dir/'bin'
root_path='/usr/local/bin'
falcon_src=$main_dir/'src'/'run_falcon.py'


echo '[5] Setting up symlinks for dependencies...'
sudo ln -s $falcon_bin/'c3d' $root_path/'c3d'
sudo ln -s $falcon_bin/'greedy' $root_path/'greedy'
echo '[6] Building dcm2niix from source...'
sudo apt-get install cmake pkg-config
sudo apt install git
git clone https://github.com/rordenlab/dcm2niix.git
cd dcm2niix
mkdir build && cd build
cmake -DZLIB_IMPLEMENTATION=Cloudflare -DUSE_JPEGLS=ON -DUSE_OPENJPEG=ON ..
sudo make install 
sudo apt install python2
echo '[7] Installing fsl, please answer the required questions via the terminal...'
python2 $falcon_bin/fslinstaller.py 
sudo chmod +x $falcon_src
sudo ln -s $falcon_src $root_path/'falcon'
