cmake_minimum_required(VERSION 3.10)

# set(CMAKE_GENERATOR_PLATFORM x64)

project(Ipc)

SET(CMAKE_BUILD_TYPE Release)
SET(BUILD_SHARED_LIBS ON)

add_library(Ipc ipc.c)

if(NOT WIN32)
    target_link_libraries(Ipc pthread)
    if(NOT APPLE)
        target_link_libraries(Ipc rt)
    endif()
endif()

install(TARGETS Ipc CONFIGURATIONS Release DESTINATION ${PROJECT_SOURCE_DIR})

