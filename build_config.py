#!/usr/bin/env python
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

# ========================================================
# Project Configurations
# CONFIG_PROJECT_NAME:           Project Name, The Identity of Product, i.e. "CCGO"
# CONFIG_PROJECT_RELATIVE_PATH:  Project Relative Directory, i.e. "ccgo"
# CONFIG_GRADLE_TASK_NAME:       Android Archive Gradle Task Name, i.e. "archiveProject"
# CONFIG_IOS_TASK_TAG:           iOS build TAG, i.e. "1"
# CONFIG_MACOS_TASK_TAG:         macOS build TAG, i.e. "1"
# CONFIG_WINDOWS_TASK_TAG:       Windows build TAG, i.e. "1"
# CONFIG_LINUX_TASK_TAG:         Linux build TAG, i.e. "1"
# ========================================================

# FIXME: This is the place where each project needs to adjust
# The Project Name
CONFIG_PROJECT_NAME = "STDCOMM"
# The Project Relative Path                        
CONFIG_PROJECT_RELATIVE_PATH = "stdcomm"
# The Android Gradle Task Name, e.g. archiveProject
CONFIG_GRADLE_TASK_NAME = "archiveProject"
# The iOS Task Tag, e.g. 1
CONFIG_IOS_TASK_TAG = "1"
# The Document Pages Branch Name, e.g. "oa-pages"
CONFIG_PAGES_BRANCH_NAME = "oa-pages"
