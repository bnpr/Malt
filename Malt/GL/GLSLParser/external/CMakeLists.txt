include(FetchContent)
include(ExternalProject)

FetchContent_Declare(
  pegtl
  GIT_REPOSITORY https://github.com/taocpp/PEGTL
  GIT_TAG        3.2.1
)
FetchContent_MakeAvailable(pegtl)


FetchContent_Declare(
  rapidjson
  GIT_REPOSITORY https://github.com/Tencent/rapidjson
  GIT_TAG        00dbcf2c6e03c47d6c399338b6de060c71356464
)
set(RAPIDJSON_BUILD_DOC OFF CACHE INTERNAL "")
set(RAPIDJSON_BUILD_EXAMPLES OFF CACHE INTERNAL "")
set(RAPIDJSON_BUILD_TESTS OFF CACHE INTERNAL "")
FetchContent_MakeAvailable(rapidjson)
FetchContent_GetProperties(rapidjson)
set(RAPIDJSON_INCLUDE_DIR ${rapidjson_SOURCE_DIR}/include PARENT_SCOPE)

#[[
ExternalProject_Add(
  rapidjson
  PREFIX ${CMAKE_BINARY_DIR}/rapidjson
  GIT_REPOSITORY https://github.com/Tencent/rapidjson
  GIT_TAG        00dbcf2c6e03c47d6c399338b6de060c71356464
  CONFIGURE_COMMAND ""
  BUILD_COMMAND ""
  INSTALL_COMMAND ""
  LOG_DOWNLOAD ON
)
ExternalProject_Get_Property(rapidjson SOURCE_DIR)
set(RAPIDJSON_INCLUDE_DIR ${SOURCE_DIR}/include PARENT_SCOPE)
]]

