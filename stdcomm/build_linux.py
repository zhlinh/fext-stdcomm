#!/usr/bin/env python3
# -- coding: utf-8 --
#
# build_linux.py
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
import sys
import glob

from build_utils import *


SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]
# dir name as project name
PROJECT_NAME = os.path.basename(SCRIPT_PATH).upper()
PROJECT_NAME_LOWER = PROJECT_NAME.lower()
PROJECT_RELATIVE_PATH = PROJECT_NAME.lower()

BUILD_OUT_PATH = 'cmake_build/Linux'
INSTALL_PATH = BUILD_OUT_PATH + '/Linux.out'

BUILD_CMD = 'cmake ../.. -DCMAKE_BUILD_TYPE=Release && make -j8 && make install'

GEN_PROJECT_CMD = 'cmake ../.. -G "CodeLite - Unix Makefiles"'


def build_linux(target_option='', tag=''):
    before_time = time.time()
    print('==================build_linux========================')
    # generate verinfo.h
    gen_project_revision_file(PROJECT_NAME, OUTPUT_VERINFO_PATH, get_version_name(SCRIPT_PATH), tag)

    clean(BUILD_OUT_PATH)
    os.chdir(BUILD_OUT_PATH)

    ret = os.system(BUILD_CMD)
    os.chdir(SCRIPT_PATH)
    if ret != 0:
        print('!!!!!!!!!!!build fail!!!!!!!!!!!!!!!')
        return False

    # add static libs
    libtool_src_libs = glob.glob(INSTALL_PATH + '/*.a')

    libtool_dst_lib = INSTALL_PATH + f'/{PROJECT_NAME_LOWER}.a'
    if not libtool_libs(libtool_src_libs, libtool_dst_lib):
        return False

    dst_framework_path = INSTALL_PATH + f'/{PROJECT_NAME_LOWER}.dir'
    make_static_framework(libtool_dst_lib, dst_framework_path, LINUX_BUILD_COPY_HEADER_FILES, './')

    print('==================Output========================')
    print(dst_framework_path)

def gen_linux_project(target_option='', tag=''):
    print('==================gen_linux_project========================')
    # generate verinfo.h
    gen_project_revision_file(PROJECT_NAME, OUTPUT_VERINFO_PATH, get_version_name(SCRIPT_PATH), tag)

    clean(BUILD_OUT_PATH)
    os.chdir(BUILD_OUT_PATH)

    cmd = GEN_PROJECT_CMD
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
    build_linux(target_option=target_option, tag=tag)


if __name__ == '__main__':
    while True:
        if len(sys.argv) >= 2:
            num = sys.argv[1]
        else:
            num = str(input('Enter menu:'
                            + '\n1. Clean && Build Linux.'
                            + '\n2. Gen Linux CodeLite Project.'
                            + '\n3. Exit\n'))
        if num == '1':
            main(tag=num)
            break
        elif num == '2':
            gen_linux_project(tag=num)
            break
        elif num == '3':
            break
        else:
            main()
            break
