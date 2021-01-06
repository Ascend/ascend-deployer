#!/bin/bash

readonly TRUE=1
readonly FALSE=0
readonly kernel_version=$(uname -r)
readonly arch=$(uname -m)

function get_os_name()
{
    local os_name=$(grep "^NAME=" /etc/os-release)
    os_name="${os_name#*=}"
    os_name="${os_name%\"}"
    os_name="${os_name#\"}"
    echo ${os_name}
}

readonly g_os_name=$(get_os_name)

function get_os_version()
{
    local ver=$(grep "^VERSION=" /etc/os-release)
    ver="${ver#*=}"
    ver="${ver%\"}"
    ver="${ver#\"}"
    echo ${ver}
}

function have_no_python_module
{
    ret=`python3.7 -c "import ${1}" 2>&1 | grep "No module" | wc -l`
    return ${ret}
}

function check_python375()
{
    if [ ! -d /usr/local/python3.7.5 ];then
        echo "Warning: no python3.7.5 installed"
        return ${FALSE}
    fi
    module_list="ctypes sqlite3 lzma"
    for module in ${module_list}
    do
        have_no_python_module ${module}
        ret=$?
        if [ ${ret} == ${TRUE} ];then
            echo "Warning: python3.7 have no moudle ${module}"
            return ${FALSE}
        fi
    done
    return ${TRUE}
}

function install_kernel_header_devel_euler()
{
    local os_name=$(get_os_name)
    if [ "${os_name}" != "EulerOS" ];then
        return
    fi

    local euler=""
    if [ -z "${os_version##*SP8*}" ];then
        euler="eulerosv2r8.${arch}"
    else
        euler="eulerosv2r9.${arch}"
    fi

    local kh=$(rpm -qa kernel-headers | wc -l)
    local kd=$(rpm -qa kernel-devel | wc -l)
    local kh_rpm=$(find ./resources/kernel/ -name "kernel-headers*" | sort -r | grep -m1 ${euler})
    local kd_rpm=$(find ./resources/kernel/ -name "kernel-devel*" | sort -r | grep -m1 ${euler})
    if [ ${kh} -eq 0 ] && [ -f "${kh_rpm}" ];then
        rpm -ivh --force --nodeps --replacepkgs ${kh_rpm}
    fi
    if [ ${kd} -eq 0 ] && [ -f "${kd_rpm}" ];then
        rpm -ivh --force --nodeps --replacepkgs ${kd_rpm}
    fi
}

function install_kernel_header_devel()
{
    local have_rpm=$(command -v rpm | wc -l)
    if [ ${have_rpm} -eq 0 ]; then
        return
    fi
    local kh_rpm=./resources/kernel/kernel-headers-${kernel_version}.rpm
    local kd_rpm=./resources/kernel/kernel-devel-${kernel_version}.rpm
    local kh=$(rpm -q kernel-headers | grep ${kernel_version} | wc -l)
    local kd=$(rpm -q kernel-devel | grep ${kernel_version} | wc -l)
    if [ ${kh} -eq 0 ] && [ -f ${kh_rpm} ];then
        rpm -ivh --force --nodeps --replacepkgs ${kh_rpm}
    fi
    if [ ${kd} -eq 0 ] && [ -f ${kd_rpm} ];then
        rpm -ivh --force --nodeps --replacepkgs ${kd_rpm}
    fi
}

function install_sys_packages()
{
    echo "install sys dependencies"
    install_kernel_header_devel
    install_kernel_header_devel_euler
    local have_rpm=$(command -v rpm | wc -l)
    local have_dnf=$(command -v dnf | wc -l)
    local have_dpkg=$(command -v dpkg | wc -l)

    local os_name=$(get_os_name)
    local os_version=$(get_os_version)
    local os_ver=""
    if [ "${os_name}" == "Ubuntu" ];then
        os_ver="Ubuntu_18.04"
    elif [ -z "${os_name##*CentOS*}" ];then
        if [ -z "${os_version##*7*}" ];then
            os_ver="CentOS_7.6"
        else
            os_ver="CentOS_8.2"
        fi
    elif [ ${os_name} == "EulerOS" ]; then
        if [ -z "${os_version##*SP8*}" ];then
            os_ver="EulerOS_2.0SP8"
        else
            os_ver="EulerOS_2.0SP9"
        fi
    elif [ -z "${os_name##*BigCloud*}" ];then
        os_ver="BigCloud_7.6"
    elif [ -z "${os_name##*Debian*}" ];then
        os_ver="Debian_9.9"
    elif [ -z "${os_name##*SLES*}" ];then
        os_ver="SLES_12.4"
    elif [ -z "${os_name##*Kylin*}" ];then
        if [ -z "${os_version##*V10*Tercel*}" ];then
            os_ver="Kylin_V10Tercel"
        fi
    fi

    if [ ${have_rpm} -eq 1 ]; then
        rpm -ivh --force --nodeps --replacepkgs ./resources/${os_ver}_${arch}/*.rpm
    elif [ ${have_dnf} -eq 1 ]; then
        rpm -ivh --force --nodeps --replacepkgs ./resources/${os_ver}_${arch}/*.rpm
    elif [ ${have_dpkg} -eq 1 ]; then
        export DEBIAN_FRONTEND=noninteractive && export DEBIAN_PRIORITY=critical; dpkg --force-all -i ./resources/${os_ver}_${arch}/*.deb
    fi
}

function install_python375()
{
    if [ ! -f ./resources/Python-3.7.5.tar.xz ];then
        echo "can't find Python-3.7.5.tar.xz"
        return
    fi
    echo "installing Python 3.7.5"
    mkdir -p ~/build
    tar -xvf ./resources/Python-3.7.5.tar.xz -C ~/build
    cd ~/build/Python-3.7.5
    ./configure --enable-shared --prefix=/usr/local/python3.7.5
    make -j4
    make install
    cd -
    python3.7 -m ensurepip
    python3.7 -m pip install --upgrade pip --no-index --find-links ./resources/pylibs
    if [ "${g_os_name}" == "EulerOS" ];then
        python3.7 -m pip install selinux --no-index --find-links ./resources/pylibs
    fi
    echo "export PATH=/usr/local/python3.7.5/bin:\$PATH" > /usr/local/ascendrc 2>/dev/null
    echo "export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:\$LD_LIBRARY_PATH" >> /usr/local/ascendrc 2>/dev/null
}

function install_ansible()
{
    python3.7 -m pip install ansible --no-index --find-links ./resources/pylibs
}

function process_install()
{
    IFS=','
    unsupport=${FALSE}
    for target in ${install_target}
    do
        if [ ! -f playbooks/install/install_${target}.yml ];then
            echo "Error: not support install for ${target}"
            unsupport=${TRUE}
        fi
    done
    if [ ${unsupport} == ${TRUE} ];then
        exit 1
    fi
    ping_all
    process_check
    if [ "x${nocopy_flag}" != "xy" ];then
        echo "ansible-playbook -i ./inventory_file playbooks/distribution.yml -e hosts_name=ascend"
        ansible-playbook -i ./inventory_file playbooks/distribution.yml -e "hosts_name=ascend"
    fi
    debug_cmd=""
    if [ "x${debug_flag}" == "xy" ];then
        debug_cmd="-v"
    fi
    for target in ${install_target}
    do
        echo "ansible-playbook -i ./inventory_file playbooks/install_${target}.yml -e hosts_name=ascend ${debug_cmd}"
        ansible-playbook -i ./inventory_file playbooks/install/install_${target}.yml -e "hosts_name=ascend" ${debug_cmd}
    done
    unset IFS
}

function process_uninstall()
{
    IFS=','
    not_supported=${FALSE}
    for target in ${uninstall_target}
    do
        if [ ! -f playbooks/uninstall/uninstall_${target}.yml ]; then
            echo "Error: not supported uninstall for ${target}"
            not_supported=${TRUE}
        fi
    done
    if [ "${not_supported}" == "${TRUE}" ]; then
        exit 1
    fi
    ping_all
    process_check
    debug_cmd=""
    if [ "x${debug_flag}" == "xy" ]; then
        debug_cmd="-v"
    fi
    for target in ${uninstall_target}
    do
        echo "ansible-playbook -i ./inventory_file playbooks/uninstall/uninstall_${target}.yml -e \"hosts_name=ascend\" ${debug_cmd}"
        ansible-playbook -i ./inventory_file playbooks/uninstall/uninstall_${target}.yml -e "hosts_name=ascend" ${debug_cmd}
    done
    unset IFS
}

function process_upgrade()
{
    IFS=','
    not_supported=${FALSE}
    for target in ${upgrade_target}
    do
        if [ ! -f playbooks/upgrade/upgrade_${target}.yml ]; then
            echo "Error: not supported upgrade for ${target}"
            not_supported=${TRUE}
        fi
    done
    if [ "${not_supported}" == "${TRUE}" ]; then
        exit 1
    fi
    ping_all
    process_check
    if [ "x${nocopy_flag}" != "xy" ];then
        echo "ansible-playbook -i ./inventory_file playbooks/distribution.yml -e hosts_name=ascend"
        ansible-playbook -i ./inventory_file playbooks/distribution.yml -e "hosts_name=ascend"
    fi
    debug_cmd=""
    if [ "x${debug_flag}" == "xy" ]; then
        debug_cmd="-v"
    fi
    for target in ${upgrade_target}
    do
        echo "ansible-playbook -i ./inventory_file playbooks/upgrade/upgrade_${target}.yml -e \"hosts_name=ascend\" ${debug_cmd}"
        ansible-playbook -i ./inventory_file playbooks/upgrade/upgrade_${target}.yml -e "hosts_name=ascend" ${debug_cmd}
    done
    unset IFS
}

function process_test()
{
    IFS=','
    unsupport=${FALSE}
    for target in ${test_target}
    do
        if [ ! -f test/test_${target}.yml ];then
            echo "Error: not support test for ${target}"
            unsupport=${TRUE}
        fi
    done
    if [ ${unsupport} == ${TRUE} ];then
        exit 1
    fi
    debug_cmd=""
    if [ "x${debug_flag}" == "xy" ];then
        debug_cmd="-v"
    fi
    for target in ${test_target}
    do
        echo "ansible-playbook -i ./inventory_file test/test_${target}.yml -e hosts_name=ascend ${debug_cmd}"
        ansible-playbook -i ./inventory_file test/test_${target}.yml -e "hosts_name=ascend" ${debug_cmd}
    done
    unset IFS
}

function process_scene()
{
    ping_all
    process_check
    echo "ansible-playbook -i ./inventory_file playbooks/distribution.yml -e hosts_name=ascend"
    if [ "x${nocopy_flag}" != "xy" ];then
        ansible-playbook -i ./inventory_file playbooks/distribution.yml -e "hosts_name=ascend"
    fi
    debug_cmd=""
    if [ "x${debug_flag}" == "xy" ];then
        debug_cmd="-v"
    fi
    echo "ansible-playbook -i ./inventory_file scene/scene_${install_scene}.yml -e hosts_name=ascend ${debug_cmd}"
    ansible-playbook -i ./inventory_file scene/scene_${install_scene}.yml -e "hosts_name=ascend" ${debug_cmd}
}

function print_usage()
{
    echo "Usage: ./install.sh [options]"
    echo " Options:"
    echo "--help  -h                     Print this message"
    echo "--check                        check environment"
    echo "--clean                        clean resources"
    echo "--nocopy                       do not copy resources"
    echo "--debug                        enable debug"
    echo "--install=<package_name>       Install specific package:"
    for target in `find playbooks/install/install_*.yml`
    do
        tmp=${target#*_}
        echo "                               ${tmp%.*}"
    done
    echo "The \"npu\" will install driver and firmware together"
    echo "--install-scene=<scene_name>   Install specific scene:"
    for scene in `find scene/scene_*.yml`
    do
        tmp=${scene#*_}
        echo "                               ${tmp%.*}"
    done
    echo "--uninstall=<package_name>     Install specific package:"
    for target in `find playbooks/uninstall/uninstall_*.yml`
    do
        tmp=${target#*_}
        echo "                               ${tmp%.*}"
    done
    echo "The \"npu\" will uninstall driver and firmware together"
    echo "--upgrade=<package_name>       Install specific package:"
    for target in `find playbooks/upgrade/upgrade_*.yml`
    do
        tmp=${target#*_}
        echo "                               ${tmp%.*}"
    done
    echo "The \"npu\" will upgrade driver and firmware together"
    echo "--test=<target>                test the functions:"
    for test in `find test/test_*.yml`
    do
        tmp=${test#*_}
        echo "                               ${tmp%.*}"
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
            shift 1
            ;;
        --version)
            echo "this is version"
            exit 0
            ;;
        --install=*)
            install_target=$(echo $1 | cut -d"=" -f2 | sed "s/\/*$//g")
            shift
            ;;
        --install-scene=*)
            install_scene=$(echo $1 | cut -d"=" -f2 | sed "s/\/*$//g")
            shift
            ;;
        --uninstall=*)
            uninstall_target=$(echo $1 | cut -d"=" -f2 | sed "s/\/*$//g")
            shift
            ;;
        --upgrade=*)
            upgrade_target=$(echo $1 | cut -d"=" -f2 | sed "s/\/*$//g")
            shift
            ;;
        --test=*)
            test_target=$(echo $1 | cut -d"=" -f2 | sed "s/\/*$//g")
            shift
            ;;
        --nocopy)
            nocopy_flag=y
            shift
            ;;
        --debug)
            debug_flag=y
            shift
            ;;
        --check)
            check_flag=y
            shift
            ;;
        --clean)
            clean_flag=y
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
    if [ "x${install_target}" != "x" ] && [ "x${install_scene}" != "x" ];then
        echo "ERROR" "Unsupported --install and --install-scene at same time"
        exit 1
    fi
}

function ping_all()
{
    ansible -i inventory_file -m ping all
    if [ $? -ne 0 ]; then
        echo "ERROR" "some hosts is unreachable"
        exit 1
    fi
}

function process_check()
{
    ansible -i ./inventory_file all -m shell -a "rm -f /etc/ansible/facts.d/npu_info.fact"
    echo "ansible-playbook -i ./inventory_file playbooks/gather_npu_fact.yml -e hosts_name=ascend"
    ansible-playbook -i ./inventory_file playbooks/gather_npu_fact.yml -e "hosts_name=ascend"
}

function process_chean()
{
    ansible -i ./inventory_file all -m shell -a "rm -rf ~/resources.tar ~/resources"
}

function bootstrap()
{
    have_ansible=`command -v ansible | wc -l`
    have_rpm=`command -v rpm | wc -l`
    check_python375
    py37_status=$?
    if [ ${py37_status} == ${FALSE} ];then
        install_sys_packages
        install_python375
    fi

    if [ ${have_ansible} -eq 0 ];then
        echo "no ansible"
        install_ansible
    fi
}

main()
{
    parse_script_args $*
    check_script_args
    if [ -d ./facts_cache ];then
        rm -rf ./facts_cache
    fi
    export PATH=/usr/local/python3.7.5/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH
    unset DISPLAY
    bootstrap

    if [ "x${install_target}" != "x" ];then
        process_install ${install_target}
    fi
    if [ "x${install_scene}" != "x" ];then
        process_scene ${install_scene}
    fi
    if [ "x${test_target}" != "x" ];then
        process_test ${test_target}
    fi
    if [ "x${check_flag}" == "xy" ]; then
        process_check
    fi
    if [ "x${clean_flag}" == "xy" ]; then
        process_chean
    fi
    if [ "x${uninstall_target}" != "x" ];then
        process_uninstall ${uninstall_target}
    fi
    if [ "x${upgrade_target}" != "x" ];then
        process_upgrade ${upgrade_target}
    fi
}

main $*
