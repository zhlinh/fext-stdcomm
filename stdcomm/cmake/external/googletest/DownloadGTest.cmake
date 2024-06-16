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

# Integrates googletest at configure time.  Based on the instructions at
# https://github.com/google/googletest/tree/master/googletest#incorporating-into-an-existing-cmake-project

# Set up the external googletest project, downloading the latest from Github
# master if requested.
configure_file(
        ${CMAKE_CURRENT_LIST_DIR}/CMakeLists.txt.in
        ${CMAKE_BINARY_DIR}/googletest-external/CMakeLists.txt
        NEWLINE_STYLE LF
)
message(STATUS "Configuring googletest from ${CMAKE_BINARY_DIR}/googletest-external")

set(COMM_SAVE_CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS})
set(COMM_SAVE_CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY})
if (BUILD_SHARED_LIBS)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DGTEST_CREATE_SHARED_LIBRARY=1")
endif()

# Configure and build the googletest source.
execute_process(COMMAND ${CMAKE_COMMAND} -G "${CMAKE_GENERATOR}" .
        RESULT_VARIABLE result
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/googletest-external)
if(result)
    message(FATAL_ERROR "CMake step for googletest failed: ${result}")
endif()

execute_process(COMMAND ${CMAKE_COMMAND} --build .
        RESULT_VARIABLE result
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/googletest-external)
if(result)
    message(FATAL_ERROR "Build step for googletest failed: ${result}")
endif()

set(CMAKE_CXX_FLAGS ${COMM_SAVE_CMAKE_CXX_FLAGS})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${COMM_SAVE_CMAKE_RUNTIME_OUTPUT_DIRECTORY})

# Prevent overriding the parent project's compiler/linker settings on Windows
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

# Add googletest directly to our build. This defines the gtest and gtest_main
# targets.
add_subdirectory(${COMM_GTEST_SRC_DIR} ${COMM_GTEST_BUILD_DIR} EXCLUDE_FROM_ALL)