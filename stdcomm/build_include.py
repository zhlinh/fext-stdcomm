#!/usr/bin/env python3
# -- coding: utf-8 --
#
# build_include.py
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

import glob
import os
import sys
import time
import platform
import shutil

from build_utils import *

SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]
# dir name as project name
PROJECT_NAME = os.path.basename(SCRIPT_PATH).upper()
PROJECT_NAME_LOWER = PROJECT_NAME.lower()
PROJECT_RELATIVE_PATH = PROJECT_NAME.lower()

BUILD_OUT_PATH = 'cmake_build/Include'
CMAKE_SYSTEM_NAME = platform.system()
INSTALL_PATH = BUILD_OUT_PATH + '/' + CMAKE_SYSTEM_NAME + '.out'


def build_include(incremental, tag=''):
    before_time = time.time()
    print(f'==================build docs with tag: {tag}, install path: {INSTALL_PATH} ========================')

    # generate verinfo.h
    gen_project_revision_file(PROJECT_NAME, OUTPUT_VERINFO_PATH, get_version_name(SCRIPT_PATH), tag,
                              incremental=incremental)
    clean(BUILD_OUT_PATH, incremental)

    if os.path.exists(INSTALL_PATH):
        shutil.rmtree(INSTALL_PATH)

    os.chdir(SCRIPT_PATH)
    copy_file_mapping(INCLUDE_BUILD_COPY_HEADER_FILERS, "./",  INSTALL_PATH + "/include")

    dst_target_path = INSTALL_PATH

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('==================Output========================')
    print(dst_target_path)

    after_time = time.time()

    print(f"use time: {int(after_time - before_time)} s")
    return True


def main(choose, filter_rules=''):
    print(f'==========Choose num: [{choose}], filter: [{filter_rules}]===========')

    result = True
    if choose == '1':
        result = build_include(False, choose)
    else:
        return

    if not result:
        raise RuntimeError('Exception occurs when build or run docs')


if __name__ == '__main__':
    while True:
        if len(sys.argv) >= 2:
            tag = ''
            if len(sys.argv) >= 3:
                tag = sys.argv[2]
            main(sys.argv[1], tag)

            break
        else:
            num = str(input(
                f'Enter menu:\n1. Clean && build {PROJECT_NAME_LOWER} include\n\n2. Exit\n'))
            main(num)
            break

