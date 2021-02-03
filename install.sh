#!/bin/bash
readonly TRUE=1
readonly FALSE=0
readonly kernel_version=$(uname -r)
readonly arch=$(uname -m)
readonly BASE_DIR=$(cd "$(dirname $0)" > /dev/null 2>&1; pwd -P)
readonly PYLIB_PATH=${BASE_DIR}/resources/pylibs

unset DISPLAY
if [ -z ${ASNIBLE_CONFIG} ];then
    export ANSIBLE_CONFIG=$BASE_DIR/ansible.cfg
fi
if [ -z ${ASNIBLE_LOG_PATH} ];then
    export ANSIBLE_LOG_PATH=$BASE_DIR/install.log
fi
if [ -z ${ASNIBLE_INVENTORY} ];then
    export ANSIBLE_INVENTORY=$BASE_DIR/inventory_file
fi
if [ -z ${ANSIBLE_CACHE_PLUGIN_CONNECTION} ];then
    export ANSIBLE_CACHE_PLUGIN_CONNECTION=$BASE_DIR/facts_cache
fi

VAULT_CMD=""
DEBUG_CMD=""
STDOUT_CALLBACK=""

if [ ${UID} == 0 ];then
    readonly PYTHON_PREFIX=/usr/local/python3.7.5
else
    readonly PYTHON_PREFIX=${HOME}/.local/python3.7.5
fi
readonly app_name_list=(all npu driver firmware nnrt nnae tfplugin toolbox toolkit)

function ansible_playbook()
{
    if [ -z "$output_file" ]; then
        ansible-playbook $*
    else
        ansible-playbook $* > "$output_file"
    fi
}

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

function encrypt_inventory() {
    pass1=$(grep ansible_ssh_pass ${BASE_DIR}/inventory_file | wc -l)
    pass2=$(grep ansible_sudo_pass ${BASE_DIR}/inventory_file | wc -l)
    pass_cnt=$((pass1 + pass2))
    if [ ${pass_cnt} == 0 ];then
        return
    fi
    echo "The inventory_file need encrypt !"
    ansible-vault encrypt ${BASE_DIR}/inventory_file
}

function init_ansible_vault()
{
    local vault_count=$(grep "ANSIBLE_VAULT.*AES" ${BASE_DIR}/inventory_file | wc -l)
    if [ ${vault_count} != 0 ] && [ -z ${ANSIBLE_VAULT_PASSWORD_FILE} ];then
         VAULT_CMD="--ask-vault-pass"
    fi
}

function have_no_python_module
{
    ret=`python3.7 -c "import ${1}" 2>&1 | grep "No module" | wc -l`
    return ${ret}
}

function check_python375()
{
    if [ ! -d ${PYTHON_PREFIX} ];then
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
    local kh_rpm=$(find ${BASE_DIR}/resources/kernel/ -name "kernel-headers*" | sort -r | grep -m1 ${euler})
    local kd_rpm=$(find ${BASE_DIR}/resources/kernel/ -name "kernel-devel*" | sort -r | grep -m1 ${euler})
    if [ ${kh} -eq 0 ] && [ -f "${kh_rpm}" ];then
        sudo rpm -ivh --force --nodeps --replacepkgs ${kh_rpm}
    fi
    if [ ${kd} -eq 0 ] && [ -f "${kd_rpm}" ];then
        sudo rpm -ivh --force --nodeps --replacepkgs ${kd_rpm}
    fi
}

function install_kernel_header_devel()
{
    local have_rpm=$(command -v rpm | wc -l)
    if [ ${have_rpm} -eq 0 ]; then
        return
    fi
    local kh_rpm=${BASE_DIR}/resources/kernel/kernel-headers-${kernel_version}.rpm
    local kd_rpm=${BASE_DIR}/resources/kernel/kernel-devel-${kernel_version}.rpm
    local kh=$(rpm -q kernel-headers | grep ${kernel_version} | wc -l)
    local kd=$(rpm -q kernel-devel | grep ${kernel_version} | wc -l)
    if [ ${kh} -eq 0 ] && [ -f ${kh_rpm} ];then
        sudo rpm -ivh --force --nodeps --replacepkgs ${kh_rpm}
    fi
    if [ ${kd} -eq 0 ] && [ -f ${kd_rpm} ];then
        sudo rpm -ivh --force --nodeps --replacepkgs ${kd_rpm}
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
        sudo rpm -ivh --force --nodeps --replacepkgs ${BASE_DIR}/resources/${os_ver}_${arch}/*.rpm
    elif [ ${have_dnf} -eq 1 ]; then
        sudo rpm -ivh --force --nodeps --replacepkgs ${BASE_DIR}/resources/${os_ver}_${arch}/*.rpm
    elif [ ${have_dpkg} -eq 1 ]; then
        sudo export DEBIAN_FRONTEND=noninteractive && export DEBIAN_PRIORITY=critical; dpkg --force-all -i ${BASE_DIR}/resources/${os_ver}_${arch}/*.deb
    fi
}

function install_python375()
{
    if [ ! -f ${BASE_DIR}/resources/Python-3.7.5.tar.xz ];then
        echo "can't find Python-3.7.5.tar.xz"
        return
    fi
    echo "installing Python 3.7.5"
    mkdir -p ~/build
    tar -xvf ${BASE_DIR}/resources/Python-3.7.5.tar.xz -C ~/build
    cd ~/build/Python-3.7.5
    ./configure --enable-shared --prefix=${PYTHON_PREFIX}
    make -j4
    make install
    cd -
    python3.7 -m ensurepip
    python3.7 -m pip install --upgrade pip --no-index --find-links ${PYLIB_PATH}
    # install wheel, if not pip will use legacy setup.py install for installation
    python3.7 -m pip install wheel --no-index --find-links ${PYLIB_PATH}
    if [ "${g_os_name}" == "EulerOS" ];then
        python3.7 -m pip install selinux --no-index --find-links ${PYLIB_PATH}
    fi
    if [ ${UID} == 0 ];then
        echo "export PATH=/usr/local/python3.7.5/bin:\$PATH" > /usr/local/ascendrc 2>/dev/null
        echo "export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:\$LD_LIBRARY_PATH" >> /usr/local/ascendrc 2>/dev/null
    else
        echo "export PATH=/usr/local/python3.7.5/bin:\$PATH" > ${HOME}/.local/ascendrc 2>/dev/null
        echo "export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:\$LD_LIBRARY_PATH" >> ${HOME}/.local/ascendrc 2>/dev/null
    fi
}

function install_ansible()
{
    local ansible_path=${PYTHON_PREFIX}/lib/python3.7/site-packages/ansible
    python3.7 -m pip install ansible --no-index --find-links ${PYLIB_PATH}
    # patch the INTERPRETER_PYTHON_DISTRO_MAP, make it support EulerOS
    if [ -f ${ansible_path}/config/base.yml ];then
        eulercnt=$(grep euleros ${ansible_path}/config/base.yml | wc -l)
        if [ ${eulercnt} == 0 ];then
            # euler os 2 is recoginized as centos 2
            sed -i "1515 i\      '2': /usr/bin/python3"     ${ansible_path}/config/base.yml
            # ubuntu 18.04 is recoginized as debian buster/sid due tu /etc/debian_release
            sed -i "1520 i\      'buster/sid': /usr/bin/python3" ${ansible_path}/config/base.yml
            # euler os use python3 as default python interpreter
            sed -i "1527 i\    euleros:"                    ${ansible_path}/config/base.yml
            sed -i "1528 i\      '2': /usr/bin/python3"     ${ansible_path}/config/base.yml
            # kylin should use python3. if selinux enalbed, the default python have no selinux
            sed -i "1529 i\    kylin:"                      ${ansible_path}/config/base.yml
            sed -i "1530 i\      '10': /usr/bin/python3"    ${ansible_path}/config/base.yml
        fi
    fi
}

function process_display()
{
    IFS=' '
    unsupported=${TRUE}
    for target in ${app_name_list[*]}
    do
        if [ "${target}" == "${display_target}" ];then
            unsupported=${FALSE}
            break
        fi
    done
    if [ ${unsupported} == ${TRUE} ];then
        echo "Error: not support display for ${display_target}"
        exit 1
    fi
    unset IFS
    ansible ${VAULT_CMD} -i ${BASE_DIR}/inventory_file all -m shell -a "rm -f /etc/ansible/facts.d/app_info.fact"
    echo "ansible-playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${BASE_DIR}/playbooks/gather_app_info.yml -e hosts_name=ascend app_name=${display_target}"
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${BASE_DIR}/playbooks/gather_app_info.yml -e "hosts_name=ascend" -e "app_name=${display_target}"

}

function process_install()
{
    IFS=','
    local unsupport=${FALSE}
    for target in ${install_target}
    do
        if [ ! -f ${BASE_DIR}/playbooks/install/install_${target}.yml ];then
            echo "Error: not support install for ${target}"
            unsupport=${TRUE}
        fi
    done
    if [ ${unsupport} == ${TRUE} ];then
        exit 1
    fi
    local tmp_install_play=${BASE_DIR}/playbooks/tmp_install.yml
    echo "- import_playbook: gather_npu_fact.yml" > ${tmp_install_play}
    if [ "x${nocopy_flag}" != "xy" ];then
        echo "- import_playbook: distribution.yml" >> ${tmp_install_play}
    fi
    for target in ${install_target}
    do
        echo "- import_playbook: install/install_${target}.yml" >> ${tmp_install_play}
    done
    unset IFS
    echo "ansible-playbook ${VAULT_CMD} -i ./inventory_file ${tmp_install_play} -e hosts_name=ascend ${DEBUG_CMD}"
    cat ${tmp_install_play}
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${tmp_install_play} -e "hosts_name=ascend" ${DEBUG_CMD}
    if [ -f ${tmp_install_play} ];then
        rm -f ${tmp_install_play}
    fi
}

function process_uninstall()
{
    IFS=','
    not_supported=${FALSE}
    for target in ${uninstall_target}
    do
        if [ ! -f ${BASE_DIR}/playbooks/uninstall/uninstall_${target}.yml ]; then
            echo "Error: not supported uninstall for ${target}"
            not_supported=${TRUE}
        fi
    done
    if [ "${not_supported}" == "${TRUE}" ]; then
        exit 1
    fi

    local tmp_uninstall_play=${BASE_DIR}/playbooks/.tmp_uninstall.yml
    echo "- import_playbook: gather_npu_fact.yml" > ${tmp_install_play}
    for target in ${uninstall_target}
    do
        echo "- import_playbook: uninstall/uninstall_${target}.yml" >> ${tmp_uninstall_play}
    done
    unset IFS
    echo "ansible-playbook ${VAULT_CMD} -i ./inventory_file ${tmp_uninstall_play} -e hosts_name=ascend ${DEBUG_CMD}"
    cat ${tmp_uninstall_play}
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${tmp_uninstall_play} -e "hosts_name=ascend" ${DEBUG_CMD}
    if [ -f ${tmp_uninstall_play} ];then
        rm -f ${tmp_uninstall_play}
    fi
}

function process_upgrade()
{
    IFS=','
    local not_supported=${FALSE}
    for target in ${upgrade_target}
    do
        if [ ! -f ${BASE_DIR}/playbooks/upgrade/upgrade_${target}.yml ]; then
            echo "Error: not supported upgrade for ${target}"
            not_supported=${TRUE}
        fi
    done
    if [ "${not_supported}" == "${TRUE}" ]; then
        exit 1
    fi

    local tmp_upgrade_play=${BASE_DIR}/playbooks/tmp_upgrade.yml
    echo "- import_playbook: gather_npu_fact.yml" > ${tmp_upgrade_play}
    if [ "x${nocopy_flag}" != "xy" ];then
        echo "- import_playbook: distribution.yml" >> ${tmp_upgrade_play}
    fi
    for target in ${upgrade_target}
    do
        echo "- import_playbook: upgrade/upgrade_${target}.yml" >> ${tmp_upgrade_play}
    done
    unset IFS
    echo "ansible-playbook ${VAULT_CMD} -i ./inventory_file ${tmp_upgrade_play} -e hosts_name=ascend ${DEBUG_CMD}"
    cat ${tmp_upgrade_play}
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${tmp_upgrade_play} -e "hosts_name=ascend" ${DEBUG_CMD}
    if [ -f ${tmp_upgrade_play} ];then
        rm -f ${tmp_upgrade_play}
    fi
}

function process_test()
{
    IFS=','
    local unsupport=${FALSE}
    for target in ${test_target}
    do
        if [ ! -f ${BASE_DIR}/test/test_${target}.yml ];then
            echo "Error: not support test for ${target}"
            unsupport=${TRUE}
        fi
    done
    if [ ${unsupport} == ${TRUE} ];then
        exit 1
    fi

    local tmp_test_play=${BASE_DIR}/test/tmp_test.yml
    touch ${tmp_test_play}
    for target in ${test_target}
    do
        echo "- import_playbook: test_${target}.yml" >> ${tmp_test_play}
    done
    unset IFS
    echo "ansible-playbook ${VAULT_CMD} -i ./inventory_file ${tmp_test_play} -e hosts_name=ascend ${DEBUG_CMD}"
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${tmp_test_play} -e "hosts_name=ascend" ${DEBUG_CMD}
    if [ -f ${tmp_test_play} ];then
        rm -f ${tmp_test_play}
    fi
}

function process_scene()
{
    local tmp_scene_play=${BASE_DIR}/scene/tmp_scene.yml
    echo "- import_playbook: ../playbooks/gather_npu_fact.yml" > ${tmp_scene_play}
    if [ "x${nocopy_flag}" != "xy" ];then
        echo "- import_playbook: ../playbooks/distribution.yml" >> ${tmp_scene_play}
    fi
    echo "- import_playbook: scene_${install_scene}.yml" >> ${tmp_scene_play}
    echo "ansible-playbook ${VAULT_CMD} -i ./inventory_file ${tmp_scene_play} -e hosts_name=ascend ${DEBUG_CMD}"
    cat ${tmp_scene_play}
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${tmp_scene_play} -e "hosts_name=ascend" ${DEBUG_CMD}
    if [ -f ${tmp_scene_play} ];then
        rm -f ${tmp_scene_play}
    fi
}

function print_usage()
{
    echo "Usage: ./install.sh [options]"
    echo " Options:"
    echo "--help  -h                     Print this message"
    echo "--check                        check environment"
    echo "--clean                        clean resources on remote servers"
    echo "--nocopy                       do not copy resources to remote servers when install for remote"
    echo "--debug                        enable debug"
    echo "--output-file=<output_file>    Redirect the output of ansible execution results to a file"
    echo "--stdout_callback=<callback_name> set stdout_callback for ansible"
    echo "                               avaiable callback could be listed by: ansible-doc -t callback -l"
    echo "--install=<package_name>       Install specific package:"
    for target in `find ${BASE_DIR}/playbooks/install/install_*.yml`
    do
        target=$(basename ${target})
        tmp=${target#*_}
        echo "                               ${tmp%.*}"
    done
    echo "The \"npu\" will install driver and firmware together"
    echo "--install-scene=<scene_name>   Install specific scene:"
    for scene in `find ${BASE_DIR}/scene/scene_*.yml`
    do
        scene=$(basename ${scene})
        tmp=${scene#*_}
        echo "                               ${tmp%.*}"
    done
    echo "--uninstall=<package_name>     Uninstall specific package:"
    for target in `find ${BASE_DIR}/playbooks/uninstall/uninstall_*.yml`
    do
        target=$(basename ${target})
        tmp=${target#*_}
        echo "                               ${tmp%.*}"
    done
    echo "The \"npu\" will uninstall driver and firmware together"
    echo "--uninstall-version=<version>  Uninstall specific version package"
    echo "                               using with --uninstall=<package_name> together"
    echo "                               support single package_name except auto,npu"
    echo "--upgrade=<package_name>       Upgrade specific package:"
    for target in `find ${BASE_DIR}/playbooks/upgrade/upgrade_*.yml`
    do
        target=$(basename ${target})
        tmp=${target#*_}
        echo "                               ${tmp%.*}"
    done
    echo "The \"npu\" will upgrade driver and firmware together"
    echo "--test=<target>                test the functions:"
    for test in `find ${BASE_DIR}/test/test_*.yml`
    do
        test=$(basename ${test})
        tmp=${test#*_}
        echo "                               ${tmp%.*}"
    done
    echo "--display=<target>             display app install info:"
    for target in ${app_name_list[*]}
    do
        tmp=${target#*_}
        echo "                               ${tmp%.*}"
    done
    echo "The \"npu\" will upgrade driver and firmware together"
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
        --display=*)
            display_target=$(echo $1 | cut -d"=" -f2 | sed "s/\/*$//g")
            shift
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
        --uninstall-version=*)
            uninstall_version=$(echo $1 | cut -d"=" -f2 | sed "s/\/*$//g")
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
        --output-file=*)
            output_file=$(echo $1 | cut -d"=" -f2 | sed "s/\/*$//g")
            shift
            ;;
        --stdout_callback=*)
            STDOUT_CALLBACK=$(echo $1 | cut -d"=" -f2 | sed "s/\/*$//g")
            shift
            ;;
        --nocopy)
            nocopy_flag=y
            shift
            ;;
        --debug)
            DEBUG_CMD="-v"
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
    ansible -i ${BASE_DIR}/inventory_file -m ping all
    if [ $? -ne 0 ]; then
        echo "ERROR" "some hosts is unreachable"
        exit 1
    fi
}

function process_check()
{
    echo "ansible-playbook ${VAULT_CMD} -i ./inventory_file playbooks/gather_npu_fact.yml -e hosts_name=ascend"
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${BASE_DIR}/playbooks/gather_npu_fact.yml -e "hosts_name=ascend"
}

function process_chean()
{
    ansible ${VAULT_CMD} -i ${BASE_DIR}/inventory_file all -m shell -a "rm -rf ~/resources.tar ~/resources"
}

function bootstrap()
{
    local have_ansible=`command -v ansible | wc -l`
    local have_rpm=`command -v rpm | wc -l`
    check_python375
    local py37_status=$?
    if [ ${py37_status} == ${FALSE} ];then
        install_sys_packages
        install_python375
    fi

    if [ ${have_ansible} -eq 0 ];then
        echo "no ansible"
        install_ansible
    fi
}

function set_permission()
{
    for f in $(find ${BASE_DIR}/  -type f  -name "*.sh" -o -name "*.py" ! -path "./.git*")
    do
        is_exe=$(file ${f} | grep executable | wc -l)
        if [[ ${is_exe} -eq 1 ]];then
            chmod 550 ${f} 2>/dev/null
        fi
    done
    chmod 600 ${BASE_DIR}/inventory_file
}

function prepare_environment()
{
    if [ -z ${ANSIBLE_STDOUT_CALLBACK} ] && [ ! -z ${STDOUT_CALLBACK} ];then
        export ANSIBLE_STDOUT_CALLBACK=${STDOUT_CALLBACK}
    fi
}

main()
{
    set_permission
    parse_script_args $*
    check_script_args
    if [ -d ${BASE_DIR}/facts_cache ];then
        rm -rf ${BASE_DIR}/facts_cache
    fi
    if [ ${UID} == 0 ];then
        export PATH=/usr/local/python3.7.5/bin:$PATH
        export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH
    else
        export PATH=${HOME}/.local/python3.7.5/bin:$PATH
        export LD_LIBRARY_PATH=${HOME}/.local/python3.7.5/lib:$LD_LIBRARY_PATH
    fi
    bootstrap
    encrypt_inventory
    init_ansible_vault
    prepare_environment

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
        process_uninstall ${uninstall_target} ${uninstall_version}
    fi
    if [ "x${upgrade_target}" != "x" ];then
        process_upgrade ${upgrade_target}
    fi
    if [ "x${display_target}" != "x" ]; then
        process_display
    fi
}

main $*
