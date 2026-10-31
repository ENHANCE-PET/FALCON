Installation Guide for FalconZ
==============================

Welcome to the FalconZ installation guide. Follow the steps below to install FalconZ on your preferred operating system. 

Prerequisites
-------------

Before proceeding, ensure you have Python installed. FalconZ supports Python 3.11 through 3.14; the patched Pillow dependency requires Python 3.11 or later. You can check your Python version by running:

.. code-block:: bash

    python --version

or

.. code-block:: bash

    python3 --version

Virtual Environment Setup
-------------------------

It's highly recommended to use a virtual environment. This keeps your main environment clean and manages dependencies specific to FalconZ without conflicts.

1. **Linux/Mac**:

   .. code-block:: bash

       python3 -m venv falconz_env
       source falconz_env/bin/activate

2. **Windows**:

   .. code-block:: bash

       python -m venv falconz_env
       .\falconz_env\Scripts\activate

Once activated, your command prompt or terminal will prepend with `(falconz_env)`, indicating the virtual environment is active.

Conda Environment Setup
-----------------------

Choose the Python version explicitly when creating a Conda environment:

.. code-block:: bash

    conda create -n falconz python=3.14 pip
    conda activate falconz
    python -m pip install falconz

Installing FalconZ
------------------

With your virtual environment active, install FalconZ using pip:

.. code-block:: bash

    python -m pip install falconz

Deactivating the Virtual Environment
------------------------------------

After you're done, you can deactivate the virtual environment:

.. code-block:: bash

    deactivate

Support
-------

For any installation issues or further assistance, refer to the `documentation <https://falconz.readthedocs.io/en/latest/>`_ or `contact us <https://github.com/QIMP-Team/FALCON/issues>`_.
