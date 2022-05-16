#!/usr/bin/env bash

# **********************************************************************************************************************
# File: falcon_uninstaller.sh
# Project: falcon
# Created: 10.05.2022
# Author: Lalith Kumar Shiyam Sundar
# Email: lalith.shiyamsundar@meduniwien.ac.at
# Institute: Quantitative Imaging and Medical Physics, Medical University of Vienna
# Description: Falcon_uninstaller.sh has been particularly created for making the removal process of Falcon easier
# in linux and mac.
# License: Apache 2.0
# **********************************************************************************************************************


echo "[1] Uninstalling Falcon v0.1.0"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[2] Linux detected..."
    echo "[3] Removing falcon from /usr/local/bin..."
    sudo rm /usr/local/bin/falcon
    echo "[4] Removing supporting binaries..."
    sudo rm /usr/local/bin/c3d
    sudo rm /usr/local/bin/greedy
    echo "[5] Removing python dependencies"
    pip uninstall -r requirements.txt
    # shellcheck disable=SC2006
    falcon_dir=`pwd`
    echo "[5] Removing falcon folder from $falcon_dir..."
    sudo rm -rf "$falcon_dir"
    echo "[6] Falcon uninstall complete..."
fi
