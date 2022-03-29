#!/bin/bash
readonly TRUE=1
readonly FALSE=0
readonly BASE_DIR=$(cd "$(dirname $0)" > /dev/null 2>&1; pwd -P)
readonly LOG_SIZE_THRESHOLD=$((20*1024*1024))
readonly LOG_COUNT_THRESHOLD=5
OS_LIST=""
PKG_LIST=""

function is_safe_owned_file()
{
    local path=$1
    local user_id=$(stat -c %u ${path})
    local group_id=$(stat -c %g ${path})
    if [ ! -n "${user_id}" ] || [ ! -n "${group_id}" ];then
        echo "user or group not exist"
        return 1
    fi
    if [ $(stat -c '%A' ${path}|cut -c6) == w ] || [ $(stat -c '%A' ${path}|cut -c9) == w ];then
        echo "${path} does not comply with security rules."
        return 1
    fi
    if [ ${user_id} != "0" ] && [ ${user_id} != ${UID} ];then
        echo "The path is not owned by root or current user"
        return 1
    fi
    return 0
}

function is_safe_owned_dir()
{
    local path=$1
    local user_id=$(stat -c %u ${path})
    local group_id=$(stat -c %g ${path})
    if [ ! -n "${user_id}" ] || [ ! -n "${group_id}" ];then
        echo "user or group not exist"
        return 1
    fi
    if [ $(stat -c '%A' ${path}|cut -c6) == w ] || [ $(stat -c '%A' ${path}|cut -c9) == w ];then
        echo "${path} does not comply with security rules."
        return 1
    fi
    if [ ${user_id} != "0" ] && [ ${user_id} != ${UID} ];then
        echo "The path is not owned by root or current user"
        return 1
    fi
    return 0
}

function safe_file()
{
    local cur_path=$(realpath "$1")
    is_safe_owned_file ${cur_path}
    if [ $? -eq 1 ];then
        exit 1
    fi
    cur_path=$(dirname "$cur_path")
    safe_dir ${cur_path}
    if [ $? -eq 1 ];then
        exit 1
    fi
    return 0
}

function safe_dir()
{
    local cur_path=$1
    while [ "${cur_path}" != "/" ];do
        is_safe_owned_dir ${cur_path}
        if [ $? -eq 1 ];then
            exit 1
        fi
        cur_path=$(dirname "$cur_path")
    done
    return 0
}

function check_exec_file()
{
    local exec_files=(cat date whoami who awk sed grep ls python3 chmod find rm basename dirname mv touch which pwd sort stat cut realpath)
    for i in ${exec_files[@]};do safe_file $(which $i);done
    local files=(yum apt)
    for j in ${files[@]};do
    which $j > /dev/null
    if [ $? -eq 0 ];then
        safe_file $(which $j)
    fi
    done
}

function operation_log_info()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    local IP_N=$(who am i | awk '{print $NF}' | sed 's/[()]//g')
    echo "${DATE_N} ${USER_N}@${IP_N} [INFO] $*" >> ${BASE_DIR}/downloader_operation.log
}

function log_info()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    local IP_N=$(who am i | awk '{print $NF}' | sed 's/[()]//g')
    echo "[INFO] $*"
    echo "${DATE_N} ${USER_N}@${IP_N} [INFO] $*" >> ${BASE_DIR}/downloader.log
}

function log_error()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    local IP_N=$(who am i | awk '{print $NF}' | sed 's/[()]//g')
    echo "[ERROR] $*"
    echo "${DATE_N} ${USER_N}@${IP_N} [ERROR] $*" >> ${BASE_DIR}/downloader.log
}

function rotate_log()
{
    local log_list=$(ls $1* | sort -r)
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
    if [[ ! -e $1 ]];then
        touch $1
    fi
    local log_size=$(ls -l $1 | awk '{ print $5 }')
    if [[ ${log_size} -ge ${LOG_SIZE_THRESHOLD} ]];then
        rotate_log $1
    fi
}

function set_permission()
{
    chmod 750 ${BASE_DIR}
    chmod 550 $0
    chmod 600 ${BASE_DIR}/downloader.log ${BASE_DIR}/downloader_operation.log 2>/dev/null
    chmod 400 ${BASE_DIR}/downloader.log.? ${BASE_DIR}/downloader_operation.log.? 2>/dev/null
}

function get_python3()
{
    # try this first
    py36="/usr/bin/python3"
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
        log_error "you are not root user and python3 is not available, please install python3 first by yourself"
        return 1
    fi

    have_yum=$(command -v yum | wc -l)
    if [ ${have_yum} -eq 1 ];then
        log_info "yum install -y python3"
        yum install -y python3 > ${BASE_DIR}/tmp.log 2>&1
        local install_result=$?
        cat ${BASE_DIR}/tmp.log >> ${BASE_DIR}/downloader.log
        cat ${BASE_DIR}/tmp.log && rm -rf ${BASE_DIR}/tmp.log
        if [[ ${install_result} != 0 ]];then
            log_error "python3 is not available and yum install -y python3 failed, please check network or yum"
            return 1
        fi

    fi

    have_apt=$(command -v apt | wc -l)
    if [ ${have_apt} -eq 1 ];then
        log_info "apt install -y python3"
        apt install -y python3 > ${BASE_DIR}/tmp.log 2>&1
        local install_result=$?
        cat ${BASE_DIR}/tmp.log >> ${BASE_DIR}/downloader.log
        cat ${BASE_DIR}/tmp.log && rm -rf ${BASE_DIR}/tmp.log
        if [[ ${install_result} != 0 ]];then
            log_error "python3 is not available and apt install -y python3 failed, please check network or apt"
            return 1
        fi
    fi

    have_python3=$(command -v python3 | wc -l)
    if [ ${have_python3} -eq 0 ];then
        log_error "python3 is not available, please check python3"
        return 1
    fi
}

function print_usage()
{
    echo "Usage: ./start_download.sh [-h] [--os-list=OS_LIST] [--download=PACKAGES]]"
    echo ""
    echo " optional arguments:"
    echo "--help  -h               show this help message and exit"
    echo "--os-list=<OS1>,<OS2>    Specific OS list to download, supported os are:"
    for os in $(find ${BASE_DIR}/downloader/config -maxdepth 1 -mindepth 1 -type d | sort -V)
    do
        os_name=$(basename ${os})
        echo "                         ${os_name}"
    done
    echo "--download=<PK1>,<PK2>==<Version>"
    echo "                         Specific package list to download, supported packages are:"
    for package_json in $(find ${BASE_DIR}/downloader/software -maxdepth 1 -type f -name "*.json" | sort -V)
    do
        package=$(basename ${package_json} .json | sed "s/_/==/g")
        echo "                         ${package}"
    done
    echo -e "\n  notes: When <Version> is missing, <PK> is the latest.\n"
}

function parse_script_args() {
    if [ $# = 0 ];then
        print_usage
        return 2
    fi
    while true; do
        case "$1" in
        --help | -h)
            print_usage
            return 2
            ;;
        --os-list=*)
            OS_LIST=$(echo $1 | cut -d"=" -f2)
            shift
            ;;
        --download=*)
            PKG_LIST=$(echo $1| cut -d"=" -f2-)
            shift
            ;;
        *)
            if [ "x$1" != "x" ]; then
                log_error "Unsupported parameters: $1"
                print_usage
                return 1
            fi
            break
            ;;
        esac
    done
}

function check_script_args()
{
    if [ -z "${OS_LIST}" ] && [ -z "${PKG_LIST}" ];then
        log_error "--os-list or --download expected one argument at least"
        print_usage
        return 1
    fi

    if [ -z "${OS_LIST}" ] && [[ "${PKG_LIST}" =~ "MindSpore" ]];then
        log_error "os_list can not be none when downloading mindspore"
        print_usage
        return 1
    fi

    if [ -z "${OS_LIST}" ] && [[ "${PKG_LIST}" =~ "MindStudio" ]];then
        log_error "os_list can not be none when downloading MindStudio"
        print_usage
        return 1
    fi

    # --os-list
    if $(echo "${OS_LIST}" | grep -Evq '^[a-zA-Z0-9._,-]*$');then
        log_error "--os-list ${OS_LIST} is invalid"
        print_usage
        return 1
    fi
    local unsupport=${FALSE}
    IFS=','
    for os in ${OS_LIST}
    do
        if [ "${os}" = "." ] || [ ! -d ${BASE_DIR}/downloader/config/${os} ];then
            log_error "not support download for ${os}"
            unsupport=${TRUE}
        fi
    done
    unset IFS
    if [ ${unsupport} == ${TRUE} ];then
        print_usage
        return 1
    fi

    # --download
    if $(echo "${PKG_LIST}" | grep -Evq '^[a-zA-Z0-9._,=]*$');then
        log_error "--download ${PKG_LIST} is invalid"
        print_usage
        return 1
    fi
    local unsupport=${FALSE}
    IFS=','
    for package in ${PKG_LIST}
    do
        case "${package}" in
        CANN|MindStudio|MindSpore)
            continue
            ;;
        *)
        local name_version=$(echo ${package} | awk -F== '{print $1"_"$2}')
            if [ ! -f ${BASE_DIR}/downloader/software/${name_version}.json ];then
                log_error "not support download for ${package}"
                unsupport=${TRUE}
            fi
            ;;
        esac
    done
    unset IFS
    if [ ${unsupport} == ${TRUE} ];then
        print_usage
        return 1
    fi
}

function main()
{
    check_exec_file
    check_log ${BASE_DIR}/downloader.log
    check_log ${BASE_DIR}/downloader_operation.log
    set_permission
    parse_script_args $*
    parse_status=$?
    if [[ ${parse_status} != 0 ]];then
        return ${parse_status}
    fi

    check_script_args
    if [[ $? != 0 ]];then
        return 1
    fi

    get_python3 >/dev/null 2>&1
    if [[ $? == 0 ]];then
        local pycmd=$(get_python3)
    else
        install_python3
        if [[ $? != 0 ]];then
            return 1
        fi
        local pycmd="python3"
    fi
    local os_cmd=""
    if [ ! -z "${OS_LIST}" ];then
        os_cmd="--os-list ${OS_LIST}"
    fi
    local download_cmd=""
    if [ ! -z "${PKG_LIST}" ];then
        download_cmd="--download ${PKG_LIST}"
    fi
    log_info "${pycmd} $(basename ${BASE_DIR})/downloader/downloader.py ${os_cmd} ${download_cmd}"
    ${pycmd} ${BASE_DIR}/downloader/downloader.py ${os_cmd} ${download_cmd}
}

main $*
main_status=$?
if [[ ${main_status} != 0 ]] && [[ ${main_status} != 2 ]];then
    operation_log_info "parameter error,run failed"
else
    operation_log_info "$0 $*: Success"
fi
exit ${main_status}
