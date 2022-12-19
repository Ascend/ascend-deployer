#!/bin/bash
readonly VERSION="20.2.0"

function build_package()
{
    local name=${1}
    local arch=${2}
    if [ ! -d src/${arch}/${name}/${name} ];then
        echo "${name} ${arch} not exist"
        return
    fi
    cd src/${arch}/${name}/${name}
    dpkg-buildpackage --no-sign
    cd -
    cp -rf src/${arch}/${name}/*.deb  mirror/pool
}

export PYPI_URL="https://repo.huaweicloud.com/repository/pypi"
export PYTHON_URL="https://repo.huaweicloud.com/python/3.7.5/Python-3.7.5.tar.xz"

function build_all()
{

    mkdir -p mirror/pool
    local arch=$(uname -m)

    build_package ascend-python3.7 ${arch}
    build_package ascend-mindspore ${arch}
    build_package ascend-tensorflow ${arch}
    build_package ascend-torch ${arch}
    build_package ascend-npu ${arch}
    build_package ascend-tfplugin ${arch}
    build_package ascend-cann-nnrt ${arch}
    build_package ascend-cann-nnae ${arch}
    build_package ascend-cann-toolkit ${arch}
}

mkdir -p resources
export RESOURCE_DIR=./resources

build_all
cd mirror
dpkg-scanpackages pool | gunzip > Packages.gz
cd -
