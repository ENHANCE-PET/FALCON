Installation Guide for FalconZ
==============================

Welcome to the FalconZ installation guide. Follow the steps below to install FalconZ on your preferred operating system. 

Prerequisites
-------------

Before proceeding, ensure you have Python installed. FalconZ requires Python 3.6 or newer. You can check your Python version by running:

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

Installing FalconZ
------------------

With your virtual environment active, install FalconZ using pip:

.. code-block:: bash

    pip install falconz

Deactivating the Virtual Environment
------------------------------------

After you're done, you can deactivate the virtual environment:

.. code-block:: bash

    deactivate

Support
-------

For any installation issues or further assistance, refer to the `documentation <https://falconz.readthedocs.io/en/latest/>`_ or `contact us <https://github.com/QIMP-Team/FALCON/issues>`_.

