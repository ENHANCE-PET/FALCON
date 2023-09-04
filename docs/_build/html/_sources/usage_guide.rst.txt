FALCON Usage Guide
==================

Harness the power of FALCON with ease. Whether you're dealing with DICOM, Nifti, Analyze, or Metaimage file formats, FALCON seamlessly handles it all. This guide provides a walkthrough on how to use FALCON efficiently and effectively.

Supported File Formats
----------------------
FALCON can process:

- DICOM
- Nifti
- Analyze
- Metaimage

You can work with either a single 4D image or multiple 3D images. Just point FALCON to the directory, and let it handle the magic.

Basic Syntax
------------
To launch FALCON, follow this syntax:

.. code-block:: bash

   falcon -m <path_to_4d_images> -r <registration_type> -i <iterations_per_level> -sf <starting_frame> -rf <reference_frame>

Examples
--------
**Pro Mode**:

.. code-block:: bash

   falcon -m /Documents/Sub001 -r deformable -i 100x50x25 -sf 0 -rf -1

This runs FALCON with deformable registration over a multi-scale, starting from the first frame, and using the last frame as the reference.

**Lazy Mode**:

For whole-body registration:

.. code-block:: bash

   falcon -m /Documents/Sub001 -r deformable

For brain-only studies (faster processing):

.. code-block:: bash

   falcon -m /Documents/Sub001 -r rigid

Lazy mode keeps things simple. Many parameters are either inferred or set based on common standards, removing the guesswork.

Important Points
----------------
⚠️ If the inferred start frame doesn't align with your needs, manually set it. FALCON has a conservative internal threshold, but adjustments are sometimes necessary. For more insights, refer to the associated manuscript.

Help & Further Options
----------------------
For detailed command line options or if you need assistance:

.. code-block:: bash

   falcon --help

Remember, when specifying iterations in the `-i` option, use the format `valueXvalueXvalue`. For instance, `-i 50x50x50` signifies 50 iterations at each level.
