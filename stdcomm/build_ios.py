#!/usr/bin/env python3
# -- coding: utf-8 --
#
# build_ios.py
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

BUILD_OUT_PATH = 'cmake_build/iOS'
# Darwin(Linux,Windows).out = ${CMAKE_SYSTEM_NAME}.out
INSTALL_PATH = BUILD_OUT_PATH + '/Darwin.out'

IOS_BUILD_SIMULATOR_CMD = 'cmake ../.. -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=../../cmake/ios.toolchain.cmake -DPLATFORM=SIMULATOR -DARCHS="x86_64;arm64;arm64e" -DDEPLOYMENT_TARGET=10.0 -DENABLE_ARC=0 -DENABLE_BITCODE=0 -DENABLE_VISIBILITY=1 %s && make -j8 && make install'
IOS_BUILD_OS_CMD = 'cmake ../.. -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=../../cmake/ios.toolchain.cmake -DPLATFORM=OS -DARCHS="arm64;arm64e;armv7;armv7s" -DDEPLOYMENT_TARGET=10.0 -DENABLE_ARC=0 -DENABLE_BITCODE=0 -DENABLE_VISIBILITY=1 %s && make -j8 && make install'

GEN_IOS_OS_PROJ = 'cmake ../.. -G Xcode -DCMAKE_TOOLCHAIN_FILE=../../cmake/ios.toolchain.cmake -DPLATFORM=OS -DARCHS="arm64;arm64e;armv7;armv7s" -DDEPLOYMENT_TARGET=10.0 -DENABLE_ARC=0 -DENABLE_BITCODE=0 -DENABLE_VISIBILITY=1 %s'

THIRD_PARTY_ARCHS = ['x86_64', 'arm64e', 'arm64', 'armv7', 'armv7s']

def build_ios(target_option='', tag=''):
    before_time = time.time()
    print('==================build_ios========================')
    # generate verinfo.h
    gen_project_revision_file(PROJECT_NAME, OUTPUT_VERINFO_PATH, get_version_name(SCRIPT_PATH), tag)

    clean(BUILD_OUT_PATH)
    os.chdir(BUILD_OUT_PATH)

    build_cmd = IOS_BUILD_OS_CMD % target_option
    ret = os.system(build_cmd)
    os.chdir(SCRIPT_PATH)
    if ret != 0:
        print('!!!!!!!!!!!build os fail!!!!!!!!!!!!!!!')
        return False
    

    # target_option is set, then build project
    lipo_dst_lib = INSTALL_PATH + f'/{PROJECT_NAME_LOWER}'
    libtool_os_dst_lib = INSTALL_PATH + f'/{PROJECT_NAME_LOWER}_os'
    libtool_simulator_dst_lib = INSTALL_PATH + f'/{PROJECT_NAME_LOWER}_simulator'
    dst_framework_path = INSTALL_PATH + f'/{PROJECT_NAME_LOWER}.framework'
    dst_framework_headers = IOS_BUILD_COPY_HEADER_FILES
    # add static libs
    total_src_lib = glob.glob(INSTALL_PATH + '/*.a')
    rm_src_lib = []
    libtool_src_lib = [x for x in total_src_lib if x not in rm_src_lib]
    print(f'libtool src lib: {len(libtool_src_lib)}/{len(total_src_lib)}')

    if not libtool_libs(libtool_src_lib, libtool_os_dst_lib):
        return False

    clean(BUILD_OUT_PATH)
    os.chdir(BUILD_OUT_PATH)

    build_cmd = IOS_BUILD_SIMULATOR_CMD % target_option
    ret = os.system(build_cmd)

    os.chdir(SCRIPT_PATH)
    if ret != 0:
        print('!!!!!!!!!!!build simulator fail!!!!!!!!!!!!!!!')
        return False

    if not libtool_libs(glob.glob(INSTALL_PATH + '/*.a'), libtool_simulator_dst_lib):
        return False

    # os
    lipo_src_libs = []
    lipo_src_libs.append(libtool_os_dst_lib)
    os_lipo_dst_lib = INSTALL_PATH + f'/os/{PROJECT_NAME_LOWER}'
    if not libtool_libs(lipo_src_libs, os_lipo_dst_lib):
        return False
    os_dst_framework_path = INSTALL_PATH + f'/os/{PROJECT_NAME_LOWER}.framework'
    make_static_framework(os_lipo_dst_lib, os_dst_framework_path, dst_framework_headers, './')
    # simulator
    lipo_src_libs = []
    lipo_src_libs.append(libtool_simulator_dst_lib)
    simulator_lipo_dst_lib = INSTALL_PATH + f'/simulator/{PROJECT_NAME_LOWER}'
    if not libtool_libs(lipo_src_libs, simulator_lipo_dst_lib):
        return False
    simulator_dst_framework_path = INSTALL_PATH + f'/simulator/{PROJECT_NAME_LOWER}.framework'
    make_static_framework(simulator_lipo_dst_lib, simulator_dst_framework_path, dst_framework_headers, './')
    # xcframework
    dst_xcframework_path = INSTALL_PATH + f'/{PROJECT_NAME_LOWER}.xcframework'
    if not make_xcframework(os_dst_framework_path, simulator_dst_framework_path, dst_xcframework_path):
        return False

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('==================Output========================')
    print(dst_xcframework_path)

    after_time = time.time()

    print(f"use time: {int(after_time - before_time)} s")
    return True

def gen_ios_project(target_option='', tag=''):
    print('==================gen_ios_project========================')
    # generate verinfo.h
    gen_project_revision_file(PROJECT_NAME, OUTPUT_VERINFO_PATH, get_version_name(SCRIPT_PATH), tag)

    clean(BUILD_OUT_PATH)
    os.chdir(BUILD_OUT_PATH)

    cmd = GEN_IOS_OS_PROJ % target_option
    ret = os.system(cmd)
    os.chdir(SCRIPT_PATH)
    if ret != 0:
        print('!!!!!!!!!!!gen fail!!!!!!!!!!!!!!!')
        return False

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('==================Output========================')
    print(f'project file: {SCRIPT_PATH}/{BUILD_OUT_PATH}')

    return True

def main(target_option='', tag=''):
    print(f"main tag {tag}")
    build_ios(target_option, tag)

if __name__ == '__main__':
    PROJECT_NAME_LOWER = PROJECT_NAME.lower()
    while True:
         if len(sys.argv) >= 2:
            num = sys.argv[1]
         else:
            archs = set(['armeabi-v7a'])
            num = str(input(
                'Enter menu:'
                + f'\n1. Clean && build iOS {PROJECT_NAME_LOWER}.'
                + f'\n2. Gen iOS {PROJECT_NAME_LOWER} Project.'
                + f'\n3. Exit.'))
         print(f'==================iOS Choose num: {num}==================')
         if num == '1':
             main(tag=num)
             break
         elif num == '2':
             gen_ios_project()
             break
         else:
             break



