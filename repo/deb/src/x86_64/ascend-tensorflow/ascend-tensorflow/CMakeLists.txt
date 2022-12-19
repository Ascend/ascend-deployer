cmake_minimum_required(VERSION 3.4.1)
project(ascend-tensorflow)

message("CMAKE_BINARY_DIR=${CMAKE_BINARY_DIR}")

SET(FILE_URL "https://repo.huaweicloud.com/repository/pypi/packages/61/d0/aa81ec732f68fef387b0f097a5c29d4d944de5f24f77ad9b0f7d2517f871/tensorflow_cpu-1.15.0-cp37-cp37m-manylinux2010_x86_64.whl")
SET(FILE_NAME "tensorflow_cpu-1.15.0-cp37-cp37m-manylinux2010_x86_64.whl")

if (DEFINED ENV{RESOURCE_DIR})
    message("RESOURCE_DIR = $ENV{RESOURCE_DIR}")
    if(NOT EXISTS $ENV{RESOURCE_DIR}/${FILE_NAME})
        message("RESOURCE_DIR defined, download from ${FILE_URL}")
	file(DOWNLOAD ${FILE_URL}
	    "$ENV{RESOURCE_DIR}/${FILE_NAME}"
            TIMEOUT 120
            INACTIVITY_TIMEOUT 120
            SHOW_PROGRESS)
    endif()
    message("copy from $ENV{RESOURCE_DIR}/${FILE_NAME}")
    file(COPY "$ENV{RESOURCE_DIR}/${FILE_NAME}"
        DESTINATION "${CMAKE_CURRENT_LIST_DIR}/files/")
else()
    message("RESOURCE_DIR not defined, download from ${FILE_URL}")
    file(DOWNLOAD ${FILE_URL}
	"${CMAKE_CURRENT_LIST_DIR}/files/${FILE_NAME}"
        TIMEOUT 120
        INACTIVITY_TIMEOUT 120
        SHOW_PROGRESS)
endif()
