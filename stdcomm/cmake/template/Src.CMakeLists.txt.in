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

include(${CMAKE_SOURCE_DIR}/cmake/CMakeUtils.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/CMakeExtraFlags.cmake)

set(TEMPLATE_SUB_LIB_NAME "")
generate_library_name(TEMPLATE_SUB_LIB_NAME ${CMAKE_CURRENT_SOURCE_DIR})

message(STATUS "Generating ThirdParty library [${TEMPLATE_SUB_LIB_NAME}]")

project(${TEMPLATE_SUB_LIB_NAME} LANGUAGES C CXX)

set(TEMP_DIR_LIST "")
get_subdirectories(TEMP_DIR_LIST "${CMAKE_CURRENT_SOURCE_DIR}/")

foreach(dir IN LISTS TEMP_DIR_LIST)
    configure_file(
            ${CMAKE_SOURCE_DIR}/cmake/template/Src.SubDir.CMakeLists.txt.in
            ${CMAKE_SOURCE_DIR}/src/${dir}/CMakeLists.txt
            NEWLINE_STYLE LF
            @ONLY
    )
    add_subdirectory(${dir} ${PROJECT_NAME}-${dir})
endforeach()
