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

IF(USE_32BITOS)
  message([STATUS] "32bit Compile Mode.")  
  link_directories(./../../bin/x86)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ./../../bin/x86)
ELSE(USE_32BITOS)
  link_directories(./../../bin/x64)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ./../../bin/x64)
ENDIF(USE_32BITOS)

IF(USE_RPI)
  set(WIZMOLIB wizmoRPi)
ELSE(USE_RPI)
  set(WIZMOLIB wizmo)
ENDIF(USE_RPI)

# cpp files
add_executable(Main ./../../src/main.cpp)

# Specifies libraries CMake should link to your target library. You
# can link multiple libraries, such as libraries you define in the
# build script, prebuilt third-party libraries, or system libraries.

target_link_libraries(Main # Specifies the target library.
                      ${WIZMOLIB} pthread)

add_definitions(-DLINUX)
