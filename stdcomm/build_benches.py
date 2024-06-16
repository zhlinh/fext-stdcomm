#!/usr/bin/env python3
# -- coding: utf-8 --
#
# build_benches.py
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

BUILD_OUT_PATH = 'cmake_build/Benches'
CMAKE_SYSTEM_NAME = platform.system()
INSTALL_PATH = BUILD_OUT_PATH + '/' + CMAKE_SYSTEM_NAME + '.out'

BENCHMARK_BUILD_CMD = 'cmake ../.. -DCMAKE_BUILD_TYPE=Release -DBENCHMARK_SUPPORT=ON && make -j8 && make install'

def build_benchmark(incremental, tag=''):
    before_time = time.time()
    print('==================build_benchmark with tag %s========================' % tag)

    clean(BUILD_OUT_PATH, incremental)
    os.chdir(BUILD_OUT_PATH)

    # generate verinfo.h
    gen_project_revision_file(PROJECT_NAME, OUTPUT_VERINFO_PATH, get_version_name(SCRIPT_PATH), tag,
                              incremental=incremental)

    ret = os.system(BENCHMARK_BUILD_CMD)
    os.chdir(SCRIPT_PATH)
    if ret != 0:
        print('!!!!!!!!!!!build benchmark fail!!!!!!!!!!!!!!!')
        return False

    clean(BUILD_OUT_PATH, incremental)
    os.chdir(BUILD_OUT_PATH)

    dst_target_path = INSTALL_PATH

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('==================Output========================')
    print(dst_target_path)

    after_time = time.time()

    print(f"use time: {int(after_time - before_time)} s")
    return True

def run_benchmark(incremental, tag=''):
    if not build_benchmark(incremental, tag):
      return False
    os.chdir(SCRIPT_PATH)
    for fpath, dirs, fs in os.walk(INSTALL_PATH):
        for file_name in fs:
            file = os.path.join(fpath, file_name)
            if file.find('_benchmark') >= 0:
                ret = os.system(file)
                if ret != 0:
                    print('!!!!!!!!!!!run benchmark %s fail!!!!!!!!!!!!!!!' % file)
                    return False
    return True

def main(choose):
    print(f'==========Choose num: {choose}===========')

    result = True
    if choose == '1':
        result = build_benchmark(False, choose)
    elif choose == '2':
        result = run_benchmark(True, choose)
    elif choose == '3':
        return
    else:
        result = build_benchmark(False, choose)

    if not result:
        raise RuntimeError('Exception occurs when build or run benchmark')

if __name__ == '__main__':
    while True:
        if len(sys.argv) >= 2:
            main(sys.argv[1])
            break
        else:
            num = str(input(
                f'Enter menu:\n1. Clean && build {PROJECT_NAME_LOWER} benchmark\n2. Run benchmark\n3. Exit\n'))
            main(num)
            break
