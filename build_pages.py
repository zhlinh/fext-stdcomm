#!/usr/bin/env python3
# -- coding: utf-8 --
#
# build_pages.py
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
import shutil
import subprocess
import datetime

# import config file, i.e. "CONFIG_" prefixed global variables
from build_config import *

# build doxygen
TARGET_PROJECT_PATH = CONFIG_PROJECT_RELATIVE_PATH
PAGES_BRANCH_NAME = CONFIG_PAGES_BRANCH_NAME


LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))

# get the python command
if sys.platform.startswith("win"):
    # windows use 'python' command
    PYTHON_CMD = "python"
else:
    if shutil.which("python3") is not None:
        # use 'python3' command if it exists
        PYTHON_CMD = "python3"
    else:
        PYTHON_CMD = "python"

subprocess.run([PYTHON_CMD, "build.py", "CI_BUILD_DOCS"], check=True)

os.chdir(LOCAL_PATH)
# copy html files to root
html_dir = f"{TARGET_PROJECT_PATH}/docs/_html"
target_dir = "./"
files_list = os.listdir(html_dir)
for item in files_list:
    shutil.move(os.path.join(html_dir, item), os.path.join(target_dir, item))

# remove PAGES_BRANCH_NAME branch and create new branch
# ignore the error because local branch may not exist
try:
    print("delete branch")
    subprocess.run(["git", "branch", "-D", PAGES_BRANCH_NAME], check=True)
except subprocess.CalledProcessError:
    pass

print("checkout new branch")
last_branch = subprocess.check_output(["git", "symbolic-ref", "--short", "-q", "HEAD"]).decode().strip()
subprocess.run(["git", "checkout", "-b", PAGES_BRANCH_NAME], check=True)

# commit codes to PAGES_BRANCH_NAME branch
print(f"add {PAGES_BRANCH_NAME} commit")
now_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
subprocess.run(["git", "add", "--all"], check=True)
subprocess.run(["git", "commit", "-a", "-m", f"ci({PAGES_BRANCH_NAME}): release {PAGES_BRANCH_NAME} on {now_date}"], check=True)

print("pushing...")
subprocess.run(["git", "push", "--set-upstream", "origin", PAGES_BRANCH_NAME, "-f"], check=True)

# checkout to last branch
subprocess.run(["git", "checkout", last_branch], check=True)
