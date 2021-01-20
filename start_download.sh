#!/bin/bash

readonly CUR_DIR=$(cd $(dirname "$0"); pwd)

function get_python_cmd()
{
    # try this first
    py36="/usr/bin/python3.6"
    if [ -f ${py36} ];then
        echo ${py36}
        return 0
    fi

    # centos 8.2
    platform_python="/usr/libexec/platform-python3.6"
    if [ -f ${platform_python} ];then
        echo ${platform_python}
        return 0
    fi

    # this python3 mybe replace by user and have no lzma or other module
    have_python3=`command -v python3 | wc -l`
    if [ ${have_python3} -eq 1 ];then
        echo python3
        return 0
    fi

    have_yum=`command -v yum | wc -l`
    if [ ${have_yum} -eq 1 ];then
        yum install -y python3 > install_python3.log
    fi

    have_apt=`command -v apt | wc -l`
    if [ ${have_apt} -eq 1 ];then
        DEBIAN_FRONTEND=noninteractive apt -y install python3 > install_python3.log
    fi
    echo python3
    return 0
}

function main()
{
    pycmd=$(get_python_cmd)
    ${pycmd} ${CUR_DIR}/downloader/downloader.py
    ${pycmd} ${CUR_DIR}/downloader/other_downloader.py
}

main $*
