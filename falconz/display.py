#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------------------------------------------------------
# Author: Lalith Kumar Shiyam Sundar | Sebastian Gutschmayer
# Institution: Medical University of Vienna
# Research Group: Quantitative Imaging and Medical Physics (QIMP) Team
# Date: 04.07.2023
# Version: 0.1.0
#
# Description:
# This module shows predefined display messages for the falconz.
#
# Usage:
# The functions in this module can be imported and used in other modules within the falconz to show predefined display
# messages.
#
# ----------------------------------------------------------------------------------------------------------------------

import pyfiglet
import logging
from falconz import constants
from falconz import file_utilities


def logo():
    """
    Display FALCON logo
    :return:
    """
    print(' ')
    logo_color_code = constants.ANSI_VIOLET
    slogan_color_code = constants.ANSI_VIOLET
    result = logo_color_code + pyfiglet.figlet_format("FALCON 2.0", font="speed").rstrip() + "\033[0m"
    text = slogan_color_code + "A part of the ENHANCE community. Join us at https://enhance.pet to build the future " \
                               "of " \
                               "PET imaging together." + "\033[0m"
    print(result)
    print(text)
    print(' ')


def citation():
    """
    Display manuscript citation
    :return:
    """
    print(
        " Shiyam Sundar, L. K., Lassen, M. L., Gutschmayer, S., Ferrara, D., Calabrò, A., Yu, J., Kluge, K., Wang, Y., "
        " Nardo, L., Hasbak, P., Kjaer, A., Abdelhafez, Y. G., Wang, G., Cherry, S. R., Spencer, B. A., Badawi, R. D., "
        " Beyer, T., Muzik, O. (2023, June 8). Fully automated, fast motion correction of dynamic whole-body and "
        " total-body PET/CT Imaging Studies. Journal of Nuclear Medicine. "
        " https://jnm.snmjournals.org/content/early/2023/06/08/jnumed.122.265362 ")
    print(" Copyright 2022, Quantitative Imaging and Medical Physics Team, Medical University of Vienna")


def expectations():
    """
    Display expected modalities for PUMA. This is used to check if the user has provided the correct set of modalities for each tracer set.
    """
    # display the expected modalities
    print(f' Expected dimensions: {constants.EXPECTED_DIMENSIONS} | Allowed modalities: {constants.MODALITIES}')
    logging.info(f' Expected dimensions: {constants.EXPECTED_DIMENSIONS} | Allowed modalities: {constants.MODALITIES}')
    print(
        f"{constants.ANSI_ORANGE} Warning: Only 4D images will be considered in the analysis. {constants.ANSI_RESET}")

    warning_message = "Only 4D images will be considered in the analysis."
    logging.warning(warning_message)
