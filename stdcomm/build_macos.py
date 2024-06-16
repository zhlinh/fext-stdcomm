#!/usr/bin/env python3
# -- coding: utf-8 --
#
# build_macos.py
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

from build_utils import *

SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]
# dir name as project name
PROJECT_NAME = os.path.basename(SCRIPT_PATH).upper()
PROJECT_NAME_LOWER = PROJECT_NAME.lower()
PROJECT_RELATIVE_PATH = PROJECT_NAME.lower()

BUILD_OUT_PATH = 'cmake_build/macOS'
INSTALL_PATH = BUILD_OUT_PATH + '/Darwin.out'

# if not target arch, it will be x86_64
MACOS_BUILD_ARM_CMD = 'cmake ../.. -DCMAKE_BUILD_TYPE=Release -DENABLE_ARC=0 -DENABLE_BITCODE=0 -DCMAKE_OSX_ARCHITECTURES="arm64;arm64e"  %s && make -j8 && make install'

MACOS_BUILD_X86_CMD = 'cmake ../.. -DCMAKE_BUILD_TYPE=Release -DENABLE_ARC=0 -DENABLE_BITCODE=0 -DCMAKE_OSX_ARCHITECTURES="x86_64" %s && make -j8 && make install'

GEN_MACOS_PROJ = 'cmake ../.. -G Xcode -DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.9 -DENABLE_BITCODE=0 %s'

def build_macos(target_option='', tag=''):
    before_time = time.time()
    print('==================build_macos========================')
    # generate verinfo.h
    gen_project_revision_file(PROJECT_NAME, OUTPUT_VERINFO_PATH, get_version_name(SCRIPT_PATH), tag)

    clean(BUILD_OUT_PATH)
    os.chdir(BUILD_OUT_PATH)

    build_cmd = MACOS_BUILD_ARM_CMD % target_option
    ret = os.system(build_cmd)
    os.chdir(SCRIPT_PATH)
    if ret != 0:
        print('!!!!!!!!!!!build os fail!!!!!!!!!!!!!!!')
        return False

    lipo_dst_lib = INSTALL_PATH + f'/{PROJECT_NAME_LOWER}'
    libtool_os_dst_lib = INSTALL_PATH + f'/{PROJECT_NAME_LOWER}_os'
    libtool_simulator_dst_lib = INSTALL_PATH + f'/{PROJECT_NAME_LOWER}_simulator'
    dst_framework_path = INSTALL_PATH + f'/{PROJECT_NAME_LOWER}.framework'
    dst_framework_headers = MACOS_BUILD_COPY_HEADER_FILES
    # add static libs
    total_src_lib = glob.glob(INSTALL_PATH + '/*.a')
    rm_src_lib = []
    libtool_src_lib = [x for x in total_src_lib if x not in rm_src_lib]
    print(f'libtool src lib: {len(libtool_src_lib)}/{len(total_src_lib)}')

    if not libtool_libs(libtool_src_lib, libtool_os_dst_lib):
        return False

    clean(BUILD_OUT_PATH)
    os.chdir(BUILD_OUT_PATH)

    build_cmd = MACOS_BUILD_X86_CMD % (target_option)
    ret = os.system(build_cmd)
    os.chdir(SCRIPT_PATH)
    if ret != 0:
        print('!!!!!!!!!!!build simulator fail!!!!!!!!!!!!!!!')
        return False
    if not libtool_libs(glob.glob(INSTALL_PATH + '/*.a'), libtool_simulator_dst_lib):
        return False

    # src libs to be libtool
    lipo_src_libs = []
    lipo_src_libs.append(libtool_os_dst_lib)
    lipo_src_libs.append(libtool_simulator_dst_lib)
    #if len(target_option) <= 0:
    #    lipo_src_libs.append(libtool_xlog_dst_lib)


    if not libtool_libs(lipo_src_libs, lipo_dst_lib):
        return False

    make_static_framework(lipo_dst_lib, dst_framework_path, dst_framework_headers, './')

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('==================Output========================')
    print(dst_framework_path)

    after_time = time.time()

    print(f"use time: {int(after_time - before_time)} s")
    return True

def gen_macos_project(target_option='', tag=''):
    print('==================gen_macos_project========================')
    # generate verinfo.h
    gen_project_revision_file(PROJECT_NAME, OUTPUT_VERINFO_PATH, get_version_name(SCRIPT_PATH), tag)

    clean(BUILD_OUT_PATH)
    os.chdir(BUILD_OUT_PATH)

    cmd = GEN_MACOS_PROJ % target_option
    ret = os.system(cmd)
    os.chdir(SCRIPT_PATH)
    if ret != 0:
        print('!!!!!!!!!!!gen fail!!!!!!!!!!!!!!!')
        return False

    project_file_prefix = os.path.join(SCRIPT_PATH, BUILD_OUT_PATH, PROJECT_NAME_LOWER)
    project_file = get_project_file_name(project_file_prefix)

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('==================Output========================')
    print(f'project file: {project_file}')

    os.system(get_open_project_file_cmd(project_file))

    return True

def main(target_option='', tag=''):
    print("main tag %s" % tag)
    build_macos(target_option, tag)

if __name__ == '__main__':
    while True:
        if len(sys.argv) >= 2:
            num = sys.argv[1]
        else:
            archs = set(['armeabi-v7a'])
            num = str(input(
                'Enter menu:'
                + f'\n1. Clean && Build macOS {PROJECT_NAME_LOWER}.'
                + f'\n2. Gen macOS {PROJECT_NAME_LOWER} Project.'
                + '\n3. Exit.\n'))
        print(f'==================MacOS Choose num: {num}==================')
        if num == '1':
            main(tag=num)
            break
        elif num == '2':
            gen_macos_project(tag=num)
            break
        else:
            break
