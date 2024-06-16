#!/usr/bin/env python
# -- coding: utf-8 --
#
# build_oa_pages.py
# ccgo
#
# Created by jaredhuang on 2021-01-17.
# Copyright © 2021 jaredhuang. All rights reserved.

import os
import sys
import shutil
import subprocess
import datetime

# 引入配置文件，即"CONFIG_"开头的全局变量
from build_config import *

# 构建doxygen
TARGET_PROJECT_PATH = CONFIG_PROJECT_RELATIVE_PATH

LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))

# 最终以获取到的为准
if sys.platform.startswith("win"):
    # Windows 上使用 python 命令
    PYTHON_CMD = "python"
else:
    if shutil.which("python3") is not None:
        # 执行 python3 命令
        PYTHON_CMD = "python3"
    else:
        PYTHON_CMD = "python"

subprocess.run([PYTHON_CMD, "build.py", "CI_BUILD_DOCS"], check=True)

os.chdir(LOCAL_PATH)
# 将doxygen生成的html下的所有文件和目录拷贝到根目录
# 指定Doxygen生成的HTML目录和根目录
html_dir = f"{TARGET_PROJECT_PATH}/docs/_html"
target_dir = "./"
files_list = os.listdir(html_dir)
for item in files_list:
    shutil.move(os.path.join(html_dir, item), os.path.join(target_dir, item))

# 删除oa-pages分支并创建新的分支
# 忽略错误，因为本地分支可能不存在
try:
    print("delete branch")
    subprocess.run(["git", "branch", "-D", "oa-pages"], check=True)
except subprocess.CalledProcessError:
    pass

print("checkout new branch")
last_branch = subprocess.check_output(["git", "symbolic-ref", "--short", "-q", "HEAD"]).decode().strip()
subprocess.run(["git", "checkout", "-b", "oa-pages"], check=True)

# 提交代码到oa-pages分支
print("add oa-pages commit")
now_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
subprocess.run(["git", "add", "--all"], check=True)
subprocess.run(["git", "commit", "-a", "-m", f"ci(oa-pages): release oa-pages on {now_date}"], check=True)

print("pushing...")
subprocess.run(["git", "push", "--set-upstream", "origin", "oa-pages", "-f"], check=True)

# checkout to last branch
subprocess.run(["git", "checkout", last_branch], check=True)
