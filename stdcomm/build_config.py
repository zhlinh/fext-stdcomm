#!/usr/bin/env python3
# -- coding: utf-8 --
#
# build_config.py
# ccgo
#
# Copyright 2024 zhlinh and ccgo Project Authors. All rights reserved.
# Use of this source code is governed by a MIT-style
# license that can be found at
#
# https://opensource.org/license/MIT
#
# The above copyright notice and this permission
# notice shall be included in all copies or
# substantial portions of the Software.

import os
from collections import ChainMap

SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]
# dir name as project name
PROJECT_NAME = os.path.basename(SCRIPT_PATH).upper()
PROJECT_NAME_LOWER = PROJECT_NAME.lower()

ANDROID_MERGE_THIRD_PARTY_LIBS = []
ANDROID_MERGE_EXCLUDE_LIBS = [
    "stdcomm",
]

# apple(iOS/macOS) export header files
APPLE_BUILD_COPY_HEADER_FILES = {
    f"include/{PROJECT_NAME_LOWER}/base/verinfo.h": "base",
    f"include/{PROJECT_NAME_LOWER}/api/apple/Stdcomm.h": "api",
}

# iOS export header files
IOS_BUILD_COPY_HEADER_FILES = ChainMap({
    f"include/{PROJECT_NAME_LOWER}/api/ios/Stdcomm.h": "api",
}, APPLE_BUILD_COPY_HEADER_FILES)

# macOS export header files
MACOS_BUILD_COPY_HEADER_FILES = ChainMap({
    f"include/{PROJECT_NAME_LOWER}/api/macos/Stdcomm.h": "api",
}, APPLE_BUILD_COPY_HEADER_FILES)

# windows export header files
WINDOWS_BUILD_COPY_HEADER_FILES = {
    f"include/{PROJECT_NAME_LOWER}/base/verinfo.h": "base",
    f"include/{PROJECT_NAME_LOWER}/api/native/stdcomm.h": "api",
}

# linux export header files
LINUX_BUILD_COPY_HEADER_FILES = WINDOWS_BUILD_COPY_HEADER_FILES

# include header files
INCLUDE_BUILD_COPY_HEADER_FILERS = {
  "include/": ".",
}

# verinfo file path
OUTPUT_VERINFO_PATH = f"include/{PROJECT_NAME_LOWER}/base/"

# Android project path
ANDROID_PROJECT_PATH = "android/main_android_sdk"
