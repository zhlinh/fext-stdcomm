#!/usr/bin/env python3
# -- coding: utf-8 --
#
# update_changelog.py
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
import platform
import subprocess
import urllib.request


def check_program(program):
    try:
        subprocess.run(program.split(" "), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[{program}] not found, exception:{e}")
        return False
    return True


sys_os = platform.system()
print(f"sys_os={sys_os}")

if not check_program("conventional-changelog --version"):
    if not check_program("npm --version"):
        if sys_os == "Darwin":
            # macOS, 'brew install'
            if not check_program("brew --version"):
                print("[brew] not found, install first...")
                url = "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"
                filename = "install.sh"
                urllib.request.urlretrieve(url, filename)
                os.chmod(filename, 0o755)
                subprocess.run(f"./{filename}".split(" "), check=True)
                subprocess.run("brew install node".split(" "), shell=True)
            print("[npm] not found, install first...")
            subprocess.run("brew install node".split(" "))
            subprocess.run("brew install npm".split(" "))
        elif sys_os == "Linux":
            subprocess.run("curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash".split(" "),
                           shell=True, check=True)
        else:
            print("update changelog failed, please install [npm] first!")
            exit(1)
    print("[commitizen] not found, install first...")
    subprocess.run("npm install -g commitizen".split(" "))
    subprocess.run("npm install -g conventional-changelog-cli".split(" "))

print("execute conventional-changelog...")
subprocess.run(["conventional-changelog", "-p", "angular", "-i", "CHANGELOG.md", "-s", "-r", "2"], check=True)
