cmake_minimum_required(VERSION 3.10)

# set(CMAKE_GENERATOR_PLATFORM x64)

project(CMalt)

SET(CMAKE_BUILD_TYPE Release)
SET(BUILD_SHARED_LIBS ON)

add_library(CMalt MaltMeshes.cpp)

install(TARGETS CMalt CONFIGURATIONS Release DESTINATION ${PROJECT_SOURCE_DIR})

