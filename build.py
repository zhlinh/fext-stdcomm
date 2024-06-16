#!/usr/bin/env python3
# -- coding: utf-8 --
#
# build.py
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

import os
import platform
import sys
import subprocess
import time
import re
import shutil
import zipfile
import glob
from threading import Timer

# import config file, i.e. "CONFIG_" prefixed global variables
from build_config import *

CI_IS_RELEASE = os.environ.get("CI_IS_RELEASE") == "true"
CI_IS_TAG = os.environ.get("CI_IS_TAG") == "true"
# config
CONFIG_IOS_TASK_TAG = "1"
CONFIG_MACOS_TASK_TAG = "1"
CONFIG_WINDOWS_TASK_TAG = "1"
CONFIG_LINUX_TASK_TAG = "1"
CONFIG_DOCS_TASK_TAG = "1"
CONFIG_INCLUDE_TASK_TAG = "1"

print(f"======={CONFIG_PROJECT_NAME} build INIT=======")
LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_PATH = f"{LOCAL_PATH}/{CONFIG_PROJECT_RELATIVE_PATH}"
print(f"LOCAL_PATH:{LOCAL_PATH}")
print(f"PROJECT_ROOT_PATH:{PROJECT_ROOT_PATH}")


def replace_in_file(file_path: str, src: str, dst: str):
    with open(file_path, "r+", encoding="UTF-8") as f:
        content = f.read()
        content = re.sub(src, dst, content)
        f.seek(0)
        f.write(content)
        f.truncate()


def decode_bytes(input: bytes) -> str:
    err_msg = ""
    try:
        err_msg = bytes.decode(input, "UTF-8")
    except UnicodeDecodeError:
        err_msg = bytes.decode(input, "GBK")
    return err_msg


def compare_version(v1: str, v2: str) -> bool:
    """
    compare version
    """
    def to_tuple(version):
        return tuple(
            int(val) if val.isdigit() else 0 for val in str(version).split('.'))

    return to_tuple(v1) > to_tuple(v2)


def run_cmd(command: str, timeout_second: int = 3600,
    check_result: bool = False) -> tuple:
    print(f"Command:[{command}] executed start")
    start_mills = int(time.time() * 1000)
    if sys.platform.startswith("win"):
        # Windows set console character set to UTF-8
        subprocess.call("chcp 65001", shell=True)
    compile_popen = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    timer = Timer(timeout_second, lambda process: process.kill(),
                  [compile_popen])
    try:
        timer.start()
        stdout, stderr = compile_popen.communicate()
    finally:
        timer.cancel()
    err_code = compile_popen.returncode
    err_msg = decode_bytes(stdout)
    if err_code == -9:
        if not err_msg:
            if stderr:
                err_msg = decode_bytes(stderr)
            if not err_msg:
                use_time = int(time.time() * 1000) - start_mills
                err_msg = f"Failed for timeout({err_code}), use_time: {use_time}ms"
    if err_code == 0:
        print(f"Command:[{command}] executed successfully!")
        print(f"Result:\n{err_msg}")
    else:
        print(f"Command:[{command}] failed with error code:{err_code}")
        print(f"Result:\n{err_msg}")
        if check_result:
            sys.exit(err_code)
    return err_code, err_msg.strip()


BRANCH_NAME = run_cmd("git symbolic-ref short -q HEAD")[1]
VERSION_CODE = run_cmd("git rev-list HEAD --count")[1]
REVISION = run_cmd("git rev-parse --short HEAD")[1]
TIME_INFO = time.strftime("%Y-%m-%d", time.localtime(int(
    run_cmd("git log -n1 --format=%at")[1])
))
PUBLISH_SUFFIX = "release"

# check build gradle file
BUILD_GRADLE_FILE = f"{PROJECT_ROOT_PATH}/build.gradle.kts"
if not os.path.exists(BUILD_GRADLE_FILE):
    BUILD_GRADLE_FILE = f"{PROJECT_ROOT_PATH}/build.gradle"

VERSION_FILE = f"{PROJECT_ROOT_PATH}/gradle/libs.versions.toml"

CI_CUR_VER = os.environ.get("CI_CUR_VER") or None
if not CI_CUR_VER:
    with open(VERSION_FILE, "r", encoding='UTF-8') as f:
        for line in f:
            match = re.search(r'commMainProject.*"(\d+\.\d+\.\d+)"', line)
            if match:
              CI_CUR_VER = match.group(1)
              break
else:
    CI_CUR_VER = CI_CUR_VER.strip('"')

release_src = "commIsRelease.*=.*\".*\""
release_dst = "commIsRelease = \"{}\""

if CI_IS_RELEASE:
    PUBLISH_SUFFIX = "release"
    tag = f"v{CI_CUR_VER}"
    # change commIsRelease to true
    replace_in_file(VERSION_FILE, release_src, release_dst.format("true"))
else:
    latest_tag = run_cmd("git rev-list --tags --no-walk --max-count=1")[1]
    count_from_latest_tag = run_cmd(f"git rev-list {latest_tag}..HEAD --count")[
        1]
    if run_cmd("git diff --stat")[1]:
        workspace_status = "-dirty"
    else:
        workspace_status = ""
    PUBLISH_SUFFIX = f"beta.{count_from_latest_tag}{workspace_status}"
    tag = f"v{CI_CUR_VER}-{PUBLISH_SUFFIX}"
    # change commIsRelease to false
    replace_in_file(VERSION_FILE, release_src, release_dst.format("false"))

version_with_code = f"v{CI_CUR_VER}_{VERSION_CODE}_{REVISION}"
print(f"cur_ver:{CI_CUR_VER}")
print(f"publish_suffix:{PUBLISH_SUFFIX}")
print(f"time_info:{TIME_INFO}")
print(f"version_code:{VERSION_CODE}")
print(f"revision:{REVISION}")
print(f"branch_name:{BRANCH_NAME}")
print(f"version_with_code:{version_with_code}")
print(f"tag:{tag}")

# Get the python command
if sys.platform.startswith("win"):
    # windows use 'python' command
    PYTHON_CMD = "python"
else:
    if shutil.which("python3") is not None:
        # use 'python3' command if it exists
        PYTHON_CMD = "python3"
    else:
        PYTHON_CMD = "python"


class BuildTask():
    def __init__(self):
        pass

    def build(self):
        pass


class TagBuildTask(BuildTask):
    def build(self):
        # TAG
        if CI_IS_RELEASE:
            print(f"======={CONFIG_PROJECT_NAME} build start add tag=======")
            run_cmd(f"git tag -a {tag} -F {LOCAL_PATH}/bin/{tag}",
                    check_result=True)
            run_cmd("git status")
            run_cmd(f"git show {tag} | head",
                    check_result=True)
            os.system(f"git push origin {tag}")
            print(f"======={CONFIG_PROJECT_NAME} build finish push tag=======")


class AndroidBuildTask(BuildTask):
    def build(self):
        print("=======$CONFIG_PROJECT_NAME build [Android] start=======")
        # start build
        run_cmd(f"chmod +x {PROJECT_ROOT_PATH}/gradlew")
        os.chdir(PROJECT_ROOT_PATH)
        run_cmd(f"{PROJECT_ROOT_PATH}/gradlew clean")
        run_cmd(f"{PROJECT_ROOT_PATH}/gradlew {CONFIG_GRADLE_TASK_NAME} --info",
                check_result=True)
        os.chdir(LOCAL_PATH)

        run_cmd(f"ls -l {PROJECT_ROOT_PATH}/bin/")
        print(
            "=======$CONFIG_PROJECT_NAME build start copy [Android] bin files=======")
        if not os.path.exists(f"{LOCAL_PATH}/bin"):
            os.mkdir(f"{LOCAL_PATH}/bin")
        for file in os.listdir(f"{PROJECT_ROOT_PATH}/bin"):
            newfile = file.replace("release", PUBLISH_SUFFIX)
            os.rename(f"{PROJECT_ROOT_PATH}/bin/{file}",
                      f"{PROJECT_ROOT_PATH}/bin/{newfile}")
        run_cmd(f"cp -r {PROJECT_ROOT_PATH}/bin/* {LOCAL_PATH}/bin/")
        print(
            f"======={CONFIG_PROJECT_NAME} build dir [Android] bin outputs=======")
        for file in os.listdir(f"{LOCAL_PATH}/bin"):
            print(f"{LOCAL_PATH}/bin/{file}")
        os.chdir(LOCAL_PATH)


class IOSBuildTask(BuildTask):
    def build(self):
        print(f"======={CONFIG_PROJECT_NAME} build [iOS] start=======")
        os.chdir(PROJECT_ROOT_PATH)
        run_cmd(f"{PYTHON_CMD} build_ios.py {CONFIG_IOS_TASK_TAG}",
                check_result=True)
        os.chdir(LOCAL_PATH)

        # change to lowercase
        target_framework = CONFIG_PROJECT_NAME.lower()
        os.chdir(f"{PROJECT_ROOT_PATH}/cmake_build/iOS/Darwin.out/")
        os.system(f"ls -l")
        print(
            f"======={CONFIG_PROJECT_NAME} build start copy [iOS] bin files=======")
        if not os.path.exists(f"{LOCAL_PATH}/bin"):
            os.mkdir(f"{LOCAL_PATH}/bin")

        source_dir = f"./{target_framework}.xcframework"
        if not os.path.exists(source_dir):
            source_dir = f"./{target_framework}.framework"
        shutil.make_archive(
            f"{LOCAL_PATH}/bin/{CONFIG_PROJECT_NAME}_IOS_FRAMEWORK-{CI_CUR_VER}-{PUBLISH_SUFFIX}",
            "zip",
            ".",
            source_dir
        )
        shutil.make_archive(
            f"{LOCAL_PATH}/bin/(ARCHIVE)_{CONFIG_PROJECT_NAME}_IOS_FRAMEWORK-{CI_CUR_VER}-{PUBLISH_SUFFIX}",
            "zip", ".")
        print(
            f"======={CONFIG_PROJECT_NAME} build dir [iOS] bin outputs=======")
        for file in os.listdir(f"{LOCAL_PATH}/bin"):
            print(f"{LOCAL_PATH}/bin/{file}")
        os.chdir(LOCAL_PATH)


class MacOSBuildTask(BuildTask):
    def build(self):
        print(f"======={CONFIG_PROJECT_NAME} build [macOS] start=======")
        os.chdir(PROJECT_ROOT_PATH)
        run_cmd(f"{PYTHON_CMD} build_macos.py {CONFIG_MACOS_TASK_TAG}",
                check_result=True)
        os.chdir(LOCAL_PATH)

        # change to lowercase
        target_framework = CONFIG_PROJECT_NAME.lower()
        os.chdir(f"{PROJECT_ROOT_PATH}/cmake_build/macOS/Darwin.out/")
        os.system("ls -l")
        print(
            f"======={CONFIG_PROJECT_NAME} build start copy [macOS] bin files=======")
        if not os.path.exists(f"{LOCAL_PATH}/bin"):
            os.mkdir(f"{LOCAL_PATH}/bin")
        source_dir = f"./{target_framework}.xcframework"
        if not os.path.exists(source_dir):
            source_dir = f"./{target_framework}.framework"
        shutil.make_archive(
            f"{LOCAL_PATH}/bin/{CONFIG_PROJECT_NAME}_MACOS_FRAMEWORK-{CI_CUR_VER}-{PUBLISH_SUFFIX}",
            "zip",
            ".",
            source_dir
        )
        shutil.make_archive(
            f"{LOCAL_PATH}/bin/(ARCHIVE)_{CONFIG_PROJECT_NAME}_MACOS_FRAMEWORK-{CI_CUR_VER}-{PUBLISH_SUFFIX}",
            "zip",
            ".")
        print(
            f"======={CONFIG_PROJECT_NAME} build dir [macOS] bin outputs=======")
        for file in os.listdir(f"{LOCAL_PATH}/bin"):
            print(f"{LOCAL_PATH}/bin/{file}")
        os.chdir(LOCAL_PATH)


class WindowsBuildTask(BuildTask):
    def build(self):
        print(f"======={CONFIG_PROJECT_NAME} build [Windows] start=======")
        os.chdir(PROJECT_ROOT_PATH)
        run_cmd(f"{PYTHON_CMD} build_windows.py {CONFIG_WINDOWS_TASK_TAG}",
                check_result=True)
        os.chdir(LOCAL_PATH)

        # change to lowercase
        target_framework = CONFIG_PROJECT_NAME.lower()
        os.chdir(f"{PROJECT_ROOT_PATH}/cmake_build/Windows/Windows.out/")
        os.system("ls -l")
        print(
            f"======={CONFIG_PROJECT_NAME} build start copy [Windows] bin files=======")
        if not os.path.exists(f"{LOCAL_PATH}/bin"):
            os.mkdir(f"{LOCAL_PATH}/bin")
        shutil.make_archive(
            f"{LOCAL_PATH}/bin/{CONFIG_PROJECT_NAME}_WINDOWS_LIB-{CI_CUR_VER}-{PUBLISH_SUFFIX}",
            "zip",
            ".",
            f"./{target_framework}.dir"
        )
        shutil.make_archive(
            f"{LOCAL_PATH}/bin/(ARCHIVE)_{CONFIG_PROJECT_NAME}_WINDOWS_LIB-{CI_CUR_VER}-{PUBLISH_SUFFIX}",
            "zip",
            ".")
        print(
            f"======={CONFIG_PROJECT_NAME} build dir [Windows] bin outputs=======")
        for file in os.listdir(f"{LOCAL_PATH}/bin"):
            print(f"{LOCAL_PATH}/bin/{file}")
        os.chdir(LOCAL_PATH)


class LinuxBuildTask(BuildTask):
    def build(self):
        print(f"======={CONFIG_PROJECT_NAME} build [Linux] start=======")
        os.chdir(PROJECT_ROOT_PATH)
        run_cmd(f"{PYTHON_CMD} build_linux.py {CONFIG_LINUX_TASK_TAG}",
                check_result=True)
        os.chdir(LOCAL_PATH)

        # change to lowercase
        target_framework = CONFIG_PROJECT_NAME.lower()
        os.chdir(f"{PROJECT_ROOT_PATH}/cmake_build/Linux/Linux.out/")
        os.system("ls")
        print(
            f"======={CONFIG_PROJECT_NAME} build start copy [Linux] bin files=======")
        if not os.path.exists(f"{LOCAL_PATH}/bin"):
            os.mkdir(f"{LOCAL_PATH}/bin")
        shutil.make_archive(
            f"{LOCAL_PATH}/bin/{CONFIG_PROJECT_NAME}_LINUX_LIB-{CI_CUR_VER}-{PUBLISH_SUFFIX}",
            "zip",
            ".",
            f"./{target_framework}.dir"
        )
        shutil.make_archive(
            f"{LOCAL_PATH}/bin/(ARCHIVE)_{CONFIG_PROJECT_NAME}_LINUX_LIB-{CI_CUR_VER}-{PUBLISH_SUFFIX}",
            "zip",
            ".")
        print(
            f"======={CONFIG_PROJECT_NAME} build dir [Linux] bin outputs=======")
        for file in os.listdir(f"{LOCAL_PATH}/bin"):
            print(f"{LOCAL_PATH}/bin/{file}")
        os.chdir(LOCAL_PATH)


class IncludeBuildTask(BuildTask):
    def build(self):
        print(f"======={CONFIG_PROJECT_NAME} build [include] start=======")
        os.chdir(PROJECT_ROOT_PATH)
        run_cmd(f"{PYTHON_CMD} build_include.py {CONFIG_INCLUDE_TASK_TAG}",
                check_result=True)
        os.chdir(LOCAL_PATH)
        system_name = platform.system()

        # change to lowercase
        target_framework = CONFIG_PROJECT_NAME.lower()
        install_path = f"{PROJECT_ROOT_PATH}/cmake_build/Include/{system_name}.out/"
        os.chdir(install_path)
        os.system("ls")
        print(
            f"======={CONFIG_PROJECT_NAME} build start copy [include] bin files=======")
        if not os.path.exists(f"{LOCAL_PATH}/bin"):
            os.mkdir(f"{LOCAL_PATH}/bin")
        shutil.make_archive(
            f"{LOCAL_PATH}/bin/{CONFIG_PROJECT_NAME}_INCLUDE-{CI_CUR_VER}-{PUBLISH_SUFFIX}",
            "zip",
            ".",
            f"./include"
        )
        print(
            f"======={CONFIG_PROJECT_NAME} build dir [include] bin outputs=======")
        for file in os.listdir(f"{LOCAL_PATH}/bin"):
            print(f"{LOCAL_PATH}/bin/{file}")
        os.chdir(LOCAL_PATH)


class DocsBuildTask(BuildTask):
    def build(self):
        print(f"======={CONFIG_PROJECT_NAME} build [docs] start=======")
        os.chdir(PROJECT_ROOT_PATH)
        run_cmd(f"{PYTHON_CMD} build_docs.py {CONFIG_DOCS_TASK_TAG}",
                check_result=True)
        os.chdir(LOCAL_PATH)
        system_name = platform.system()

        # change to lowercase
        target_framework = CONFIG_PROJECT_NAME.lower()
        install_path = f"{PROJECT_ROOT_PATH}/cmake_build/Docs/{system_name}.out/"
        os.chdir(install_path)
        os.system("ls")
        print(
            f"======={CONFIG_PROJECT_NAME} build start copy [docs] bin files=======")
        if not os.path.exists(f"{LOCAL_PATH}/bin"):
            os.mkdir(f"{LOCAL_PATH}/bin")
        shutil.make_archive(
            f"{LOCAL_PATH}/bin/{CONFIG_PROJECT_NAME}_DOCS-{CI_CUR_VER}-{PUBLISH_SUFFIX}",
            "zip",
            ".",
            f"./_html"
        )
        print(
            f"======={CONFIG_PROJECT_NAME} build dir [docs] bin outputs=======")
        for file in os.listdir(f"{LOCAL_PATH}/bin"):
            print(f"{LOCAL_PATH}/bin/{file}")
        os.chdir(LOCAL_PATH)


class CCGOBuildTask(BuildTask):
    def build(self):
        print(f"======={CONFIG_PROJECT_NAME} build [ccgo] start=======")
        os.chdir(LOCAL_PATH)

        # change to lowercase
        target_framework = CONFIG_PROJECT_NAME.lower()
        source_path = f"{LOCAL_PATH}/source_sdk/all/"
        os.chdir(source_path)
        os.system("ls")
        print(
            f"======={CONFIG_PROJECT_NAME} build start copy [ccgo] bin files=======")
        output_dir = "bin"
        if not os.path.exists(f"{LOCAL_PATH}/{output_dir}"):
            os.rmtree(f"{LOCAL_PATH}/{output_dir}")
        if not os.path.exists(f"{LOCAL_PATH}/{output_dir}"):
            os.mkdir(f"{LOCAL_PATH}/{output_dir}")
        os.chdir(LOCAL_PATH)
        # list of dictionaries containing the configurations
        configurations = [
            {
                "source_pattern": fr"{CONFIG_PROJECT_NAME}_INCLUDE-(.*).zip",
                "target_base_dir": f"{output_dir}/{target_framework}/include/",
                "target_mappings": {
                    f"include/{target_framework}": target_framework,
                }
            },
            {
                "source_pattern": fr"{CONFIG_PROJECT_NAME}_ANDROID_SDK-(.*).aar",
                "target_base_dir": f"{output_dir}/{target_framework}/lib/android/",
                "target_mappings": {
                    f"jni/arm64-v8a/lib{target_framework}.so": f"arm64-v8a/lib{target_framework}.so",
                    f"jni/armeabi-v7a/lib{target_framework}.so": f"armeabi-v7a/lib{target_framework}.so",
                    f"jni/x86_64/lib{target_framework}.so": f"x86_64/lib{target_framework}.so",
                }
            },
            {
                "source_pattern": fr"{CONFIG_PROJECT_NAME}_WINDOWS_LIB-(.*).zip",
                "target_base_dir": f"{output_dir}/{target_framework}/lib/windows/",
                "target_mappings": {
                    f"{target_framework}.dir/x64/{target_framework}.lib": f"x64/{target_framework}.lib",
                    f"{target_framework}.dir/x86/{target_framework}.lib": f"x86/{target_framework}.lib"
                }
            },
            {
                "source_pattern": fr"{CONFIG_PROJECT_NAME}_IOS_FRAMEWORK-(.*).zip",
                "target_base_dir": f"{output_dir}/{target_framework}/lib/ios/",
                "target_mappings": {
                    f"{target_framework}.framework" : f"{target_framework}.framework",
                    f"{target_framework}.xcframework" : f"{target_framework}.xcframework",
                }
            },
            {
                "source_pattern": fr"{CONFIG_PROJECT_NAME}_MACOS_FRAMEWORK-(.*).zip",
                "target_base_dir": f"{output_dir}/{target_framework}/lib/macos/",
                "target_mappings": {
                    f"{target_framework}.framework" : f"{target_framework}.framework",
                    f"{target_framework}.xcframework" : f"{target_framework}.xcframework",
                }
            },
            {
                "source_pattern": fr"{CONFIG_PROJECT_NAME}_LINUX_LIB-(.*).zip",
                "target_base_dir": f"{output_dir}/{target_framework}/lib/linux/",
                "target_mappings": {
                    f"{target_framework}.dir/{target_framework}.a": f"{target_framework}.a"
                }
            }
        ]

        version_desc = ""
        # create target directories
        for config in configurations:
            print(config)
            print("-----------")
            os.makedirs(config["target_base_dir"], exist_ok=True)
            # extract library files
            for file in os.listdir(source_path):
                match = re.match(config["source_pattern"], file)
                if match:
                    version_desc = match.group(1) if compare_version(match.group(1), version_desc) else version_desc
                    with zipfile.ZipFile(os.path.join(source_path, file), "r") as zip_ref:
                        zip_ref.extractall("temp")
                        for from_path, to_path in config["target_mappings"].items():
                            full_from_path_reg = os.path.join("temp", from_path)
                            files = glob.glob(full_from_path_reg)
                            if not files:
                                continue
                            full_from_path = files[0]
                            full_to_path = os.path.join(config["target_base_dir"], to_path)
                            # override
                            if os.path.exists(full_to_path):
                                shutil.rmtree(full_to_path)
                            if full_to_path.rfind("/") != -1 and not os.path.exists(full_to_path[:full_to_path.rfind("/")]):
                                os.makedirs(full_to_path[:full_to_path.rfind("/")], exist_ok=True)
                            if os.path.isfile(full_from_path):
                                shutil.copy(full_from_path, full_to_path)
                            else:
                                shutil.copytree(full_from_path, full_to_path)
                        shutil.rmtree("temp")

        if not version_desc:
            version_desc = CI_CUR_VER
        # the output directory
        os.chdir(output_dir)
        output_zip_name = f"{CONFIG_PROJECT_NAME}_CCGO-{version_desc}.zip"
        # compress the ccgo zip
        with zipfile.ZipFile(output_zip_name, "w") as zip_ref:
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if not file.endswith(".zip"):
                        zip_ref.write(os.path.join(root, file))
        # compress the zip of all platforms
        os.chdir(source_path)
        shutil.make_archive(
            f"{LOCAL_PATH}/{output_dir}/{CONFIG_PROJECT_NAME}_ALL-{version_desc}",
            "zip",
            ".",
            f"."
        )
        print(
            f"======={CONFIG_PROJECT_NAME} build dir [ccgo] bin outputs=======")
        for file in os.listdir(f"{LOCAL_PATH}/bin"):
            print(f"{LOCAL_PATH}/bin/{file}")
        os.chdir(LOCAL_PATH)


ALL_BUILD_ITEMS_MAP = {
    "TAG": TagBuildTask(),
    "ANDROID": AndroidBuildTask(),
    "IOS": IOSBuildTask(),
    "MACOS": MacOSBuildTask(),
    "WINDOWS": WindowsBuildTask(),
    "LINUX": LinuxBuildTask(),
    "INCLUDE": IncludeBuildTask(),
    "DOCS": DocsBuildTask(),
    "CCGO": CCGOBuildTask(),
}
KEY_BUILD_PREFIX = "CI_BUILD_"
WITH_PREFIX_ALL_BUILD_ITEMS = list(
    map(lambda x: KEY_BUILD_PREFIX + x, ALL_BUILD_ITEMS_MAP.keys()))
TARGET_WITH_PREFIX_ALL_BUILD_ITEMS = []


class BuildTaskFactory():
    @staticmethod
    def get_build_task(build_item: str) -> BuildTask:
        return (ALL_BUILD_ITEMS_MAP.get(build_item.upper())
                or ALL_BUILD_ITEMS_MAP.get(
                build_item.replace(KEY_BUILD_PREFIX, "").upper())
                )

    @staticmethod
    def get_all_build_items() -> list:
        return list(ALL_BUILD_ITEMS_MAP.keys())


def main():
    print(f"======={CONFIG_PROJECT_NAME} build ENV=======")
    print(f"ANDROID_HOME:{os.environ.get('ANDROID_HOME')}")
    print(f"JAVA_HOME:{os.environ.get('JAVA_HOME')}")
    print(f"ANDROID_NDK_HOME:{os.environ.get('ANDROID_NDK_HOME')}")
    print(f"CMAKE_HOME:{os.environ.get('CMAKE_HOME')}")

    # read parameters from shell
    if len(sys.argv) > 1:
        for item in sys.argv:
            if item in WITH_PREFIX_ALL_BUILD_ITEMS:
                TARGET_WITH_PREFIX_ALL_BUILD_ITEMS.append(item)
                print(f"from shell parm {item} = true")
    else:
        for item in WITH_PREFIX_ALL_BUILD_ITEMS:
            raw_ignore_items = ["TAG"]
            with_prefix_ignore_items = list(
                map(lambda x: KEY_BUILD_PREFIX + x, raw_ignore_items))
            ignore_items = raw_ignore_items + with_prefix_ignore_items
            if item not in ignore_items:
                TARGET_WITH_PREFIX_ALL_BUILD_ITEMS.append(item)
                print(f"from default parm {item} = true")

    print(f"======={CONFIG_PROJECT_NAME} build define consts=======")
    print(f"CI_IS_RELEASE:{CI_IS_RELEASE}")
    print(f"CI_IS_TAG:{CI_IS_TAG}")

    print(f"======={CONFIG_PROJECT_NAME} build mkdir bin=======")

    os.chdir(LOCAL_PATH)
    # bin dir
    if os.path.exists(f"{LOCAL_PATH}/bin"):
        shutil.rmtree(f"{LOCAL_PATH}/bin")
    os.mkdir(f"{LOCAL_PATH}/bin")

    # generate tag file for archiving
    with open(f"{LOCAL_PATH}/bin/{tag}", "w", encoding="UTF-8") as f:
        f.write(f"{tag} info:\n-----------------------------"
                + f"\n\nVERSION_NAME={CI_CUR_VER}"
                + f"\nVERSION_CODE={VERSION_CODE}"
                + f"\nREVISION={REVISION}"
                + f" \nBRANCH_NAME={BRANCH_NAME}"
                + f" \nTAG={tag}"
                + f" \nDATETIME={TIME_INFO}"
                + f" \n\n-----------------------------")

    if not TARGET_WITH_PREFIX_ALL_BUILD_ITEMS:
        print(f"======={CONFIG_PROJECT_NAME} build failed, not found {sys.argv}=======")
        return

    # start build
    for task in TARGET_WITH_PREFIX_ALL_BUILD_ITEMS:
        print(f"======={CONFIG_PROJECT_NAME} build start {task}=======")
        build_task = BuildTaskFactory.get_build_task(task)
        if not build_task:
            print(f"======={CONFIG_PROJECT_NAME} build {task} not found=======")
            continue
        build_task.build()
        print(f"======={CONFIG_PROJECT_NAME} build finish {task}=======")


if __name__ == "__main__":
    main()
