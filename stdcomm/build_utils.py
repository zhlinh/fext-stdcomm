#!/usr/bin/env python3
# -- coding: utf-8 --
#
# build_utils.py
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
import shutil
import time
import glob
import codecs
import io
import platform
import subprocess
import sys
import re
import zipfile

from build_config import *

def libtool_libs(src_libs, dst_lib):
    src_lib_str = ' '.join(src_libs)
    os.makedirs(dst_lib[:dst_lib.rfind("/")], exist_ok=True)

    if platform.system().lower() == 'darwin':
        # if is macos
        cmd = f"libtool -static -no_warning_for_no_symbols -o {dst_lib} {src_lib_str}"
    else:
        # if is linux
        # ar crs means
        # r option means add the target file to the static library. If the static library already contains a target file with the same name, it will replace it
        # c option means create a static library. If the static library does not exist, a new static library will be created; if the static library already exists, it will be updated
        # s option means create a symbol table in the static library. The symbol table contains the symbol information of all target files in the static library, which can be used for symbol resolution during linking
        if dst_lib.endswith('.a'):
            temp_static_lib = dst_lib
        else:
            temp_static_lib = f"{dst_lib}.a"
        cmd = f"gcc -r -nostdlib -Wl,--whole-archive -Wl,--allow-multiple-definition -o {dst_lib}.o {src_lib_str} && ar crs {temp_static_lib} {dst_lib}.o " \
              f"&& rm -f {dst_lib}.o"
        if temp_static_lib != dst_lib:
            cmd += f" && mv {temp_static_lib} {dst_lib}"

    print(cmd)
    ret = os.system(cmd)
    if ret != 0:
        print(f"!!!!!!!!!!! libtool {dst_lib} failed, cmd:['{cmd}'] !!!!!!!!!!!!!!!")
        return False

    return True


def lipo_libs(src_libs, dst_lib):
    if platform.system().lower() != 'darwin':
        # not macos
        return libtool_libs(src_libs, dst_lib)

    src_lib_str = ' '.join(src_libs)
    cmd = 'lipo -create %s -output %s' %(src_lib_str, dst_lib)
    ret = os.system(cmd)
    if ret != 0:
        print(f"!!!!!!!!!!! lipo_libs {dst_lib} failed, cmd:['{cmd}'] !!!!!!!!!!!!!!!")
        return False

    return True


def lipo_thin_libs(src_lib, dst_lib, archs):
    tmp_results = []
    for arch in archs:
        if len(archs) == 1:
            tmp_result = dst_lib
        else:
            tmp_result = dst_lib + '.' + arch

        cmd = f"lipo {src_lib} -thin {arch} -output {tmp_result}"
        ret = os.system(cmd)
        if ret != 0:
            print(f"!!!!!!!!!!!lipo_thin_libs {tmp_result} failed, cmd:{cmd}!!!!!!!!!!!!!!!")
            return False
        tmp_results.append(tmp_result)

    if len(archs) == 1:
        return True
    else:
        return lipo_libs(tmp_results, dst_lib)


GENERATE_DSYM_FILE_CMD = "dsymutil {src_dylib} -o {dst_dsym}"


def gen_dwarf_with_dsym(src_dylib, dst_dsym):
    os.system(GENERATE_DSYM_FILE_CMD.format(src_dylib=src_dylib, dst_dsym=dst_dsym))


def decode_bytes(input: bytes) -> str:
    err_msg = ""
    try:
        err_msg = bytes.decode(input, "UTF-8")
    except UnicodeDecodeError:
        err_msg = bytes.decode(input, "GBK")
    return err_msg


def exec_command(command):
    if sys.platform.startswith("win"):
        # windows set console charset to utf-8
        subprocess.call("chcp 65001", shell=True)
    compile_popen = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    compile_popen.wait()
    err_code = compile_popen.returncode
    err_msg =  decode_bytes(compile_popen.stdout.read())
    return err_code, err_msg


def remove_cmake_files(path):
    cmake_files = path + '/CMakeFiles'
    if os.path.exists(cmake_files):
        shutil.rmtree(cmake_files)

    make_files = path + '/Makefile'
    if os.path.isfile(make_files):
        os.remove(make_files)

    cmake_cache = path + '/CMakeCache.txt'
    if os.path.isfile(cmake_cache):
        os.remove(cmake_cache)

    for f in glob.glob(path + '/*.a'):
        os.remove(f)
    for f in glob.glob(path + '/*.so'):
        os.remove(f)
    for f in glob.glob(path + '/*.lib'):
        os.remove(f)
    for f in glob.glob(path + '/*.dylib'):
        os.remove(f)
    for f in glob.glob(path + '/*.xcframework'):
        shutil.rmtree(f)
    for f in glob.glob(path + '/*.framework'):
        shutil.rmtree(f)


def clean_except(path, except_list):
    for fpath, dirs, fs in os.walk(path):
        in_except = False
        for exc in except_list:
            if exc in fpath:
                in_except = True
                break
        if not in_except:
            remove_cmake_files(fpath)

    if not os.path.exists(path):
        os.makedirs(path)

def clean_unix(path, incremental=False):
    if not incremental:
        for fpath, dirs, fs in os.walk(path):
            remove_cmake_files(fpath)

    if not os.path.exists(path):
        os.makedirs(path)


def clean_windows(path, incremental):
    if not os.path.exists(path):
        os.makedirs(path)
        return

    if incremental:
        return

    try:
        if os.path.exists(path):
            shutil.rmtree(path)
            if not os.path.exists(path):
                os.makedirs(path)
    except Exception:
        pass


def clean(path, incremental=False):
    if system_is_windows():
        clean_windows(path, incremental)
    else:
        clean_unix(path, incremental)


def copy_file(src, dst):
    if not os.path.exists(src):
        # if src not exists, then return
        return
    if os.path.isfile(src):
        if dst.rfind("/") != -1 and not os.path.exists(dst[:dst.rfind("/")]):
            os.makedirs(dst[:dst.rfind("/")], exist_ok=True)
        shutil.copy(src, dst)
    else:
        # dirs_exist_ok = True needs python 3.8+
        shutil.copytree(src, dst)


def copy_file_mapping(header_file_mappings, header_files_src_base, header_files_dst_end):
    for (src, dst) in header_file_mappings.items():
        copy_file(header_files_src_base + src,
                  header_files_dst_end + "/" + dst + '/' + src[src.rfind("/"):])


def make_static_framework(src_lib, dst_framework, header_file_mappings, header_files_src_base='./'):
    if os.path.exists(dst_framework):
        shutil.rmtree(dst_framework)

    os.makedirs(dst_framework)
    shutil.copy(src_lib, dst_framework)

    framework_path = dst_framework + '/Headers'
    for (src, dst) in header_file_mappings.items():
        copy_file(header_files_src_base + src,
                  framework_path + "/" + dst + '/' + src[src.rfind("/"):])

    return True

def make_xcframework(os_framework, simulator_framework, dst_framework):
    cmd = "xcodebuild -create-xcframework"
    cmd += f" -framework {os_framework}"
    cmd += f" -framework {simulator_framework}"
    cmd += f" -output {dst_framework}"
    ret = os.system(cmd)
    if ret != 0:
        print(f"!!!!!!!!!!! make_xcframework {dst_framework} failed, cmd:['{cmd}'] !!!!!!!!!!!!!!!")
        return False

    return True


def get_ndk_desc():
    return "r25c"


def check_ndk_revision(revision):
    if revision >= "25.2":
        return True
    return False


def check_ndk_env():
    try:
        ndk_path = os.environ['NDK_ROOT']
    except KeyError as identifier:
        print("Error: ndk does not exist or you do not set it into NDK_ROOT.")
        return False

    if ndk_path is not None and ndk_path.strip():
        print(f"ndk path:{ndk_path}")

    if not ndk_path:
        print("Error: ndk does not exist or you do not set it into NDK_ROOT.")
        return False

    if not os.path.isfile(os.path.join(ndk_path, "source.properties")):
        print(f"Error: source.properties does not exist, make sure ndk's version=={get_ndk_desc()}")
        return False

    ndk_revision = None

    f = open(os.path.join(ndk_path, "source.properties"))
    line = f.readline()
    while line:
        if line.startswith("Pkg.Revision") and len(line.split("=")) == 2:
            ndk_revision = line.split("=")[1].strip()
        line = f.readline()

    f.close()

    if not ndk_revision or len(ndk_revision) < 4:
        print("Error: parse source.properties fail")
        return False

    if check_ndk_revision(ndk_revision[:4]):
        return True

    print(f"Error: make sure ndk's version == {get_ndk_desc()}, current is {ndk_revision[:4]}")
    return False


def get_ndk_host_tag():
    system_str = platform.system().lower()
    if system_architecture_is64():
        system_str = system_str + '-x86_64'
    return system_str


html_css = '''
<style type="text/css">
.description table {
    margin: 10px 0 15px 0;
    border-collapse: collapse;
    font-family: Helvetica, "Hiragino Sans GB", Arial, sans-serif;
    font-size: 11px;
    line-height: 16px;
    color: #737373;
    background-color: white;
    margin: 10px 12px 10px 12px;
}
.description td,th { border: 1px solid #ddd; padding: 3px 10px; }
.description th { padding: 5px 10px; }
.description a { color: #0069d6; }
.description a:hover { color: #0050a3; text-decoration: none; }
.description h5 { font-size: 14px; }
</style>
'''

html_table_template = '''
<div class="description">
<h5>{title}</h5>
<table>
<thead>
<tr>
<th align="left">KEY</th>
<th align="left">VALUE</th>
</tr>
</thead>
{table_rows}
</table>
</div>
'''

html_row_template = '''
<tr>
<td align="left">{key}</td>
<td align="left">{value}</td>
</tr>
'''


def parse_as_git(path):
    curdir = os.getcwd()
    os.chdir(path)
    revision = os.popen('git rev-parse --short HEAD').read().strip()
    path = os.popen('git rev-parse --abbrev-ref HEAD').read().strip()
    url = os.popen('git remote get-url origin').read().strip()
    # url remove oauth2
    pos = url.find('oauth2')
    if pos >= 0:
        pos_to_trim = url.find('@')
        if pos_to_trim >= 0:
            url = 'git' + url[pos_to_trim:]

    os.chdir(curdir)

    return revision, path, url


def gen_project_revision_file(project_name, origin_version_file_path, version_name,
                                tag='', incremental=False):
    print(f"version name {version_name}")
    cur_python_dir_path = os.path.dirname(os.path.realpath(__file__))
    version_file_path = os.path.join(cur_python_dir_path, origin_version_file_path)
    os.makedirs(version_file_path, exist_ok=True)
    revision, path, url = parse_as_git(version_file_path)

    build_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    build_time = build_date if incremental else time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    version_file_name = 'verinfo.h'
    contents = u'''//
// {version_file_name}
// {origin_version_file_path}
//
// Create by ccgo on {build_date}
// Copyright {build_year} ccgo Project Authors. All rights reserved.

#ifndef {project_name}_BASE_VERINFO_H_
#define {project_name}_BASE_VERINFO_H_

#define CCGO_{project_name}_VERSION "{version_name}"
#define CCGO_{project_name}_REVISION "{revision}"
#define CCGO_{project_name}_PATH "{path}"
#define CCGO_{project_name}_URL "{url}"
#define CCGO_{project_name}_BUILD_TIME "{build_time}"
#define CCGO_{project_name}_TAG "{tag}"

#endif  // {project_name}_BASE_VERINFO_H_
'''.format(version_file_name=version_file_name,
           origin_version_file_path=origin_version_file_path,
           build_date=build_date,
           build_year=build_date.partition('-')[0],
           project_name=project_name.upper(),
           version_name=version_name,
           revision=revision,
           path=path,
           url=url,
           build_time=build_time,
           tag=tag)

    with io.open(os.path.join(version_file_path, version_file_name), 'w', encoding='utf-8') as f:
        f.write(contents)
        f.flush()

    version_data = {
        'PublicComponent': {
            'Branch': path,
            'Revision': revision,
            'BuildTag': tag,
            'BuildTime': build_time
        }
    }

    output = f"[[==BUILD_DESCRIPTION==]]Revision: {version_data['PublicComponent']['Revision']} {'&nbsp;' * 18}"
    html = html_css
    data_type = 'PublicComponent'
    html_rows = ''
    for key in sorted(version_data[data_type].keys()):
        html_rows += html_row_template.format(key=key, value=version_data[data_type][key])

    html += html_table_template.format(title=data_type, table_rows=html_rows)

    output += html

    print (''.join(output.splitlines()))


def system_is_windows():
    return platform.system().lower() == 'windows'


def system_is_macos():
    return platform.system().lower() == 'darwin'


def system_architecture_is64():
    return platform.machine().endswith('64')


def get_gradle_file_path(project_path):
    gradle_file = f"{project_path}/build.gradle.kts"
    if not os.path.exists(gradle_file):
        gradle_file = f"{project_path}/build.gradle"
    return gradle_file


def get_version_file_path(project_path):
    return f"{project_path}/gradle/libs.versions.toml"


def get_version_name(project_path):
    version_name = ""
    # get from gradle/libs.versions.toml file
    # commMainProject = "x.x.x"
    with io.open(get_version_file_path(project_path), "r", encoding='UTF-8') as f:
        for line in f:
            match = re.search(r'commMainProject.*"(\d+\.\d+\.\d+)"', line)
            if match:
                version_name = match.group(1)
                break
    return version_name


def check_vs_env():
    vs_tool_dir = os.getenv("VS140COMNTOOLS")

    if not vs_tool_dir:
        print("You must install visual studio 2015 for build.")
        return False

    print('vs.dir: ' + vs_tool_dir)
    envbat = vs_tool_dir + "../../vc/vcvarsall.bat"
    print('vsvar.dir: ' + envbat)
    p = subprocess.Popen(envbat)
    p.wait()

    return True


def merge_win_static_libs(src_libs, dst_lib):
    vs_tool_dir = os.getenv("VS140COMNTOOLS")
    lib_cmd = vs_tool_dir + '/../../VC/bin/lib.exe'
    print('lib cmd:' + lib_cmd)

    src_libs.insert(0, '/OUT:' + dst_lib)
    src_libs.insert(0, lib_cmd)

    p = subprocess.Popen(src_libs)
    p.wait()
    if p.returncode != 0:
        print(f'!!!!!!!!!!!lib.exe {dst_lib} fail!!!!!!!!!!!!!!!')
        return False

    return True


def copy_windows_pdb(cmake_out, sub_folder, config, dst_folder):
    for sf in sub_folder:
        src_file = f"{cmake_out}/{sf}/{config}"
        pdbs = glob.glob(src_file + "/*.pdb")
        if len(pdbs) != 1:
            print(f"Warning: {src_file} path error.")
            continue
        else:
            print(f"start copy {pdbs[0]}")
        pdb = pdbs[0]
        if os.path.isfile(pdb):
            shutil.copy(pdb, dst_folder)
        else:
            print(f"{pdb} not exists")


def merge_files_ends_with(src_dir, suffix, out_file):
    # List of files to merge
    file_list = glob.glob(f"{src_dir}/*{suffix}")
    # Open the output file for writing
    if out_file.rfind("/") != -1 and not os.path.exists(out_file[:out_file.rfind("/")]):
        os.makedirs(out_file[:out_file.rfind("/")], exist_ok=True)
    with open(out_file, "wb") as outfile:
        # Loop through the input files and write their contents to the output file
        for filename in file_list:
            with open(filename, "rb") as infile:
                outfile.write(infile.read())


def zip_files_ends_with(src_dir, suffix, out_file):
    # List of files to zip
    file_list = glob.glob(f"{src_dir}/*{suffix}")
    # Open the output file for writing
    if out_file.rfind("/") != -1 and not os.path.exists(out_file[:out_file.rfind("/")]):
        os.makedirs(out_file[:out_file.rfind("/")], exist_ok=True)
    # zip all the files
    with zipfile.ZipFile(out_file, 'w') as zipf:
        for filename in file_list:
            zipf.write(filename, os.path.basename(filename))


def get_project_file_name(project_file_prefix):
    if system_is_macos():
        project_file = f"{project_file_prefix}.xcodeproj"
    elif system_is_windows():
        project_file = f"{project_file_prefix}.sln"
    else:
        project_file = f"{project_file_prefix}.workspace"
    return project_file


def get_open_project_file_cmd(project_file):
    if system_is_macos():
        # open xcode project
        return f'open {project_file}'
    elif system_is_windows():
        # open vs project, and as Release config
        return f'start "" {project_file} /property:Configuration=Release'
    else:
        # open codelite project, and background
        return f'codelite {project_file} &'


def is_in_lib_list(target, lib_list):
    target = os.path.basename(target)
    for lib in lib_list:
        if target == lib:
            return True
        # remote suffix
        target = os.path.splitext(target)[0]
        if target == lib:
            return True
        if target.startswith("lib"):
            if target[3:] == lib:
                return True
    return False


def main():
    cur_path = os.path.dirname(os.path.realpath(__file__))
    gen_project_revision_file(PROJECT_NAME, OUTPUT_VERINFO_PATH, get_version_name(cur_path))


if __name__ == '__main__':
    main()
