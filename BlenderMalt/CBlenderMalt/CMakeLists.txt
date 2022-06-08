cmake_minimum_required(VERSION 3.10)

SET(CMAKE_CXX_STANDARD 17)
# set(CMAKE_GENERATOR_PLATFORM x64)

project(CBlenderMalt)

SET(CMAKE_BUILD_TYPE Release)
SET(BUILD_SHARED_LIBS ON)

add_library(CBlenderMalt CBlenderMalt.cpp)
target_include_directories(CBlenderMalt PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/blender_dna)

install(TARGETS CBlenderMalt CONFIGURATIONS Release DESTINATION ${PROJECT_SOURCE_DIR})

