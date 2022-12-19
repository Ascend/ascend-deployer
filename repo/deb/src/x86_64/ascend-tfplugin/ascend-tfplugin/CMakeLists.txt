cmake_minimum_required(VERSION 3.4.1)
project(ascend-tfplugin)

SET(FILE_URL "https://repo.huaweicloud.com/ascend/autoarchive/CANN/CANN%20V100R020C20/Ascend-cann-tfplugin_20.2.alpha001_linux-x86_64.run")
SET(FILE_NAME "Ascend-cann-tfplugin_20.2.alpha001_linux-x86_64.run")

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
