cmake_minimum_required (VERSION 3.9)
project(PackageTest CXX)


set(LIBTCOD_CATCH2 "find_package" CACHE STRING "How this library will be linked.")
set_property(CACHE LIBTCOD_CATCH2 PROPERTY STRINGS "find_package")

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake OPTIONAL RESULT_VARIABLE CONAN_FILE)
if(CONAN_FILE)
    conan_basic_setup(KEEP_RPATHS TARGETS)
    set(LINK_TARGETS PRIVATE ${CONAN_LIBS})
else()
    set(LINK_TARGETS PRIVATE LIBTCOD::LIBTCOD)
endif()


if (APPLE)
    set(CMAKE_INSTALL_RPATH "@executable_path")
else()
    set(CMAKE_INSTALL_RPATH "$ORIGIN")
endif()
set(CMAKE_BUILD_WITH_INSTALL_RPATH ON)

add_executable(unittest unittest.cpp)
target_link_libraries(unittest ${LINK_TARGETS})
target_compile_features(unittest PUBLIC cxx_std_14)
target_compile_definitions(unittest PRIVATE _CRT_SECURE_NO_WARNINGS)

if(CONAN_FILE)
    target_link_libraries(unittest PRIVATE CONAN_PKG::Catch2)
elseif(LIBTCOD_CATCH2 STREQUAL "find_package")
    find_package(Catch2 CONFIG REQUIRED)
    target_link_libraries(unittest PRIVATE Catch2::Catch2)
else()
    message(FATAL_ERROR "Unknown option for LIBTCOD_CATCH2: '${LIBTCOD_CATCH2}'")
endif()

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME example
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND example)
