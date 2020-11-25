#!/bin/bash

function install_sys_packages()
{
    echo "install sys dependencies"
    have_rpm=`command -v rpm | wc -l`
    have_dnf=`command -v dnf | wc -l`
    have_dpkg=`command -v dpkg | wc -l`

    os_ver=""
    if [ ${have_dpkg} -eq 1 ]; then
        os_ver="Ubuntu_18.04"
    elif [ ${have_dnf} -eq 1 ]; then
        os_ver="CentOS_8.2"
    elif [ ${have_rpm} -eq 1 ]; then
        os_ver="CentOS_7.6"
    fi

    if [ ${have_rpm} -eq 1 ]; then
        rpm -ivh --force --replacepkgs ~/resources/${os_ver}_`uname -m`/*.rpm
    elif [ ${have_dnf} -eq 1 ]; then
        dnf install ~/resources/${os_ver}_`uname -m`/*.rpm
    elif [ ${have_dpkg} -eq 1 ]; then
        export DEBIAN_FRONTEND=noninteractive && export DEBIAN_PRIORITY=critical; dpkg -i ~/resources/${os_ver}_`uname -m`/*.deb
    fi
}

function install_python375()
{
    if [ ! -f ./resources/Python-3.7.5.tar.xz ];then
        echo "can't find Python-3.7.5.tar.xz"
        return
    fi
    echo "installing Python 3.7.5"
    pyinstall_path="/usr/local/python3.7.5"
    if [ -d ${pyinstall_path} ];then
        echo "python 3.7.5 already installed"
        return
    fi
    tar -xvf ./resources/Python-3.7.5.tar.xz -C ~/
    cd ~/Python-3.7.5
    ./configure --enable-shared --prefix=/usr/local/python3.7.5
    make -j4
    make install
    cd -
    python3.7 -m ensurepip
    python3.7 -m pip install --upgrade pip --no-index --find-links ./resources/`uname -m`
}

function install_ansible()
{
    python3.7 -m pip install ansible --no-index --find-links ./resources/`uname -m`
}

function install_target()
{
    ping_all
    echo "ansible-playbook -i ./inventory_file playbooks/gather_npu_fact.yml -e hosts_name=ascend"
    ansible-playbook -i ./inventory_file playbooks/gather_npu_fact.yml -e "hosts_name=ascend"
    echo "ansible-playbook -i ./inventory_file playbooks/distribution.yml -e hosts_name=ascend"
    if [ "x${nocopy_flag}" != "xy" ];then
        ansible-playbook -i ./inventory_file playbooks/distribution.yml -e "hosts_name=ascend"
    fi
    debug_cmd=""
    if [ "x${debug_flag}" == "xy" ];then
        debug_cmd="-v"
    fi
    echo "ansible-playbook -i ./inventory_file playbooks/install_${install_target}.yml -e hosts_name=ascend ${debug_cmd}"
    ansible-playbook -i ./inventory_file playbooks/install_${install_target}.yml -e "hosts_name=ascend" ${debug_cmd}
}

function install_scene()
{
    ping_all
    echo "ansible-playbook -i ./inventory_file playbooks/gather_npu_fact.yml -e hosts_name=ascend"
    ansible-playbook -i ./inventory_file playbooks/gather_npu_fact.yml -e "hosts_name=ascend"
    echo "ansible-playbook -i ./inventory_file playbooks/distribution.yml -e hosts_name=ascend"
    if [ "x${nocopy_flag}" != "xy" ];then
        ansible-playbook -i ./inventory_file playbooks/distribution.yml -e "hosts_name=ascend"
    fi
    debug_cmd=""
    if [ "x${debug_flag}" == "xy" ];then
        debug_cmd="-v"
    fi
    echo "ansible-playbook -i ./inventory_file scene/scene_${install_scene}.yml -e hosts_name=ascendi ${debug_cmd}"
    ansible-playbook -i ./inventory_file scene/scene_${install_scene}.yml -e "hosts_name=ascend" ${debug_cmd}
}

function print_usage()
{
    echo "Usage: ./install.sh [options]"
    echo " Options:"
    echo "--help  -h                     Print this message"
    echo "--check                        check evironment"
    echo "--clean                        clean resouces"
    echo "--nocopy                       do not copy resouces"
    echo "--debug                        enable debug"
    echo "--install=<package_name>       Install specific package:"
    echo "                               npu        install dirver and firmware toghter"
    echo "                               driver"
    echo "                               firmware"
    echo "                               nnrt"
    echo "                               nnae"
    echo "                               toolbox"
    echo "                               toolkit"
    echo "                               tfplugin"
    echo "                               torch"
    echo "                               tensorflow"
    echo "                               sys_pkg    install system dependencies"
    echo "                               gcc        install gcc 7.3.0"
    echo "                               python375  install python 3.7.5"
    echo "--install-scene=<username>     Install specific scene: auto, infer_dev, infer_run"
    echo "                               train_dev, train_run, vmhost"
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
        --chean)
            chean_flag=y
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

function check()
{
    ansible-playbook -i ./inventory_file playbooks/gather_npu_fact.yml -e "hosts_name=ascend"
}

function chean_resouces()
{
    ansible -i ./inventory_file all -m shell -a "rm -rf ~/resources.tar ~/resources"
}

main()
{
    if [ -d ./facts_cache ];then
        rm -rf ./facts_cache
    fi
    export PATH=/usr/local/python3.7.5/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH
    have_ansible=`command -v ansible | wc -l`
    have_rpm=`command -v rpm | wc -l`
    have_gcc=`command -v gcc | wc -l`
    if [ ! -d /usr/local/python3.7.5 ];then
        if [ ${have_gcc} -eq 0 ];then
            install_sys_packages
        fi
        install_python375
    fi

    if [ ${have_ansible} -eq 0 ];then
        install_ansible
    fi

    parse_script_args $*
    check_script_args

    if [ "x${install_target}" != "x" ];then
        install_target ${install_target}
    fi

    if [ "x${install_scene}" != "x" ];then
        install_scene ${install_scene}
    fi

    if [ "x${check_flag}" == "xy" ]; then
        check
    fi
    if [ "x${chean}" == "xy" ]; then
        chean_resouces
    fi
}

main $*
