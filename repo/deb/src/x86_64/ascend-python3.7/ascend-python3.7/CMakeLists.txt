cmake_minimum_required(VERSION 3.4.1)
project(ascend-python37)

include(ExternalProject)

message("CMAKE_BINARY_DIR=${CMAKE_BINARY_DIR}")

if(DEFINED ENV{PYPI_URL})
    set(PYPI_URL $ENV{PYPI_URL})
else()
    set(PYPI_URL https://repo.huaweicloud.com/repository/pypi)
endif()

if(DEFINED ENV{PYTHON_URL})
    set(PY_URL $ENV{PYTHON_URL})
else()
    set(PY_URL "https://repo.huaweicloud.com/python/3.7.5/Python-3.7.5.tar.xz")
endif()

ExternalProject_Add(Python-3.7.5
  URL ${PY_URL}
  PREFIX "${CMAKE_BINARY_DIR}"
  CONFIGURE_COMMAND cd ${CMAKE_BINARY_DIR}/src/Python-3.7.5 && ./configure --prefix=/usr/local/python3.7.5 --enable-shared
  BUILD_COMMAND make -C ${CMAKE_BINARY_DIR}/src/Python-3.7.5 -j4
  INSTALL_COMMAND make -C ${CMAKE_BINARY_DIR}/src/Python-3.7.5 install DESTDIR=${CMAKE_CURRENT_LIST_DIR}/files
  COMMAND LD_LIBRARY_PATH=${CMAKE_CURRENT_LIST_DIR}/files/usr/local/python3.7.5/lib:$ENV{LD_LIBRARY_PATH} && ${CMAKE_CURRENT_LIST_DIR}/files/usr/local/python3.7.5/bin/python3.7 -m ensurepip
  COMMAND LD_LIBRARY_PATH=${CMAKE_CURRENT_LIST_DIR}/files/usr/local/python3.7.5/lib:$ENV{LD_LIBRARY_PATH} && ${CMAKE_CURRENT_LIST_DIR}/files/usr/local/python3.7.5/bin/python3.7 -m pip install --upgrade pip -f  ${PYPI_URL}
  COMMAND LD_LIBRARY_PATH=${CMAKE_CURRENT_LIST_DIR}/files/usr/local/python3.7.5/lib:$ENV{LD_LIBRARY_PATH} && ${CMAKE_CURRENT_LIST_DIR}/files/usr/local/python3.7.5/bin/python3.7 -m pip install -r ${CMAKE_CURRENT_LIST_DIR}/requirements.txt -f ${PYPI_URL}
)
