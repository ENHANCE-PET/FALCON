#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ***********************************************************************************************************************
# File: fileOp.py
# Project: falcon
# Created: 27.01.2022
# Author: Lalith Kumar Shiyam Sundar
# Email: Lalith.Shiyamsundar@meduniwien.ac.at
# Institute: Quantitative Imaging and Medical Physics, Medical University of Vienna
# Description: Falcon (FALCON) is a tool for the performing dynamic PET motion correction. It is based on the greedy
# algorithm developed by the Paul Yushkevich. The algorithm is capable of performing fast rigid/affine/deformable
# registration.
# License: Apache 2.0
# **********************************************************************************************************************

import glob
import os
import shutil


def display_logo():
    """
    Display Falcon logo
    :return:
    """
    print("""                                             
                                                                                                                                                                                                                           
                                                                                                                                                                                                  @@@@@ 
                                                                                                                                                                                            @@@@@@@@@   
                                                                                                                                                                                      #@@@@@@@@@@@#     
                                                                                                                                                                                 @@@@@@@@@@@@@@@        
                                                                                                                                                                           @@@@@@@@@@@@@@@@@@@          
                                                                                                                                                                     @@@@@@@@@@@@@@@@@@@@@@@            
                                                                                                                                                               @@@@@@@@@@@@@@@@@@@@@@@@@@@              
                                                                                                                                                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                
                                                                                                                                                      @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                  
                                                                                                                                                    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*                    
                                                                                                                                                   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                       
                                                                                                                                                 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                         
                                                                                                                                                @@@@@@@@@@@@@@@@@@@@@@@@@@@@@                           
                                                                                                                                              .@@@@@@@@@@@@@@@@@@@@@@@@@@@@                             
                                                                                                                                             @@@@@@@@@@@@@@@@@@@@@@@@@@@@                               
                                                                                                                         ,@@                @@@@@@@@@@@@@@@@@@@@@@@@@@                                  
@@                                                                                                                     @@@@               @@@@@@@@@@@@@@@@@@@@@@@@@@                                    
 @@@@                                                                                                               @@@@@@@              @@@@@@@@@@@@@@@@@@@@@@@@@                                      
  @@@@@@@                                                                                                        @@@@@@@@@              @@@@@@@@@@@@@@@@@@@@@@@@                                        
   @@@@@@@@@                                                                                                  @@@@@@@@@@@             @@@@@@@@@@@@@@@@@@@@@@@@                                          
   .@@@@@@@@@@@                                                                                            @@@@@@@@@@@@@             @@@@@@@@@@@@@@@@@@@@@@*                                            
    @@@@@@@@@@@@@@@                                                                                     @@@@@@@@@@@@@@@             @@@@@@@@@@@@@@@@@@@@@                                               
     @@@@@@@@@@@@@@@@@                                                                               @@@@@@@@@@@@@@@@@@           @@@@@@@@@@@@@@@@@@@@@                                                 
      @@@@@@@@@@@@@@@@@@@#                                                                          @@@@@@@@@@@@@@@@@@           @@@@@@@@@@@@@@@@@@@@                                                   
       @@@@@@@@@@@@@@@@@@@@@@                                                                       @@@@@@@@@@@@@@@@@          @@@@@@@@@@@@@@@@@@@@                                                     
       .@@@@@@@@@@@@@@@@@@@@@@@@                                                                    @@@@@@@@@@@@@@@@          @@@@@@@@@@@@@@@@@@@                                                       
          @@@@@@@@@@@@@@@@@@@@@@@@@&                                                                @@@@@@@@@@@@@@@%         @@@@@@@@@@@@@@@@@@                                                         
              @@@@@@@@@@@@@@@@@@@@@@@@@                                                  @          *@@@@@@@@@@@@@@        @@@@@@@@@@@@@@@@@.                                                           
                  ,@@@@@@@@@@@@@@@@@@@@@@@                                             @@@@         *@@@@@@@@@@@@@        @@@@@@@@@@@@@@@@                                                              
                       @@@@@@@@@@@@@@@@@@@@@@&                                       *@@@@@/        *@@@@@@@@@@@@       /@@@@@@@@@@@@@@@                                                                
                            @@@@@@@@@@@@@@@@@@@@@                                   @@@@@@@@        *@@@@@@@@@@@       @@@@@@@@@@@@@@@                                                                  
                                /@@@@@@@@@@@@@@@@@@@                              @@@@@@@@@@@       *@@@@@@@@@@.      @@@@@@@@@@@@@@                                                                    
                                     @@@@@@@@@@@@@@@@@@@                        @@@@@@@@@@@@@@      *@@@@@@@@@@     @@@@@@@@@@@@@@                                                                      
                 %@@                     (@@@@@@@@@@@@@@@@@                     @@@@@@@@@@@@@@       @@@@@@@@@     @@@@@@@@@@@@.                                                                        
                   @@@@@@@@                   @@@@@@@@@@@@@@@@                    @@@@@@@@@@@@@      @@@@@@@@     @@@@@@@@@@@                                                                           
                     @@@@@@@@@@@@                 .@@@@@@@@@@@@@@@                 @@@@@@@@@@@@@     @@@@@@@    @@@@@@@@@@@                                                                             
                      @@@@@@@@@@@@@@@@@@               @@@@@@@@@@@@@@                @@@@@@@@@@@@    @@@@@@@   @@@@@@@@@@                                                                               
                        @@@@@@@@@@@@@@@@@@@@@@              @@@@@@@@@@@@(              @@@@@@@@@@    @@@@@@   @@@@@@@@@                                                                                 
                          @@@@@@@@@@@@@@@@@@@@@@@@@@@           @@@@@@@@@@@@            @@@@@@@@@@   @@@@@  @@@@@@@@&                                                                                   
                           @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@          @@@@@@@@@@           @@@@@@@@@  @@@@  @@@@@@@                                                                                      
                                   .@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@       @@@@@@@@@,         @@@@@@@@@@@@@@@@@@@@                                                                                        
                                              *@@@@@@@@@@@@@@@@@@@@@@@@@      @@@@@@@@       #@@@@@@@@@@@@@@@@                                                                                          
                                                           ,@@@@@@@@@@@@@@@@@@%   @@@@@@@      @@@@@@@@@@@@@                                                                                            
                                                                      @@@@@@@@@@@@@@@@@@@@@@(    @@@@@@@@@                                                                                              
                                                                                   &@@@@@@@@@@@@  /@@@@@                                                                                                
                                           @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                                                                   
                                                @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                        ,#@@@@@@@@@@@@@                                                                       
                                                     .@@@@@@@@@@@@@@@@@@@.                   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                                  
                                                                               .@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                             
                                                                   *@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                             
                                                       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                    @                                                              
                                           @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                                                          
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                                                                 
                 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                                                                         
     *@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                                                                                
                                @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*                                                                                                                       
                              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                                                                                               
                           @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                                                                                                    
                        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                                                                                                        
                     @@@@@@@@@@@@@/            @@@@@@@@@@@@@                                                                                                                                            
                   .                           @@@@@@@@@                                                                                                                                                
                                              @@@@@@                                                                                                                                                    
                                             @@@                                                                                                                                                        
                                            
                                            """)


def get_folders(dir_path: str) -> list:
    """
    Returns a list of all folders in a directory
    :param dir_path: Main directory containing all folders
    :return: List of folder paths
    """
    # Get a list of folders inside a directory using glob
    folders = glob.glob(os.path.join(dir_path, "*"))
    # Sort the list of folders by name
    folders.sort(key=lambda x: os.path.basename(x))
    return folders


def get_files(dir_path: str, wildcard: str) -> list:
    """
    Returns a list of all files in a directory
    :param dir_path: Folder containing all files
    :param wildcard: Wildcard to filter files
    :return: List of file paths
    """
    # Get a list of files inside a directory using glob
    files = glob.glob(os.path.join(dir_path, wildcard))
    # Sort the list of files by name
    files.sort(key=lambda x: os.path.basename(x))
    return files


def make_dir(dir_path: str, dir_name: str) -> str:
    """
    Creates a new directory
    :param dir_path: Directory path to create the new directory in
    :param dir_name: Name of the new directory
    :return: Path to the new directory
    """
    # Create a directory with user specified name if it does not exist
    if not os.path.exists(os.path.join(dir_path, dir_name)):
        os.mkdir(os.path.join(dir_path, dir_name))

    return os.path.join(dir_path, dir_name)


def move_files(src_dir: str, dest_dir: str, wildcard: str) -> None:
    """
    Moves files from one directory to another
    :param src_dir: Source directory from which files are moved
    :param dest_dir: Target directory to which files are moved
    :param wildcard: Wildcard to filter files that are moved
    :return: None
    """
    # Get a list of files using wildcard
    files = get_files(src_dir, wildcard)
    # Move each file from source directory to destination directory
    for file in files:
        os.rename(file, os.path.join(dest_dir, os.path.basename(file)))


def copy_files(src_dir: str, dest_dir: str, wildcard: str) -> None:
    """
    Copies files from one directory to another
    :param src_dir: Source directory from which files are copied
    :param dest_dir: Target directory to which files are copied
    :param wildcard: Wildcard to filter files that are copied
    :return: None
    """
    # Get a list of files using wildcard
    files = get_files(src_dir, wildcard)
    # Copy each file from source directory to destination directory
    for file in files:
        shutil.copy(file, dest_dir)


def delete_files(dir_path: str, wildcard: str) -> None:
    """
    Deletes files from a directory
    :param dir_path: Path to the directory from which files are deleted
    :param wildcard: Wildcard to filter files that are deleted
    :return: None
    """
    # Get a list of files using wildcard
    files = get_files(dir_path, wildcard)
    # Delete each file from directory
    for file in files:
        os.remove(file)

