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
# third_party not include CMakeExtraFlags
# include(${CMAKE_SOURCE_DIR}/cmake/CMakeExtraFlags.cmake)

set(TEMPLATE_SUB_LIB_NAME "")
generate_library_name(TEMPLATE_SUB_LIB_NAME ${CMAKE_CURRENT_SOURCE_DIR})

message(STATUS "Generating ThirdParty library [${TEMPLATE_SUB_LIB_NAME}]")

project(${TEMPLATE_SUB_LIB_NAME} LANGUAGES C CXX)

set(TEMP_DIR_LIST "")
get_third_party_src_directories(TEMP_DIR_LIST ${CMAKE_CURRENT_SOURCE_DIR})

foreach(dir IN LISTS TEMP_DIR_LIST)
    set(TEMP_CHILD_PATH "${dir}/src")
    set(DIR_FILES "")
    add_sub_layer_sources_recursively(DIR_FILES ${CMAKE_CURRENT_SOURCE_DIR}/${TEMP_CHILD_PATH})
    list(APPEND SELF_TEMP_SRC_FILES ${DIR_FILES})
    message(STATUS "Generating ThirdParty library [${TEMPLATE_SUB_LIB_NAME}] from [${TEMP_CHILD_PATH}] with source files [${DIR_FILES}]")
endforeach()

message(STATUS "Generating ThirdParty library [${TEMPLATE_SUB_LIB_NAME}] with source files [${SELF_TEMP_SRC_FILES}]")

add_cc_library(
        NAME
        ${TEMPLATE_SUB_LIB_NAME}
        SRCS
        ${SELF_TEMP_SRC_FILES}
)
