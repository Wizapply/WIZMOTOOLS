# Sets the minimum version of CMake required to build the native
# library. You should either keep the default value or only pass a
# value of 3.2.0 or lower.

cmake_minimum_required(VERSION 3.2.0)

# Creates and names a library, sets it as either STATIC
# or SHARED, and provides the relative paths to its source code.
# You can define multiple libraries, and CMake builds it for you.
# Gradle automatically packages shared libraries with your APK.

project (wizmo_app)

set(CMAKE_CXX_COMPILER g++)
set(CMAKE_CXX_FLAGS "-std=c++11 -Wall") #-m32
set(CMAKE_CXX_FLAGS_DEBUG "-g3 -O0 -march=native -pg -fsigned-char")
set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-g -O3 -march=native -pg -fsigned-char")
set(CMAKE_CXX_FLAGS_RELEASE "-O2 -s -DNDEBUG -march=native -fomit-frame-pointer -fpic -ffunction-sections -fsigned-char")
set(CMAKE_CXX_FLAGS_MINSIZEREL "-Os -s -DNDEBUG -march=native")

include_directories(./../../include ./../../src/)

if(CMAKE_SYSTEM_PROCESSOR MATCHES "arm" OR CMAKE_SYSTEM_PROCESSOR MATCHES "aarch")
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
        set(ARCH "aarch64")
    else()
        set(ARCH "arm")
    endif()
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^mips.*")
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
        set(ARCH "mips64el")
    else()
        set(ARCH "mipsel")
    endif()
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^ppc.*")
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
        set(ARCH "ppc64le")
    else()
        message(FATAL_ERROR "Architecture is not supported")
    endif()
else()
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
        set(ARCH "x86_64")
    else()
        set(ARCH "x86")
    endif()
endif()

IF(ARCH STREQUAL "aarch64")
  link_directories(./../../bin/aarch64)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ./../../bin/aarch64)
ELSEIF(ARCH STREQUAL "arm")
  link_directories(./../../bin/armv7l)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ./../../bin/armv7l)
ELSEIF(ARCH STREQUAL "x86_64")
  link_directories(./../../bin/x64)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ./../../bin/x64)
ELSE()
  link_directories(./../../bin/x86)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ./../../bin/x86)
ENDIF()

# cpp files
add_executable(wizmo_app ./../../src/main.cpp)

# Specifies libraries CMake should link to your target library. You
# can link multiple libraries, such as libraries you define in the
# build script, prebuilt third-party libraries, or system libraries.

target_link_libraries(wizmo_app # Specifies the target library.
                      wizmo pthread)

add_definitions(-DLINUX)
