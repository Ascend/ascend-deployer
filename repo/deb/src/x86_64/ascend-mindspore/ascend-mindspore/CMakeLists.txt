cmake_minimum_required(VERSION 3.4.1)
project(ascend-mindspore)

message("CMAKE_BINARY_DIR=${CMAKE_BINARY_DIR}")

SET(FILE_URL "https://ms-release.obs.cn-north-4.myhuaweicloud.com/1.1.0/MindSpore/cpu/ubuntu_x86/mindspore-1.1.0-cp37-cp37m-linux_x86_64.whl")
SET(FILE_NAME "mindspore-1.1.0-cp37-cp37m-linux_x86_64.whl")

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
