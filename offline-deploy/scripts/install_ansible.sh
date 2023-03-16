#!/bin/bash
set -e

readonly arch=$(uname -m)

function get_os_name()
{
    local os_name=$(grep -oP "^ID=\"?\K\w+" /etc/os-release)
    echo ${os_name}
}

function get_os_version()
{
    local os_version=$(grep -oP "^VERSION_ID=\"?\K\w+\.?\w*" /etc/os-release)
    echo ${os_version}
}

function install_ansible()
{
    echo -e "[INFO]\t$(date +"%Y-%m-%d %H:%M:%S")\t start install ansible..."
    local is_ansible_installed=$(checkAnsible)
    if [[ ${is_ansible_installed} != 0 ]];then
        RESOURCE_DIR=/root/resources
        if [ ! -d $RESOURCE_DIR ];then
            echo -e "[ERROR]\t$(date +"%Y-%m-%d %H:%M:%S")\t error: no resource dir $RESOURCE_DIR"
            exit 1
        fi

        case ${os_name} in
        ubuntu)
            dpkg -i --force-all /root/resources/ansible/Ubuntu_${os_version}/${arch}/*.deb 1>/dev/null
            ;;
        openEuler)
            rpm -i --nodeps --force /root/resources/ansible/OpenEuler_${os_version}_LTS/${arch}/*.rpm 1>/dev/null
            ;;
        centos)
            rpm -i --nodeps --force /root/resources/ansible/CentOS_7.6/${arch}/*.rpm 1>/dev/null
            ;;    
        esac
        echo -e "\n[INFO]\t$(date +"%Y-%m-%d %H:%M:%S")\t successfully installed ansible\n"
    else
        echo -e "[INFO]\t$(date +"%Y-%m-%d %H:%M:%S")\t ansible is already installed\n"
    fi
    sed -i "s?#gathering = implicit?gathering = smart?" /etc/ansible/ansible.cfg
    sed -i "s?#fact_caching = memory?fact_caching = jsonfile?" /etc/ansible/ansible.cfg
    sed -i "s?#fact_caching_connection=/tmp?fact_caching_connection=/etc/ansible/facts-cache?" /etc/ansible/ansible.cfg
    sed -i "s?#host_key_checking = False?host_key_checking = False?" /etc/ansible/ansible.cfg

    ansible --version >/dev/null 2>&1
}

function checkAnsible() {
    ansible --version >/dev/null 2>&1
    echo $?
}

function main()
{
    local os_name=$(get_os_name)
    local os_version=$(get_os_version)
    install_ansible
}

main

