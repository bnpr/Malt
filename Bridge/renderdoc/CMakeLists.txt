cmake_minimum_required(VERSION 3.10)

# set(CMAKE_GENERATOR_PLATFORM x64)

project(RenderDocWrapper)

SET(CMAKE_BUILD_TYPE Release)
SET(BUILD_SHARED_LIBS ON)

add_library(renderdoc_wrapper renderdoc_wrapper.c)

if(NOT WIN32)
    target_link_libraries(renderdoc_wrapper dl)
endif()

install(TARGETS renderdoc_wrapper CONFIGURATIONS Release DESTINATION ${PROJECT_SOURCE_DIR})

