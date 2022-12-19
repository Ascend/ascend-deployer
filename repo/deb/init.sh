#!/bin/bash
readonly VERSION="20.2.0"

function create_package()
{
    local name=${1}
    local arch=${2}
    if [ -d src/${arch}/${name}/${name} ];then
        echo "${name} alreay exist"
        return
    fi
    mkdir -p src/${arch}/${name}/${name}
    cd src/${arch}/${name}/${name}
    dh_make -y -c apache --native --single -p ${name}_${VERSION} --email liuyuncheng@huawei.com
    cd -
}

function init_all()
{
    create_package ascend-tensorflow x86_64
    create_package ascend-tensorflow aarch64

    create_package ascend-torch x86_64
    create_package ascend-torch aarch64

    create_package ascend-npu x86_64
    create_package ascend-npu aarch64

    create_package ascend-tfplugin x86_64
    create_package ascend-tfplugin aarch64

    create_package ascend-cann-toolkit x86_64
    create_package ascend-cann-toolkit aarch64

    create_package ascend-cann-toolbox x86_64
    create_package ascend-cann-toolbox aarch64
}

if [ $# -eq 1 ];then
    create_package ${1} x86_64
    create_package ${1} aarch64
elif [ $# -eq 2 ];then
    init_all
else
    echo "please input package name"
fi
