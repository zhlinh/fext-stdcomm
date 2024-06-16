cmake_minimum_required(VERSION 3.14)

set(CMAKE_INSTALL_PREFIX "${CMAKE_BINARY_DIR}" CACHE PATH "Installation directory" FORCE)
message(STATUS "CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}")

# main project root
set(MAIN_PROJECT_ROOT_DIR ${CMAKE_SOURCE_DIR})
string(REPLACE "/" ";" TEMP_SPLIT_ITEMS "${CMAKE_SOURCE_DIR}")
list(GET TEMP_SPLIT_ITEMS -1 MAIN_PROJECT_NAME)

project(${MAIN_PROJECT_NAME})

message(STATUS "MAIN_PROJECT_NAME=${MAIN_PROJECT_NAME}")

find_package(Doxygen)

IF(NOT DOXYGEN_FOUND)
    message(STATUS "No Doxygen found. Documentation won't be built")
ELSE()
    CONFIGURE_FILE(Doxyfile.in Doxyfile
            NEWLINE_STYLE LF
            @ONLY
    )
    CONFIGURE_FILE(Doxyfile.zh-cn.in Doxyfile.zh-cn
            NEWLINE_STYLE LF
            @ONLY
    )

    file(GLOB DOXYFILES ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile*)

    add_custom_command(OUTPUT html
        COMMAND ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile
        COMMAND ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile.zh-cn
        DEPENDS ${MARKDOWN_DOC} ${SOURCES} ${DOXYFILES}
        WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/../
        )
    add_custom_target(docs ALL DEPENDS html)

    install(DIRECTORY ${CMAKE_SOURCE_DIR}/_html
        DESTINATION ${CMAKE_INSTALL_PREFIX}/${CMAKE_SYSTEM_NAME}.out
        COMPONENT docs)
ENDIF()
