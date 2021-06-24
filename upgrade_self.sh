#!/bin/bash
readonly BASE_DIR=$(cd "$(dirname $0)" > /dev/null 2>&1; pwd -P)
readonly LOG_SIZE_THRESHOLD=$((20*1024*1024))
readonly LOG_COUNT_THRESHOLD=5

function log_info()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    echo "[INFO] $*"
    echo "${DATE_N} ${USER_N} [INFO] $*" >> ${BASE_DIR}/install_python3.log
}

function log_error()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    echo "[ERROR] $*"
    echo "${DATE_N} ${USER_N} [ERROR] $*" >> ${BASE_DIR}/install_python3.log
}

function rotate_log()
{
    local log_list=$(ls ${BASE_DIR}/install_python3.log* | sort -r)
    for item in $log_list; do
        local suffix=${item##*.}
        local prefix=${item%.*}
        if [[ ${suffix} != "log" ]]; then
            if [[ ${suffix} -lt ${LOG_COUNT_THRESHOLD} ]];then
                suffix=$(($suffix+1))
                mv -f $item $prefix.$suffix
            fi
        else
            mv -f ${item} ${item}.1
            cat /dev/null > ${item}
        fi
    done
}

function check_log()
{
    local log_size=$(ls -l $BASE_DIR/install_python3.log | awk '{ print $5 }')
    if [[ ${log_size} -ge ${LOG_SIZE_THRESHOLD} ]];then
        rotate_log
    fi
}

function get_python3()
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
    have_python3=$(command -v python3 | wc -l)
    if [ ${have_python3} -eq 1 ];then
        echo python3
        return 0
    fi

    return 1
}

function install_python3()
{
    if [ $(id -u) -ne 0 ];then
        log_error "you are not root user and python3 is not available, please install python3 first by yourselt"
        exit 1
    fi

    if [[ ! -e ${BASE_DIR}/install_python3.log ]];then
        touch ${BASE_DIR}/install_python3.log
    fi
    chmod 600 ${BASE_DIR}/install_python3.log
    check_log

    have_yum=$(command -v yum | wc -l)
    if [ ${have_yum} -eq 1 ];then
        log_info "yum install -y python3"
        yum install -y python3 > ${BASE_DIR}/tmp.log 2>&1
        local install_result=$?
        cat ${BASE_DIR}/tmp.log >> ${BASE_DIR}/install_python3.log
        cat ${BASE_DIR}/tmp.log && rm -rf ${BASE_DIR}/tmp.log
        if [[ ${install_result} != 0 ]];then
            log_error "python3 is not available and yum install -y python3 failed, please check network or yum"
            exit 1
        fi

    fi

    have_apt=$(command -v apt | wc -l)
    if [ ${have_apt} -eq 1 ];then
        log_info "apt install -y python3"
        apt install -y python3 > ${BASE_DIR}/tmp.log 2>&1
        local install_result=$?
        cat ${BASE_DIR}/tmp.log >> ${BASE_DIR}/install_python3.log
        cat ${BASE_DIR}/tmp.log && rm -rf ${BASE_DIR}/tmp.log
        if [[ ${install_result} != 0 ]];then
            log_error "python3 is not available and apt install -y python3 failed, please check network or apt"
            exit 1
        fi
    fi

    have_python3=$(command -v python3 | wc -l)
    if [ ${have_python3} -eq 0 ];then
        log_error "python3 is not available, please check python3"
        exit 1
    fi
}

function main()
{
    get_python3 >/dev/null 2>&1
    if [[ $? == 0 ]];then
        local pycmd=$(get_python3)
    else
        install_python3
        local pycmd="python3"
    fi
    ${pycmd} ${BASE_DIR}/downloader/upgrade_self.py
}

main $*
