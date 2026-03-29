include(FetchContent)
include(ExternalProject)

FetchContent_Declare(
  pegtl
  GIT_REPOSITORY https://github.com/taocpp/PEGTL
  GIT_TAG        3.2.8
)
FetchContent_MakeAvailable(pegtl)


FetchContent_Declare(
  rapidjson
  GIT_REPOSITORY https://github.com/Tencent/rapidjson
  GIT_TAG        24b5e7a8b27f42fa16b96fc70aade9106cf7102f
)
set(RAPIDJSON_BUILD_DOC OFF CACHE INTERNAL "")
set(RAPIDJSON_BUILD_EXAMPLES OFF CACHE INTERNAL "")
set(RAPIDJSON_BUILD_TESTS OFF CACHE INTERNAL "")
FetchContent_MakeAvailable(rapidjson)
FetchContent_GetProperties(rapidjson)
set(RAPIDJSON_INCLUDE_DIR ${rapidjson_SOURCE_DIR}/include PARENT_SCOPE)
