cmake_minimum_required(VERSION 3.10)

# set(CMAKE_GENERATOR_PLATFORM x64)

project(CBlenderMalt)

SET(CMAKE_BUILD_TYPE Release)
SET(BUILD_SHARED_LIBS ON)

add_library(CBlenderMalt CBlenderMalt.cpp)

install(TARGETS CBlenderMalt CONFIGURATIONS Release DESTINATION ${PROJECT_SOURCE_DIR})

