#!/usr/bin/env python3
# -- coding: utf-8 --
#
# build_android.py
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
import platform
import shutil
import sys
import time

from build_utils import *


SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]
# dir name as project name
PROJECT_NAME = os.path.basename(SCRIPT_PATH).upper()
PROJECT_NAME_LOWER = PROJECT_NAME.lower()
PROJECT_RELATIVE_PATH = PROJECT_NAME.lower()

if system_is_windows():
    ANDROID_GENERATOR = '-G "Unix Makefiles"'
else:
    ANDROID_GENERATOR = ''

try:
    NDK_ROOT = os.environ['NDK_ROOT']
except KeyError as identifier:
    NDK_ROOT = ''

BUILD_OUT_PATH = 'cmake_build/Android'
ANDROID_LIBS_INSTALL_PATH = BUILD_OUT_PATH + '/'
ANDROID_BUILD_CMD = ('cmake "%s" %s -DANDROID_ABI="%s" '
                     '-DCMAKE_BUILD_TYPE=Release '
                     '-DCMAKE_TOOLCHAIN_FILE=%s/build/cmake/android.toolchain.cmake '
                     '-DANDROID_TOOLCHAIN=clang '
                     '-DANDROID_NDK=%s '
                     '-DANDROID_PLATFORM=android-19 '
                     '-DANDROID_STL="c++_shared" %s '
                     '&& cmake --build . --config Release -- -j8')
ANDROID_SYMBOL_PATH = f'{ANDROID_PROJECT_PATH}/obj/local/'
ANDROID_LIBS_PATH = f'{ANDROID_PROJECT_PATH}/libs/'

ANDROID_STRIP_FILE = {
    'armeabi-v7a': NDK_ROOT + f"/toolchains/llvm/prebuilt/{get_ndk_host_tag()}/bin/llvm-strip",
    'x86': NDK_ROOT + f"/toolchains/llvm/prebuilt/{get_ndk_host_tag()}/bin/llvm-strip",
    'arm64-v8a': NDK_ROOT + f"/toolchains/llvm/prebuilt/{get_ndk_host_tag()}/bin/llvm-strip",
    'x86_64': NDK_ROOT + f"/toolchains/llvm/prebuilt/{get_ndk_host_tag()}/bin/llvm-strip",
}

# r25c location is different from r23 and below
ANDROID_STL_FILE = {
    'armeabi-v7a': NDK_ROOT + f"/toolchains/llvm/prebuilt/{get_ndk_host_tag()}/sysroot/usr/lib/arm-linux-androideabi/libc++_shared.so",
    'x86': NDK_ROOT + f"/toolchains/llvm/prebuilt/{get_ndk_host_tag()}/sysroot/usr/lib/i686-linux-android/libc++_shared.so",
    'arm64-v8a': NDK_ROOT + f"/toolchains/llvm/prebuilt/{get_ndk_host_tag()}/sysroot/usr/lib/aarch64-linux-android/libc++_shared.so",
    'x86_64': NDK_ROOT + f"/toolchains/llvm/prebuilt/{get_ndk_host_tag()}/sysroot/usr/lib/x86_64-linux-android/libc++_shared.so",
}



def get_android_strip_cmd(arch):
    strip_cmd = ANDROID_STRIP_FILE[arch]
    print(f'Android strip cmd:{strip_cmd}')
    return strip_cmd


def build_android(incremental, arch, target_option, tag):
    before_time = time.time()

    clean(os.path.join(SCRIPT_PATH, BUILD_OUT_PATH), incremental)
    os.chdir(os.path.join(SCRIPT_PATH, BUILD_OUT_PATH))

    build_cmd = ANDROID_BUILD_CMD % (
        SCRIPT_PATH, ANDROID_GENERATOR, arch, NDK_ROOT, NDK_ROOT, target_option)
    print("build cmd:[" + build_cmd + "]")
    ret = os.system(build_cmd)
    os.chdir(SCRIPT_PATH)

    if 0 != ret:
        print('!!!!!!!!!!!!!!!!!!build fail!!!!!!!!!!!!!!!!!!!!')
        return False

    symbol_path = ANDROID_SYMBOL_PATH
    lib_path = ANDROID_LIBS_PATH

    if not os.path.exists(symbol_path):
        os.makedirs(symbol_path)

    symbol_path = symbol_path + arch
    if os.path.exists(symbol_path):
        shutil.rmtree(symbol_path)

    os.mkdir(symbol_path)

    if not os.path.exists(lib_path):
        os.makedirs(lib_path)

    lib_path = lib_path + arch
    if os.path.exists(lib_path):
        shutil.rmtree(lib_path)

    os.mkdir(lib_path)

    for f in glob.glob(ANDROID_LIBS_INSTALL_PATH + "*.so"):
        if is_in_lib_list(f, ANDROID_MERGE_EXCLUDE_LIBS):
            continue
        shutil.copy(f, symbol_path)
        shutil.copy(f, lib_path)

    if "stdcomm" not in os.listdir('third_party'):
        # copy stl
        shutil.copy(ANDROID_STL_FILE[arch], symbol_path)
        shutil.copy(ANDROID_STL_FILE[arch], lib_path)

    # copy third_party/xxx/lib/android/yyy/*.so
    for f in os.listdir('third_party'):
        if f.endswith("comm") and (f not in ANDROID_MERGE_THIRD_PARTY_LIBS):
            # xxxcomm is not default to merge
            continue
        target_dir = f'third_party/{f}/lib/android/{arch}/'
        if not os.path.exists(target_dir):
            continue
        file_names = glob.glob(target_dir + "*.so")
        for file_name in file_names:
            if is_in_lib_list(file_name, ANDROID_MERGE_EXCLUDE_LIBS):
                continue
            shutil.copy(file_name, lib_path)

    # strip
    strip_cmd = get_android_strip_cmd(arch)
    for f in glob.glob(f'{lib_path}/*.so'):
        os.system(f'{strip_cmd} {f}')

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('==================Output========================')
    print(f'libs(release): {lib_path}')
    print(f'symbols(must store permanently): {symbol_path}')

    after_time = time.time()

    print(f"use time: {int(after_time - before_time)}")
    return True


def main(incremental, build_archs, target_option='', tag=''):
    if not check_ndk_env():
        raise RuntimeError(f"Exception occurs when check ndk env, please install ndk {get_ndk_desc()} and put in env NDK_ROOT")

    print(f"main tag {tag}")

    # generate verinfo.h
    gen_project_revision_file(PROJECT_NAME, OUTPUT_VERINFO_PATH, get_version_name(SCRIPT_PATH), tag,
                              incremental=incremental)

    for arch in build_archs:
        if not build_android(incremental, arch, target_option, tag):
            raise RuntimeError("Exception occurs when build android")


if __name__ == '__main__':
    while True:
        if len(sys.argv) >= 3:
            archs = sys.argv[2:]
            num = sys.argv[1]
        else:
            archs = set(['armeabi-v7a'])
            num = str(input(
                'Enter menu:\n'
                + f'1. Clean && build {PROJECT_NAME_LOWER}.\n'
                + f'2. Build incrementally {PROJECT_NAME_LOWER}.\n'
                + '3. Build for so test.\n'
                + '4. Exit.\n'))
        print(f'==================Android Choose num: {num}==================')
        if num == '1':
            main(False, archs, tag=num)
            break
        elif num == '2':
            main(True, archs, tag=num)
            break
        elif num == '3':
            # if test, then set it incremental
            cur_time = time.strftime("%H%M%S", time.localtime())
            main(False, archs,
                 target_option=f"-DCOMM_LOG_TAG_SUFFIX={cur_time}",
                 tag=num)
            break
        else:
            break 
