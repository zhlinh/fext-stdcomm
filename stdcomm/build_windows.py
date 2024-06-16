#!/usr/bin/env python3
# -- coding: utf-8 --
#
# build_windows.py
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
# substantial portions of the Softwaree

import os
import sys
import glob
import time
import shutil
import platform

from build_utils import *

SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]
# dir name as project name
PROJECT_NAME = os.path.basename(SCRIPT_PATH).upper()
PROJECT_NAME_LOWER = PROJECT_NAME.lower()
PROJECT_RELATIVE_PATH = PROJECT_NAME.lower()

BUILD_OUT_PATH = 'cmake_build/Windows'
INSTALL_PATH = BUILD_OUT_PATH + "/Windows.out/"

# VS 2019
WIN_BUILD_CMD = 'cmake ../.. -G "Visual Studio 16 2019" -T v142 && cmake --build . --target install --config %s'
WIN_GEN_PROJECT_CMD = 'cmake ../.. -G "Visual Studio 16 2019" -T v142'
WIN_ARCH = 'x64'
WIN_SRC_DIR = "src"
THIRD_PARTY_MERGE_LIBS = ["pthread"]

def build_windows(incremental, tag='', config='Release'):
    before_time = time.time()
    # generate verinfo.h
    gen_project_revision_file(PROJECT_NAME, OUTPUT_VERINFO_PATH, get_version_name(SCRIPT_PATH), tag,
                              incremental=incremental)

    clean(BUILD_OUT_PATH, incremental)
    os.chdir(BUILD_OUT_PATH)

    cmd = WIN_BUILD_CMD % (config)
    print("build cmd:" + cmd)
    ret = os.system(cmd)
    os.chdir(SCRIPT_PATH)

    if 0 != ret:
        print('!!!!!!!!!!!!!!!!!!build fail!!!!!!!!!!!!!!!!!!!!')
        return False

    win_result_dir = INSTALL_PATH + f'{PROJECT_NAME_LOWER}.dir/' + WIN_ARCH
    if os.path.exists(win_result_dir):
        shutil.rmtree(win_result_dir)
    os.makedirs(win_result_dir)

    needed_libs = glob.glob(INSTALL_PATH + '*.lib')

    for other_lib in THIRD_PARTY_MERGE_LIBS:
        temp_libs_path = SCRIPT_PATH + f"/third_party/{other_lib}/lib/windows/{WIN_ARCH}/"
        temp_libs = glob.glob(temp_libs_path + '*.lib')
        needed_libs.extend(temp_libs)

    filtered_lib_names = list(map(lambda x: os.path.splitext(os.path.basename(x))[0],
                                  needed_libs))

    print(f"build merge libs: {needed_libs}")
    if not merge_win_static_libs(needed_libs, win_result_dir + f"/{PROJECT_NAME_LOWER}.lib"):
        print('!!!!!!!!!!!!!!!!!!merge libs fail!!!!!!!!!!!!!!!!!!!!')
        return False

    headers = dict()
    headers.update(WINDOWS_BUILD_COPY_HEADER_FILES)
    copy_file_mapping(headers, './', win_result_dir + "/include")

    sub_folders = filtered_lib_names
    # copy pdb of third_party
    copy_windows_pdb(BUILD_OUT_PATH, sub_folders, config, INSTALL_PATH)
    src_dir_folder = PROJECT_NAME_LOWER + "-" + WIN_SRC_DIR
    # copy pdb of src
    sub_folders = list(map(lambda x: x.replace(PROJECT_NAME_LOWER, src_dir_folder), sub_folders))
    copy_windows_pdb(os.path.join(BUILD_OUT_PATH, src_dir_folder), sub_folders, config, INSTALL_PATH)

    # zip pdb files
    pdf_suffix = ".pdb"
    zip_files_ends_with(INSTALL_PATH, pdf_suffix, win_result_dir + f"/{PROJECT_NAME_LOWER}{pdf_suffix}.zip")

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('==================Output========================')
    print(f"libs: {win_result_dir}")
    print(f"pdb files: {INSTALL_PATH}")

    after_time = time.time()
    print(f"use time: {int(after_time - before_time)} s")
    return True


def gen_win_project(tag='', config='Release'):
    before_time = time.time()
    # generate verinfo.h
    gen_project_revision_file(PROJECT_NAME, OUTPUT_VERINFO_PATH, get_version_name(SCRIPT_PATH), tag,
                              incremental=False)

    clean(BUILD_OUT_PATH, False)
    os.chdir(BUILD_OUT_PATH)
    ret = os.system(WIN_GEN_PROJECT_CMD)
    os.chdir(SCRIPT_PATH)

    after_time = time.time()

    print(f"use time: {int(after_time - before_time)} s")

    if 0 != ret:
        print('!!!!!!!!!!!!!!!!!!gen project file fail!!!!!!!!!!!!!!!!!!!!')
        return False

    project_file_prefix = os.path.join(SCRIPT_PATH, BUILD_OUT_PATH, PROJECT_NAME_LOWER)
    project_file = get_project_file_name(project_file_prefix)

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('==================Output========================')
    print(f'project file: {project_file}')

    os.system(get_open_project_file_cmd(project_file))

    return True


def main():
    if not check_vs_env():
        return

    while True:
        if len(sys.argv) >= 2:
            num = sys.argv[1]
        else:
            num = input(
                'Enter menu:'
                + f'\n1. Clean && build {PROJECT_NAME_LOWER} Release.'
                + f'\n2. Gen Project {PROJECT_NAME_LOWER} file.'
                + f'\n3. Clean && build {PROJECT_NAME_LOWER} Debug.'
                + '\n4. Exit\n'
            )
        print(f'==================Windows Choose num: {num}==================')
        if num == '1':
            build_windows(incremental=False, tag=num, config='Release')
            break
        elif num == '2':
            gen_win_project(tag=num, config='Release')
            break
        elif num == '3':
            build_windows(incremental=False, tag=num, config='Debug')
            break
        elif num == '4':
            break
        else:
            break


if __name__ == '__main__':
    main()
