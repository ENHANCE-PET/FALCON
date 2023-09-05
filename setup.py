from setuptools import setup, find_packages

setup(
    name='falconz',
    version='2.0.13',
    author='Lalith Kumar Shiyam Sundar',
    author_email='Lalith.shiyamsundar@meduniwien.ac.at',
    description='FalconZ: A streamlined Python package for PET motion correction.',
    python_requires='>=3.9',
    long_description='FalconZ is a robust and comprehensive Python package that offers a simplified approach to PET ('
                     'Positron Emission Tomography) motion correction. The software is equipped to handle both head '
                     'and total-body scans, ensuring high-accuracy results in diverse settings. Built around the '
                     'potent greedy registration toolkit, FalconZ serves as an efficient engine for registration '
                     'tasks, providing precise alignment in PET imaging. The package has been designed with '
                     'user-friendliness in mind, streamlining the implementation process of motion correction. '
                     'Whether you are a researcher, healthcare professional, or an individual working with PET scans, '
                     'FalconZ provides a seamless solution to your needs. It integrates effortlessly into your '
                     'existing Python environment, and its straightforward usability makes it an indispensable tool '
                     'for accurate PET scan analysis.',
    url='https://github.com/QIMP-Team/FALCON',
    license='GPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ],

    keywords='PET motion correction, diffeomorphic imaging, image processing',
    packages=find_packages(),
    install_requires=[
    'nibabel',
    'halo',
    'SimpleITK',
    'pydicom',
    'argparse',
    'numpy',
    'mpire',
    'openpyxl',
    'matplotlib',
    'pyfiglet',
    'natsort',
    'pillow',
    'colorama',
    'rich',
    'pandas',
    'dicom2nifti',
    'requests',
    'emoji',
    'psutil',
    'nilearn',
    'scikit-image',
    'dask',
    'dask[distributed]'
],
    entry_points={
        'console_scripts': [
            'falconz=falconz.falconz:main',
        ],
    },
)
