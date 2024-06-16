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

cmake_minimum_required(VERSION 3.14)

# main project root
set(MAIN_PROJECT_ROOT_DIR ${CMAKE_SOURCE_DIR})
string(REPLACE "/" ";" TEMP_SPLIT_ITEMS "${CMAKE_SOURCE_DIR}")
list(GET TEMP_SPLIT_ITEMS -1 MAIN_PROJECT_NAME)

project(${MAIN_PROJECT_NAME} CXX C)

include(${CMAKE_SOURCE_DIR}/cmake/template/Root.CMakeLists.txt.in)
