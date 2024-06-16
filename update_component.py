#!/usr/bin/env python3
# -- coding: utf-8 --
#
# update_component.py
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
import platform
import subprocess
import urllib.request
import shutil

# ========================================================
# 1. Build Configurations
# CI_IS_RELEASE:                                   If Release version, ture or false
# CI_BUILD_TAG:                                    If TAG, true or false
# CI_BUILD_ANDROID:                                If Build Android, true or false
# CI_BUILD_IOS:                                    If Build iOS, true or false
# CI_BUILD_MACOS:                                  If Build macOS, true or false
# CI_BUILD_WINDOWS:                                If Build Windows, true or false
# CI_BUILD_LINUX:                                  If Build Linux, true or false
# CI_BUILD_COMPONENT_NAME:                         Module Name, i.e. "LOGCOMM"
# CI_BUILD_COMPONENT_RELATIVE_PATH:                Module Relative Directory, i.e. "logcomm"
# CI_BUILD_THIRD_PARTY_COMPONENT_RELATIVE_PATH:    ThirdParty Component Path, i.e. "third_party/xxxcomm"
# 2. Project Configurations
# CONFIG_PROJECT_NAME:           Project Name, The Identity of Product, i.e. "CCGO"
# CONFIG_PROJECT_RELATIVE_PATH:  Project Relative Directory, i.e. "ccgo"
# CONFIG_GRADLE_TASK_NAME:       Android Archive Gradle Task Name, i.e. "archiveProject"
# CONFIG_IOS_TASK_TAG:           iOS build TAG, i.e. "1"
# CONFIG_MACOS_TASK_TAG:         macOS build TAG, i.e. "1"
# CONFIG_WINDOWS_TASK_TAG:       Windows build TAG, i.e. "1"
# CONFIG_LINUX_TASK_TAG:         Linux build TAG, i.e. "1"
# 3. Environment Variables
# ANDROID_HOME:              Android SDK Path
# JAVA_HOME:                 Java Home Path
# ANDROID_NDK_HOME:          Android NDK Path
# CMAKE_HOME:                Cmake Home Path
# ========================================================

# shellcheck disable=SC1091
# import all config parameters, which are start with "CONFIG_"
from build_config import *

script_path = os.path.dirname(os.path.abspath(__file__))
project_path = script_path
android_source_sdk_path = os.path.join(script_path, "source_sdk", "android")
ios_source_sdk_path = os.path.join(script_path, "source_sdk", "ios")

# FIXME: update this when use in your project
project_name = os.environ["CI_BUILD_COMPONENT_RELATIVE_PATH"]
output_zip_prefix = os.environ["CI_BUILD_COMPONENT_NAME"]
third_party_lib_path = os.environ["CI_BUILD_THIRD_PARTY_COMPONENT_RELATIVE_PATH"]

lib_path_name = os.path.join(CONFIG_PROJECT_RELATIVE_PATH, third_party_lib_path)

shutil.rmtree(os.path.join(project_path, lib_path_name), ignore_errors=True)
os.makedirs(os.path.join(project_path, lib_path_name, "ios"))
os.makedirs(os.path.join(project_path, lib_path_name, "android"))

# android
os.chdir(android_source_sdk_path)
android_sdk_file = [f for f in os.listdir() if f.startswith(output_zip_prefix + "_ANDROID_") and f.endswith(".aar") and "ARCHIVE" not in f][0]
print(f"android_sdk_file: {android_sdk_file}")
# update so
shutil.unpack_archive(android_sdk_file, os.path.join(project_path, lib_path_name, f"{project_name}.aar"))
shutil.move(os.path.join(project_path, lib_path_name, f"{project_name}.aar", "jni"), os.path.join(project_path, lib_path_name, "android"))
os.remove(os.path.join(project_path, lib_path_name, "android", "arm64-v8a", "libc++_shared.so"))
os.remove(os.path.join(project_path, lib_path_name, "android", "armeabi-v7a", "libc++_shared.so"))
os.remove(os.path.join(project_path, lib_path_name, "android", "x86_64", "libc++_shared.so"))
shutil.rmtree(os.path.join(project_path, lib_path_name, f"{project_name}.aar"))

# ios
os.chdir(ios_source_sdk_path)
ios_sdk_file = [f for f in os.listdir() if f.startswith(output_zip_prefix + "_IOS_") and f.endswith(".zip") and "ARCHIVE" not in f][0]
print(f"ios_sdk_file: {ios_sdk_file}")
# update framework
shutil.unpack_archive(ios_sdk_file, os.path.join(project_path, lib_path_name))
shutil.move(os.path.join(project_path, lib_path_name, f"{project_name}.framework", project_name), os.path.join(project_path, lib_path_name, "ios", f"{project_name}.a"))
shutil.move(os.path.join(project_path, lib_path_name, f"{project_name}.framework", "Headers", "log"), os.path.join(project_path, lib_path_name))
shutil.rmtree(os.path.join(project_path, lib_path_name, f"{project_name}.framework"))

os.chdir(project_path)

# get android version
android_sdk_file_without_suffix = os.path.splitext(android_sdk_file)[0]
print(f"android_sdk_file_without_suffix: {android_sdk_file_without_suffix}")
# remove head
android_cur_ver = android_sdk_file_without_suffix.replace(f"{output_zip_prefix}_ANDROID_SDK-", "").replace("-release", "").replace("-beta.*", "")
print(f"android_cur_ver: {android_cur_ver}")

# get ios version
ios_sdk_file_without_suffix = os.path.splitext(ios_sdk_file)[0]
print(f"ios_sdk_file_without_suffix: {ios_sdk_file_without_suffix}")
# remove head
ios_cur_ver = ios_sdk_file_without_suffix.replace(f"{output_zip_prefix}_IOS_FRAMEWORK-", "").replace("-release", "").replace("-beta.*", "")
print(f"ios_cur_ver: {ios_cur_ver}")

if android_cur_ver != ios_cur_ver:
    print(f"[ERROR] android_cur_ver:{android_cur_ver} not equals ios_cur_ver:{ios_cur_ver}")
    exit(1)

sys_os = os.uname().sysname
print(f"sys_os={sys_os}")
if sys_os == "Darwin":
    # iOS
    print('iOS, use sed -i ""')
    sed_cmd = 'sed -i ""'
else:
    sed_cmd = 'sed -i'

PROJECT_ROOT_PATH = os.path.join(project_path, CONFIG_PROJECT_RELATIVE_PATH)
# check build gradle file
BUILD_GRADLE_FILE = f"{PROJECT_ROOT_PATH}/build.gradle.kts"
if not os.path.exists(BUILD_GRADLE_FILE):
    BUILD_GRADLE_FILE = f"{PROJECT_ROOT_PATH}/build.gradle"


src = "'version', *\".*\""
dst = f"'version', \"{ios_cur_ver}\""
os.system(f"{sed_cmd} 's/{src}/{dst}/g' {BUILD_GRADLE_FILE}")

os.system("git add --all")
os.system(f"git commit -m \"ci({project_name}): update component {project_name} version to v{ios_cur_ver}\"")
os.system("git push origin master")
