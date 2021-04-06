#!/bin/bash
readonly TRUE=1
readonly FALSE=0
readonly BASE_DIR=$(cd "$(dirname $0)" > /dev/null 2>&1; pwd -P)
readonly CUR_DIR=$(cd $(dirname "$0"); pwd)
OS_LIST=""

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
        sudo -E yum install -y python3 > install_python3.log
    fi

    have_apt=`command -v apt | wc -l`
    if [ ${have_apt} -eq 1 ];then
        sudo -E DEBIAN_FRONTEND=noninteractive apt -y install python3 > install_python3.log
    fi
    echo python3
    return 0
}

function print_usage()
{
    echo "Usage: ./start_download.sh [options]"
    echo " Options:"
    echo "--help  -h               Print this message"
    echo "--os-list=<OS1>,<OS2>    Specific OS list to download, supported os are:"
    for os in $(find ${BASE_DIR}/downloader/config -mindepth 1 -type d  | sort)
    do
        os_name=$(basename ${os})
        echo "                         ${os_name}"
    done
    exit 0
}

function parse_script_args() {
    if [ $# = 0 ];then
        print_usage
    fi
    while true; do
        case "$1" in
        --help | -h)
            print_usage
            ;;
        --os-list=*)
            OS_LIST=$(echo $1 | cut -d"=" -f2 | sed "s/\(\*\|?\|{\|}\|\[\|\]\|\/\)//g")
            shift
            ;;
        --download=*)
            PKG_LIST=$(echo $1| cut -d"=" -f2-)
            shift
            ;;
        *)
            if [ "x$1" != "x" ]; then
                echo "ERROR" "Unsupported parameters: $1"
                print_usage
            fi
            break
            ;;
        esac
    done
}

function check_script_args()
{
    if [ -z ${OS_LIST} ];then
        echo "ERROR" "--os-list parameter is invalid"
        print_usage
    fi
    local unsupport=${FALSE}
    IFS=','
    for os in ${OS_LIST}
    do
        if [ -z ${os} ] || [ ! -d ${BASE_DIR}/downloader/config/${os} ];then
            echo "Error: not support download for ${os}"
            unsupport=${TRUE}
        fi
    done
    unset IFS
    if [ ${unsupport} == ${TRUE} ];then
        print_usage
    fi
}

function main()
{
    parse_script_args $*
    local pycmd=$(get_python_cmd)
    local download_cmd=""
    if [ ! -z "${PKG_LIST}" ];then
        download_cmd="--download ${PKG_LIST}"
    fi
    ${pycmd} ${CUR_DIR}/downloader/downloader.py --os-list ${OS_LIST} ${download_cmd}
}

main $*
