#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ***********************************************************************************************************************
# File: fileop.py
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


# Function to display the logo of the software
def display_logo():
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

# Function that gets a list of folders inside a directory using glob and returns the list of paths sorted by name


def get_folders(dir_path):
    # Get a list of folders inside a directory using glob
    folders = glob.glob(os.path.join(dir_path, "*"))
    # Sort the list of folders by name
    folders.sort(key=lambda x: os.path.basename(x))
    return folders


# Functions that gets a list of files using wildcard inside a directory using glob and returns the list of paths sorted
# by name

def get_files(dir_path, wildcard):
    # Get a list of files inside a directory using glob
    files = glob.glob(os.path.join(dir_path, wildcard))
    # Sort the list of files by name
    files.sort(key=lambda x: os.path.basename(x))
    return files


# Function for making directories if they do not exist inside a given directory with user specified name

def make_dir(dir_path, dir_name):
    # Create a directory with user specified name if it does not exist
    if not os.path.exists(os.path.join(dir_path, dir_name)):
        os.mkdir(os.path.join(dir_path, dir_name))

    return os.path.join(dir_path, dir_name)


# Function that moves multiple files from one directory to another based on a wildcard

def move_files(src_dir, dest_dir, wildcard):
    # Get a list of files using wildcard
    files = get_files(src_dir, wildcard)
    # Move each file from source directory to destination directory
    for file in files:
        os.rename(file, os.path.join(dest_dir, os.path.basename(file)))


# Function that copies multiple files from one directory to another based on a wildcard using shutil

def copy_files(src_dir, dest_dir, wildcard):
    # Get a list of files using wildcard
    files = get_files(src_dir, wildcard)
    # Copy each file from source directory to destination directory
    for file in files:
        shutil.copy(file, dest_dir)


# Function to delete a list of files

def delete_files(dir_path, wildcard):
    # Get a list of files using wildcard
    files = get_files(dir_path, wildcard)
    # Delete each file from directory
    for file in files:
        os.remove(file)
