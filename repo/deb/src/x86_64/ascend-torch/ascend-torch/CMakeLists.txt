cmake_minimum_required(VERSION 3.4.1)
project(ascend-torch)

message("CMAKE_BINARY_DIR=${CMAKE_BINARY_DIR}")

SET(FILE_URL "https://obs-9be7.obs.cn-east-2.myhuaweicloud.com/turing/resource/PTAdapter/V100R020C10/torch-1.5.0%2Bascend-cp37-cp37m-linux_x86_64.whl")
SET(FILE_NAME "torch-1.5.0+ascend-cp37-cp37m-linux_x86_64.whl")

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
