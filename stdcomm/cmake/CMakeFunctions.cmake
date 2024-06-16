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

##
# exclude_unittest_files()
# @brief This macro excludes unit test, test and mock files from the build process when GOOGLETEST_SUPPORT is not enabled.
#
# It takes a list of input source files, then filters out any file that matches the following patterns:
# 1. *_unittest.cc
# 2. *_test.cc
# 3. *_mock.cc
# These files are excluded from the build when GOOGLETEST_SUPPORT is not set.
#
# Usage:
#   exclude_unittest_files(<list_of_input_source_files>)
#
# @param[in] input_source_files A list of source files to exclude test-related files from.
macro(exclude_unittest_files input_source_files)
    if (NOT GOOGLETEST_SUPPORT)
        list(FILTER ${input_source_files} EXCLUDE REGEX ".*_unittest\\.cc$")
        list(FILTER ${input_source_files} EXCLUDE REGEX ".*_test\\.cc$")
        list(FILTER ${input_source_files} EXCLUDE REGEX ".*_mock\\.cc$")
    endif()
endmacro()

# add_subdirectories_recursively()
# define a function to add subdirectories recursively
function(add_subdirectories_recursively out_dir_list root_dir)
    set(temp_dir_list "")
    set(dir_stack ${root_dir})

    while(dir_stack)
        # get the top directory
        list(GET dir_stack 0 cur_dir)
        list(REMOVE_AT dir_stack 0)

        # get all subdirectories under the current directory
        file(GLOB subdirectories RELATIVE ${root_dir} ${cur_dir}/*)

        # loop through all subdirectories
        foreach(subdirectory ${subdirectories})
            # if the subdirectory is a directory and not a file
            if(IS_DIRECTORY ${root_dir}/${subdirectory})
                message(STATUS "Checking subdirectory: ${subdirectory}")
                # filter subdirectory by platform
                string(REPLACE "/" ";" temp_items "${subdirectory}")
                list(GET temp_items -1 base_subdirectory)
                set(temp_subdirectory_valid FALSE)

                if((${base_subdirectory} STREQUAL "android") OR (${base_subdirectory} STREQUAL "jni"))
                    if(ANDROID)
                        set(temp_subdirectory_valid TRUE)
                    endif()
                elseif((${base_subdirectory} STREQUAL "ios"))
                    if(APPLE AND IOS)
                        set(temp_subdirectory_valid TRUE)
                    endif()
                elseif((${base_subdirectory} STREQUAL "macos") OR (${base_subdirectory} STREQUAL "osx"))
                    if(APPLE AND (NOT IOS))
                        set(temp_subdirectory_valid TRUE)
                    endif()
                elseif((${base_subdirectory} STREQUAL "oni") OR (${base_subdirectory} STREQUAL "apple"))
                    # oni is macOS and iOS
                    if(APPLE)
                        set(temp_subdirectory_valid TRUE)
                    endif()
                elseif((${base_subdirectory} STREQUAL "windows") OR (${base_subdirectory} STREQUAL "win"))
                    if(MSVC)
                        set(temp_subdirectory_valid TRUE)
                    endif()
                elseif((${base_subdirectory} STREQUAL "linux"))
                    # linux
                    if(UNIX AND (NOT APPLE) AND (NOT ANDROID))
                        set(temp_subdirectory_valid TRUE)
                    endif()
                else()
                    set(temp_subdirectory_valid TRUE)
                endif()

                if (temp_subdirectory_valid)
                    # add the subdirectory to the stack
                    list(APPEND temp_dir_list ${subdirectory})
                    list(APPEND dir_stack ${cur_dir}/${subdirectory})
                endif()
            endif()
        endforeach()
    endwhile()

    # note that setting PARENT_SCOPE is necessary to return the value to the parent scope
    set(${out_dir_list} "${temp_dir_list}" PARENT_SCOPE)
endfunction()

# add_sub_layer_sources_recursively()
function(add_sub_layer_sources_recursively output_src_files input_source_dir)
    string(REPLACE "/" ";" TEMP_SPLIT_ITEMS "${CMAKE_SOURCE_DIR}")
    list(GET TEMP_SPLIT_ITEMS -1 SOURCE_DIR_NAME)

    set(temp_src_files "")
    # the current root directory
    include_directories(${input_source_dir}/)
    file(GLOB SELF_TEMP_SRC_FILES
            ${input_source_dir}/*.cc
            ${input_source_dir}/*.c
            ${input_source_dir}/*.cpp
            ${input_source_dir}/*.mm
            ${input_source_dir}/*.m
            )
    source_group(${SOURCE_DIR_NAME} FILES ${SELF_TEMP_SRC_FILES})
    list(APPEND temp_src_files ${SELF_TEMP_SRC_FILES})

    # get all subdirectories under the current directory
    file(GLOB CHILDREN RELATIVE ${input_source_dir} */)
    # output all subdirectories
    set(DIR_LIST "")
    add_subdirectories_recursively(DIR_LIST ${input_source_dir})
    message(STATUS "SUB_DIRECTORIES: [${DIR_LIST}] from [${input_source_dir}]")

    # loop DIR_LIST
    foreach(dir IN LISTS DIR_LIST)
        include_directories(${input_source_dir}/${dir}/)
        file(GLOB SELF_TEMP_SRC_FILES
                ${input_source_dir}/${dir}/*.cc
                ${input_source_dir}/${dir}/*.c
                ${input_source_dir}/${dir}/*.cpp
                ${input_source_dir}/${dir}/*.mm
                ${input_source_dir}/${dir}/*.m
                )
        source_group(${SOURCE_DIR_NAME}\\${dir} FILES ${SELF_TEMP_SRC_FILES})
        list(APPEND temp_src_files ${SELF_TEMP_SRC_FILES})
    endforeach()
    # filter the files in the list
    set(temp_only_files "")
    foreach(temp_file ${temp_src_files})
        if(IS_DIRECTORY ${temp_file})
            # skip dir
        else()
            # file
            list(APPEND temp_only_files ${temp_file})
        endif()
    endforeach()
    set(${output_src_files} "${temp_only_files}" PARENT_SCOPE)
endfunction()

# generate_library_name()
function(generate_library_name output_library_name input_current_dir)
    # Replace the path separator with a semicolon to split the directories
    string(REPLACE "/" ";" TEMP_SPLIT_ITEMS "${input_current_dir}")
    # Get the last directory in the path
    list(GET TEMP_SPLIT_ITEMS -1 TEMP_NAME)
    # Set the library name
    set(temp_library_name "${MAIN_PROJECT_NAME}-${TEMP_NAME}")
    message(STATUS "Generating input_current_dir [${input_current_dir}]")
    set(${output_library_name} "${temp_library_name}" PARENT_SCOPE)
endfunction()

# get_subdirectories()
function(get_subdirectories output_dir_list dir_path)
    # get all subdirectories under the current directory
    file(GLOB CHILDREN RELATIVE
            "${dir_path}/"
            ${dir_path}/*
            )
    set(DIR_LIST "")
    # loop CHILDREN
    foreach(child ${CHILDREN})
        set(TEMP_CHILD_PATH "${dir_path}/${child}")
        if(IS_DIRECTORY "${TEMP_CHILD_PATH}")
            file(GLOB_RECURSE TARGET_FILES
                    "${TEMP_CHILD_PATH}/*.cc"
                    "${TEMP_CHILD_PATH}/*.c"
                    "${TEMP_CHILD_PATH}/*.cpp"
                    "${TEMP_CHILD_PATH}/*.mm"
                    "${TEMP_CHILD_PATH}/*.m"
                    )
            if (TARGET_FILES)
                list(APPEND DIR_LIST ${child})
            endif()
        endif()
    endforeach()
    set(${output_dir_list} "${DIR_LIST}" PARENT_SCOPE)
endfunction()

# add_valid_subdirectories()
function(add_valid_subdirectories output_dir_list dir_path)
    # get the subdirectories
    file(GLOB CHILDREN RELATIVE
            "${dir_path}/"
            ${dir_path}/*
            )
    set(DIR_LIST "")
    # loop CHILDREN and check if there is a CMakeLists.txt file
    foreach(child ${CHILDREN})
        set(TEMP_CHILD_PATH "${dir_path}/${child}")
        if(IS_DIRECTORY "${TEMP_CHILD_PATH}")
            if(EXISTS "${TEMP_CHILD_PATH}/CMakeLists.txt")
                file(GLOB_RECURSE TARGET_FILES
                        "${TEMP_CHILD_PATH}/*.cc"
                        "${TEMP_CHILD_PATH}/*.c"
                        "${TEMP_CHILD_PATH}/*.cpp"
                        "${TEMP_CHILD_PATH}/*.mm"
                        "${TEMP_CHILD_PATH}/*.m"
                        )
                if (TARGET_FILES)
                    list(APPEND DIR_LIST ${child})
                endif()
            endif()
        endif()
    endforeach()
    foreach(dir IN LISTS DIR_LIST)
        add_subdirectory("${dir_path}/${dir}" "${PROJECT_NAME}-${dir}")
    endforeach()
    set(${output_dir_list} "${DIR_LIST}" PARENT_SCOPE)
endfunction()

# get_third_party_lib_directories()
function(get_third_party_lib_directories output_dir_list dir_path)
    # get all subdirectories under the current directory
    file(GLOB CHILDREN RELATIVE
            "${dir_path}/"
            ${dir_path}/*
            )
    set(DIR_LIST "")
    # loop CHILDREN and check if there is a lib directory
    foreach(child ${CHILDREN})
        set(TEMP_CHILD_PATH "${dir_path}/${child}")
        if(IS_DIRECTORY "${TEMP_CHILD_PATH}")
            if(EXISTS "${TEMP_CHILD_PATH}/lib")
                file(GLOB_RECURSE TARGET_FILES
                        "${TEMP_CHILD_PATH}/lib/*.so"
                        "${TEMP_CHILD_PATH}/lib/*.a"
                        "${TEMP_CHILD_PATH}/lib/*.lib"
                        "${TEMP_CHILD_PATH}/lib/*.dylib"
                )
                if (TARGET_FILES)
                    list(APPEND DIR_LIST ${child})
                endif()
            endif()
        endif()
    endforeach()
    set(${output_dir_list} "${DIR_LIST}" PARENT_SCOPE)
endfunction()

# get_third_party_include_directories()
function(get_third_party_include_directories output_dir_list dir_path)
    # get all subdirectories under the current directory
    file(GLOB CHILDREN RELATIVE
            "${dir_path}/"
            ${dir_path}/*
            )
    set(DIR_LIST "")
    # loop CHILDREN and check if there is a include directory
    foreach(child ${CHILDREN})
        set(TEMP_CHILD_PATH "${dir_path}/${child}")
        if(IS_DIRECTORY "${TEMP_CHILD_PATH}")
            if(EXISTS "${TEMP_CHILD_PATH}/include")
                file(GLOB_RECURSE TARGET_FILES
                        "${TEMP_CHILD_PATH}/include/*.h"
                        "${TEMP_CHILD_PATH}/include/*.hpp"
                )
                if (TARGET_FILES)
                    list(APPEND DIR_LIST ${child})
                endif()
            endif()
        endif()
    endforeach()
    set(${output_dir_list} "${DIR_LIST}" PARENT_SCOPE)
endfunction()

# get_third_party_src_directories()
function(get_third_party_src_directories output_dir_list dir_path)
    # get all subdirectories under the current directory
    file(GLOB CHILDREN RELATIVE
            "${dir_path}/"
            ${dir_path}/*
            )
    set(DIR_LIST "")
    # loop CHILDREN and check if there is a src directory
    foreach(child ${CHILDREN})
        set(TEMP_CHILD_PATH "${dir_path}/${child}")
        if(IS_DIRECTORY "${TEMP_CHILD_PATH}")
            if(EXISTS "${TEMP_CHILD_PATH}/src")
                file(GLOB_RECURSE TARGET_FILES
                        "${TEMP_CHILD_PATH}/src/*.cc"
                        "${TEMP_CHILD_PATH}/src/*.c"
                        "${TEMP_CHILD_PATH}/src/*.cpp"
                        "${TEMP_CHILD_PATH}/src/*.mm"
                        "${TEMP_CHILD_PATH}/src/*.m"
                        "${TEMP_CHILD_PATH}/src/*.h"
                        "${TEMP_CHILD_PATH}/src/*.hpp"
                )
                if (TARGET_FILES)
                    list(APPEND DIR_LIST ${child})
                endif()
            endif()
        endif()
    endforeach()
    set(${output_dir_list} "${DIR_LIST}" PARENT_SCOPE)
endfunction()


# get_third_party_binary_files()
# usage:
# set(TEMP_TARGET_SRC_LINKS "")
# set(TEMP_TARGET_LINK_FLAGS "")
# get_third_party_binary_files(TEMP_TARGET_SRC_LINKS TEMP_TARGET_LINK_FLAGS)
# then set target link:
# TEMP_TARGET_SRC_LINKS(list): target_link_libraries(${TARGET_NAME} ${TEMP_TARGET_SRC_LINKS})
# TEMP_TARGET_LINK_FLAGS(str): set_target_properties(${TARGET_NAME} PROPERTIES LINK_FLAGS ${TEMP_TARGET_LINK_FLAGS})
function(get_third_party_binary_files output_target_src_links output_target_link_flags)
    if(ANDROID)
        set(TEMP_PLATFORM "android")
        set(TEMP_REG_SUFFIX "${ANDROID_ABI}/*.so")
    elseif(APPLE)
        if (IOS)
            set(TEMP_PLATFORM "ios")
            set(TEMP_REG_SUFFIX "*")
        else()
            set(TEMP_PLATFORM "macos")
            set(TEMP_REG_SUFFIX "*")
        endif()
    elseif(MSVC)
        set(TEMP_PLATFORM "windows")
        if(CMAKE_GENERATOR_PLATFORM STREQUAL "Win32")
            set(TEMP_REG_SUFFIX "x86/*.lib")
        else()
            set(TEMP_REG_SUFFIX "x64/*.lib")
        endif()
    else()
        # for linux
        set(TEMP_PLATFORM "linux")
        set(TEMP_REG_SUFFIX "*")
    endif()
    set(TEMP_TARGET_SRC_LINKS "")
    set(TEMP_TARGET_LINK_FLAGS "")
    set(TEMP_THIRD_PARTY_LIB_DIRS "")
    get_third_party_lib_directories(TEMP_THIRD_PARTY_LIB_DIRS ${PROJECT_SOURCE_DIR}/third_party/)
    foreach(item ${TEMP_THIRD_PARTY_LIB_DIRS})
        set(third_party_sub_dir ${PROJECT_SOURCE_DIR}/third_party/${item})
        # add the binary files
        file(GLOB TEMP_COMM_FILES RELATIVE ${PROJECT_SOURCE_DIR} ${third_party_sub_dir}/lib/${TEMP_PLATFORM}/${TEMP_REG_SUFFIX})
        # exclude the files start with .
        list(FILTER TEMP_COMM_FILES EXCLUDE REGEX "^\\.")
        if(NOT TEMP_COMM_FILES STREQUAL "")
            foreach(file_path ${TEMP_COMM_FILES})
                get_filename_component(file_ext ${file_path} LAST_EXT)
                get_filename_component(file_name ${file_path} NAME_WE)
                get_filename_component(file_dir ${file_path} DIRECTORY)
                # if the file is a shared library, add it as a shared library
                if(file_path MATCHES ".*\\.so" OR file_path MATCHES ".*\\.dylib" OR file_path MATCHES ".*\\.dll")
                    add_library(${file_name}-lib SHARED IMPORTED)
                    set_target_properties(${file_name}-lib PROPERTIES IMPORTED_LOCATION ${PROJECT_SOURCE_DIR}/${file_path})
                    list(APPEND TEMP_TARGET_SRC_LINKS ${file_name}-lib)
                elseif(file_path MATCHES ".*\\.xcframework" OR file_path MATCHES ".*\\.framework")
                    list(APPEND TEMP_TARGET_SRC_LINKS "-framework ${file_name}")
                    # add the framework path to the link flags, then call, as string format
                    set(TEMP_TARGET_LINK_FLAGS "${TEMP_TARGET_LINK_FLAGS} -Wl,-F${PROJECT_SOURCE_DIR}/${file_dir}")
                else()
                    add_library(${file_name}-lib STATIC IMPORTED)
                    set_target_properties(${file_name}-lib PROPERTIES IMPORTED_LOCATION ${PROJECT_SOURCE_DIR}/${file_path})
                    list(APPEND TEMP_TARGET_SRC_LINKS ${file_name}-lib)
                endif()
                message(STATUS "Add third party (${file_name}-lib) binary file: ${PROJECT_SOURCE_DIR}/${file_path}")
            endforeach()
        endif()
    endforeach()

    set(${output_target_src_links} "${TEMP_TARGET_SRC_LINKS}" PARENT_SCOPE)
    set(${output_target_link_flags} "${TEMP_TARGET_LINK_FLAGS}" PARENT_SCOPE)
endfunction()

# add_cc_library()
#
# CMake function to add a C++ library target to the build.
#
# Parameters:
# NAME: target name (see notes)
# HDRS: the library's public header files
# SRCS: the library's source files
# DIRS: the library's source directories, recursively search for c and cc files, up to 2 levels
# DEPS: the list of other libraries that this library depends on
# COPTS: the list of private compile options
# DEFINES: the list of public definitions
# LINKOPTS: the list of link options
# PUBLIC: add this option to export this library to the "project name" folder, instead of the "project name/internal" folder
# TESTONLY: add this option to only build this target when GOOGLETEST_SUPPORT=ON or BENCHMARK_SUPPORT=ON
#
# Notes:
# by default,
# add_cc_library will always create a library named xxx-${NAME} and create an alias target xxx::${NAME}.
# always use xxx:: form to reduce namespace pollution, where xxx is the project name
#
# add_cc_library(
#   NAME
#     awesome
#   HDRS
#     "a.h"
#     "b.hpp"
#   SRCS
#     "a.cc"
#     "b.cc"
# )
# add_cc_library(
#   NAME
#     fantastic_lib
#   SRCS
#     "b.cc"
#     "c.cc"
#   DIRS
#     "a/"
#     "b/"
#   DEPS
#     xxx::awesome # not "awesome"
#   PUBLIC
#   SHARED
# )
#
# add_cc_library(
#   NAME
#     main_lib
#   ...
#   DEPS
#     xxx::fantastic_lib
# )
#
function(add_cc_library)
    # cmake_parse_arguments(
    #   <prefix>       # this is the prefix defined for the CMake arguments, used to set the prefix of the parsed arguments
    #   <options>      # this is a list that defines all supported command line argument options, each option consists of three parts:
    #                  # 1. the option's name (required)
    #                  # 2. the option's type (required)
    #                  # 3. the option's description (optional)
    #   <one_value_kw> # this is a keyword used to specify the name of a single value argument, the default is "VALUE"
    #   <multi_value_kw> # this is a keyword used to specify the name of a multi-value argument, the default is "VALUES"
    #   <...>          # this is the actual command line arguments, each argument can be either a single value type or a multi-value type argument.
    # )
    cmake_parse_arguments(CC_LIB
            "DISABLE_INSTALL;PUBLIC;TESTONLY;SHARED"
            "NAME"
            "HDRS;SRCS;DIRS;COPTS;DEFINES;LINKOPTS;DEPS"
            ${ARGN}
            )

    if(CC_LIB_TESTONLY AND
            NOT (GOOGLETEST_SUPPORT OR BENCHMARK_SUPPORT))
        return()
    endif()

    message(STATUS "COMM_ENABLE_INSTALL: ${COMM_ENABLE_INSTALL}")
    if(COMM_ENABLE_INSTALL)
        set(_NAME "${CC_LIB_NAME}")
    else()
        set(_NAME "${MAIN_PROJECT_NAME}-${CC_LIB_NAME}")
    endif()
    message(STATUS "CC_LIBRARY_NAME: ${_NAME}")

    set(group_top_prefix "")
    if(CC_LIB_DIRS)
        foreach(dir IN LISTS CC_LIB_DIRS)
            set(DIR_FILES "")
            add_sub_layer_sources_recursively(DIR_FILES ${dir})
            list(APPEND CC_LIB_SRCS ${DIR_FILES})
        endforeach()
    endif()
    message(STATUS "CC_LIB_SRCS: ${CC_LIB_SRCS}")

    exclude_unittest_files(CC_LIB_SRCS)

    if (CC_LIB_SRCS STREQUAL "")
        return()
    endif()

    set(CC_SRCS ${CC_LIB_SRCS})
    # Check if this is a header-only library
    list(FILTER CC_SRCS EXCLUDE REGEX ".*\\.(h|inc)")

    if(CC_SRCS STREQUAL "")
        set(CC_LIB_IS_INTERFACE 1)
    else()
        set(CC_LIB_IS_INTERFACE 0)
    endif()

    # 1. "shared"  -- This is a shared library, perhaps on a non-windows platform
    #                 where DLL doesn't make sense.
    # 2. "static"  -- This target does not depend on the DLL and should be built
    #                 statically.
    if(COMM_BUILD_SHARED_LIBS OR CC_LIB_SHARED)
        set(_build_type "shared")
    else()
        set(_build_type "static")
    endif()

    if(NOT CC_LIB_IS_INTERFACE)
        if(_build_type STREQUAL "static" OR _build_type STREQUAL "shared")
            add_library(${_NAME} "")
            message(STATUS "CC_LIB_PUBLIC: ${CC_LIB_PUBLIC}")
            if((CC_LIB_PUBLIC AND ENABLE_VISIBILITY) OR CC_LIB_TESTONLY)
                message(STATUS "AddLibrarySet all to PUBLIC")
                target_sources(${_NAME}
                        PUBLIC
                        ${CC_LIB_SRCS} ${CC_LIB_HDRS}
                        )
            else()
                # let the source code with __attribute__((visibility("default"))) or (dllimport) to be PUBLIC
                # merge list A and list B
                set(sources ${CC_LIB_SRCS})
                list(APPEND sources ${CC_LIB_HDRS})
                set(is_public_sources FALSE)
                foreach(source IN LISTS sources)
                    if(IS_DIRECTORY "${source}")
                        # skip dir
                    else()
                        # file
                        file(STRINGS "${source}" contents REGEX "__attribute__\\(\\(visibility\\(\"default\"\\)\\)\\)|\\(dllimport\\)|COMM_PUBLIC|PROJECT_EXPORT_PUBLIC|JNIEXPORT")
                        if (contents)
                            set(is_public_sources TRUE)
                            break()
                        endif()
                    endif()
                endforeach()
                if(is_public_sources)
                    message(STATUS "AddCCLibrary[PUBLIC] ${_NAME}")
                    target_sources(${_NAME} PUBLIC ${CC_LIB_SRCS} ${CC_LIB_HDRS})
                else()
                    message(STATUS "AddCCLibrary[PRIVATE] ${_NAME}")
                    target_sources(${_NAME} PRIVATE ${CC_LIB_SRCS} ${CC_LIB_HDRS})
#                        set_source_files_properties("${NAME}" PROPERTIES
#                                COMPILE_FLAGS "-fvisibility=hidden")
                endif()
                target_sources(${_NAME}
                        PRIVATE
                        ${CC_LIB_SRCS} ${CC_LIB_HDRS}
                        )
            endif()
            message(STATUS "CC_LIB_DEPS: ${CC_LIB_DEPS}")
            target_link_libraries(${_NAME}
                    PUBLIC
                    ${CC_LIB_DEPS}
                    PRIVATE
                    ${CC_LIB_LINKOPTS}
                    ${COMM_DEFAULT_LINKOPTS}
                    )
        else()
            message(FATAL_ERROR "Invalid build type: ${_build_type}")
        endif()

        # if the language is not set, the linker language will be set to CXX
        set_property(TARGET ${_NAME} PROPERTY LINKER_LANGUAGE "CXX")

        target_include_directories(${_NAME} ${COMM_INTERNAL_INCLUDE_WARNING_GUARD}
                PUBLIC
                "$<BUILD_INTERFACE:${COMM_COMMON_INCLUDE_DIRS}>"
                $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
                )
        target_compile_options(${_NAME} PRIVATE ${CC_LIB_COPTS})
        target_compile_definitions(${_NAME} PUBLIC ${CC_LIB_DEFINES})

        # Add all targets to a a folder in the IDE for organization.
        if(CC_LIB_PUBLIC)
            set_property(TARGET ${_NAME} PROPERTY FOLDER ${COMM_IDE_FOLDER})
        elseif(CC_LIB_TESTONLY)
            set_property(TARGET ${_NAME} PROPERTY FOLDER ${COMM_IDE_FOLDER}/test)
        else()
            set_property(TARGET ${_NAME} PROPERTY FOLDER ${COMM_IDE_FOLDER}/internal)
        endif()

        # install will lose the prefix, add it back here
        if(COMM_ENABLE_INSTALL)
            set_target_properties(${_NAME} PROPERTIES
                    OUTPUT_NAME "${_NAME}"
                    SOVERSION 0
                    )
        endif()
    else()
        # header-only library
        add_library(${_NAME} INTERFACE)
        target_include_directories(${_NAME} ${COMM_INTERNAL_INCLUDE_WARNING_GUARD}
                INTERFACE
                "$<BUILD_INTERFACE:${COMM_COMMON_INCLUDE_DIRS}>"
                $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
                )

        target_link_libraries(${_NAME}
                INTERFACE
                ${CC_LIB_DEPS}
                ${CC_LIB_LINKOPTS}
                ${COMM_DEFAULT_LINKOPTS}
                )
        target_compile_definitions(${_NAME} INTERFACE ${CC_LIB_DEFINES})
    endif()

    set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}" CACHE PATH "Installation directory" FORCE)
    message(STATUS "CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}")
    message(STATUS "CMAKE_SYSTEM_NAME=${CMAKE_SYSTEM_NAME}")

    if(COMM_ENABLE_INSTALL)
        install(TARGETS ${_NAME} EXPORT ${PROJECT_NAME}Targets
                RUNTIME DESTINATION ${CMAKE_SYSTEM_NAME}.out
                LIBRARY DESTINATION ${CMAKE_SYSTEM_NAME}.out
                ARCHIVE DESTINATION ${CMAKE_SYSTEM_NAME}.out
                )
    endif()

    add_library(${MAIN_PROJECT_NAME}::${CC_LIB_NAME} ALIAS ${_NAME})
endfunction()

# add_cc_test()
#
# CMake function to add a C++ test target to the build.
#
# Parameters:
# NAME: target name (see notes)
# SRCS: the test's source files
# DIRS: the test's source directories, recursively search for c and cc files, up to 2 levels
# DEPS: the list of other libraries that this test depends on
# COPTS: the list of private compile options
# DEFINES: the list of public definitions
# LINKOPTS: the list of link options
#
# Notes:
# by default,
# add_cc_test will always create a test named xxx-${NAME} and create an alias target xxx::${NAME}.
# always use xxx:: form to reduce namespace pollution, where xxx is the project name
#
# smaple:
# add_cc_library(
#   NAME
#     awesome
#   HDRS
#     "a.h"
#     "b.hpp"
#   SRCS
#     "a.cc"
#   DIRS
#     "a/"
#     "b/"
#   PUBLIC
# )
#
# add_cc_tests(
#   NAME
#     awesome_test
#   SRCS
#     "awesome_test.cc"
#   DIRS
#     "a/"
#     "b/"
#   DEPS
#     xxx::awesome
#     GTest::gmock
#     GTest::gtest_main
# )
function(add_cc_tests)
    if(NOT (GOOGLETEST_SUPPORT OR BENCHMARK_SUPPORT))
        return()
    endif()

    cmake_parse_arguments(CC_TEST
            ""
            "NAME"
            "SRCS;DIRS;COPTS;DEFINES;LINKOPTS;DEPS"
            ${ARGN}
            )

    set(_NAME "${CC_TEST_NAME}")
    message(STATUS "CC_TEST_NAME: ${_NAME}")

    add_executable(${_NAME} "")

    set(group_top_prefix "")
    if(CC_TEST_DIRS)
        foreach(dir IN LISTS CC_TEST_DIRS)
            set(DIR_FILES "")
            add_sub_layer_sources_recursively(DIR_FILES ${dir})
            list(APPEND CC_TEST_SRCS ${DIR_FILES})
        endforeach()
    endif()
    message(STATUS "CC_TEST_SRCS: ${CC_TEST_SRCS}")

    target_sources(${_NAME} PRIVATE ${CC_TEST_SRCS})
    target_include_directories(${_NAME}
            PUBLIC ${COMM_COMMON_INCLUDE_DIRS}
            PRIVATE ${COMM_GTEST_SRC_DIR}/googletest/include ${COMM_GTEST_SRC_DIR}/googlemock/include
            )

    target_compile_definitions(${_NAME}
            PUBLIC
            ${CC_TEST_DEFINES}
            )
    target_compile_options(${_NAME}
            PRIVATE ${CC_TEST_COPTS}
            )

    target_link_libraries(${_NAME}
            PUBLIC ${CC_TEST_DEPS}
            PRIVATE ${CC_TEST_LINKOPTS}
            )
    # Add all targets to a a folder in the IDE for organization.
    set_property(TARGET ${_NAME} PROPERTY FOLDER ${COMM_IDE_FOLDER}/tests)

    add_test(NAME ${_NAME} COMMAND ${_NAME})
endfunction()
