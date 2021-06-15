#!/bin/bash
readonly TRUE=1
readonly FALSE=0
readonly SIZE_THRESHOLD=$((5*1024*1024*1024))
readonly LOG_SIZE_THRESHOLD=$((20*1024*1024))
readonly LOG_COUNT_THRESHOLD=5
readonly kernel_version=$(uname -r)
readonly arch=$(uname -m)
readonly BASE_DIR=$(cd "$(dirname $0)" > /dev/null 2>&1; pwd -P)
readonly PYLIB_PATH=${BASE_DIR}/resources/pylibs
readonly A300I_PRODUCT_LIST="A300i-pro"
readonly INFER_PRODUCT_LIST="A300-3000,A300-3010"
readonly TRAIN_PRODUCT_LIST="A300t-9000,A800-9000,A800-9010,A900-9000"
readonly CANN_PRODUCT_LIST="Ascend-cann,MindX"

declare -A OS_MAP=(["ubuntu"]="Ubuntu")
OS_MAP["ubuntu"]="Ubuntu"
OS_MAP["centos"]="CentOS"
OS_MAP["euleros"]="EulerOS"
OS_MAP["debian"]="Debian"
OS_MAP["sles"]="SLES"
OS_MAP["kylin"]="Kylin"
OS_MAP["bclinux"]="BCLinux"
OS_MAP["Linx"]="Linx"
OS_MAP["UOS"]="UOS"
OS_MAP["uos"]="UOS"
OS_MAP["tlinux"]="Tlinux"
OS_MAP["openEuler"]="OpenEuler"

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
readonly app_name_list=(all npu driver firmware nnrt nnae tfplugin toolbox toolkit atlasedge ha)

function log_info()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    echo "${DATE_N} ${USER_N} [INFO] $*" >> ${BASE_DIR}/install.log
}

function ansible_playbook()
{
    if [ -z "$output_file" ]; then
        ansible-playbook $*
    else
        ansible-playbook $* > "$output_file"
    fi
}

function get_os_version()
{
    local id=${1}
    local ver=${2}
    local codename=${3}
    local version=${ver}

    # Ubuntu, bclinux, SLES no need specific handle

    # CentOS
    if [ "${id}" == "CentOS" ];then
        if [ "${ver}" == "7" ];then
            version="7.6"
        fi
        if [ "${ver}" == "8" ];then
            version="8.2"
        fi
    fi

    # EulerOS
    if [ "${id}" == "EulerOS" ];then
        if [ "${ver}" == "2.0" ] && [ "${codename}" == "SP8" ];then
            version="2.8"
        elif [ "${ver}" == "2.0" ] && [[ "${codename}" =~ SP9 ]];then
            version="2.9"
        fi
    fi

    # Debian
    if [ "${id}" == "Debian" ];then
        if [ "${ver}" == "9" ];then
            version="9.9"
        elif [ "${ver}" == "10" ];then
            version="10.0"
        fi
    fi

    # Kylin
    if [ "${id}" == "Kylin" ];then
        version=${ver}${codename}
    fi

    # Linx 6 is almost same with debian 9
    if [ "${id}" == "Linx" ];then
        if [ "${ver}" == "9" ];then
            version="6"
        fi
    fi

    # OpenEuler
    if [ "${id}" == "OpenEuler" ];then
        version=${ver}${codename}
    fi

    echo ${version}
    return 0
}

function get_os_name()
{
    local os_id=$(grep -oP "^ID=\"?\K\w+" /etc/os-release)
    local os_name=${OS_MAP[$os_id]}
    echo ${os_name}
}

readonly g_os_name=$(get_os_name)

function get_os_ver_arch()
{
    local os_ver=$(grep -oP "^VERSION_ID=\"?\K\w+\.?\w*" /etc/os-release)
    local codename=$(grep -oP "^VERSION=(.*?)\(\K[\w\.\ -]+" /etc/os-release | awk -F_ '{print $1}')
    local os_name=$(get_os_name)
    local version=$(get_os_version ${os_name} ${os_ver} ${codename})
    local os_ver_arch=${g_os_name}_${version}_${arch}
    echo ${os_ver_arch}
    return
}

readonly g_os_ver_arch=$(get_os_ver_arch)

# check if resource of specific os is exists
function check_resources()
{
    if [ -d ${BASE_DIR}/resources/${g_os_ver_arch} ];then
        return
    fi
    echo "WARNING: no resources found for os ${g_os_ver_arch}, start downloading"
    bash ${BASE_DIR}/start_download.sh --os-list=${g_os_ver_arch}
}

function encrypt_inventory() {
    local pass1=$(grep ansible_ssh_pass ${BASE_DIR}/inventory_file | wc -l)
    local pass2=$(grep ansible_sudo_pass ${BASE_DIR}/inventory_file | wc -l)
    local pass3=$(grep ansible_become_pass ${BASE_DIR}/inventory_file | wc -l)
    local pass_cnt=$((pass1 + pass2 + pass3))
    if [ ${pass_cnt} == 0 ];then
        return
    fi
    echo "The inventory_file need encrypt !"
    ansible-vault encrypt ${BASE_DIR}/inventory_file
    if [[ $? != 0 ]];then
        exit 1
    fi
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

function check_cmd_isok()
{
    if [[ $? != 0 ]];then
        exit 1
    fi
}

function install_kernel_header_devel_euler()
{
    local os_name=$(get_os_name)
    if [ "${os_name}" != "EulerOS" ];then
        return
    fi

    local euler=""
    if [[ "${g_os_ver_arch}" =~ 2.8 ]];then
        euler="eulerosv2r8.${arch}"
    else
        euler="eulerosv2r9.${arch}"
    fi

    local kh=$(rpm -qa kernel-headers | wc -l)
    local kd=$(rpm -qa kernel-devel | wc -l)
    local kh_rpm=$(find ${BASE_DIR}/resources/kernel/ -name "kernel-headers*" | sort -r | grep -m1 ${euler})
    local kd_rpm=$(find ${BASE_DIR}/resources/kernel/ -name "kernel-devel*" | sort -r | grep -m1 ${euler})
    if [ ${kh} -eq 0 ] && [ -f "${kh_rpm}" ];then
        rpm -ivh --force --nodeps --replacepkgs ${kh_rpm}
        check_cmd_isok
    fi
    if [ ${kd} -eq 0 ] && [ -f "${kd_rpm}" ];then
        rpm -ivh --force --nodeps --replacepkgs ${kd_rpm}
        check_cmd_isok
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
        rpm -ivh --force --nodeps --replacepkgs ${kh_rpm}
        check_cmd_isok
    fi
    if [ ${kd} -eq 0 ] && [ -f ${kd_rpm} ];then
        rpm -ivh --force --nodeps --replacepkgs ${kd_rpm}
        check_cmd_isok
    fi
}

function install_sys_packages()
{
    check_resources
    echo "install system packages"
    log_info "install system packages"

    install_kernel_header_devel
    install_kernel_header_devel_euler
    local have_rpm=0
    case ${g_os_name} in
    CentOS|EulerOS|SLES|Kylin|BCLinuxL|Tlinux|OpenEuler)
        local have_rpm=1
        ;;
    Ubuntu|Debian|Linx|UOS)
        local have_rpm=0
        ;;
    *)
        echo "ERROR: check OS ${g_os_name} fail"
        exit 1
        ;;
    esac

    if [ ${have_rpm} -eq 1 ]; then
        rpm -ivh --force --nodeps --replacepkgs ${BASE_DIR}/resources/${g_os_ver_arch}/*.rpm
    else
        export DEBIAN_FRONTEND=noninteractive && export DEBIAN_PRIORITY=critical; dpkg --force-all -i ${BASE_DIR}/resources/${g_os_ver_arch}/*.deb
    fi
    check_cmd_isok
}

function install_python375()
{
    if [ ! -f ${BASE_DIR}/resources/sources/Python-3.7.5.tar.xz ];then
        echo "can't find Python-3.7.5.tar.xz"
        return
    fi
    echo "install Python 3.7.5"
    log_info "install Python 3.7.5"

    mkdir -p -m 750 ~/build
    tar --no-same-owner -xf ${BASE_DIR}/resources/sources/Python-3.7.5.tar.xz -C ~/build
    cd ~/build/Python-3.7.5
    ./configure --enable-shared --prefix=${PYTHON_PREFIX}
    make -j20
    make install
    cd -
    python3.7 -m ensurepip
    python3.7 -m pip install --upgrade pip --no-index --find-links ${PYLIB_PATH}
    # install wheel, if not pip will use legacy setup.py install for installation
    python3.7 -m pip install wheel --no-index --find-links ${PYLIB_PATH}
    if [[ "${g_os_name}" == "EulerOS" ]] || [[ "${g_os_name}" == "OpenEuler" ]];then
        python3.7 -m pip install selinux --no-index --find-links ${PYLIB_PATH}
    fi
    echo "export PATH=${PYTHON_PREFIX}/bin:\$PATH" > ${PYTHON_PREFIX}/../ascendrc 2>/dev/null
    echo "export LD_LIBRARY_PATH=${PYTHON_PREFIX}/lib:\$LD_LIBRARY_PATH" >> ${PYTHON_PREFIX}/../ascendrc 2>/dev/null
}

function install_ansible()
{
    log_info "install ansible"
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
            sed -i "1528 i\    euleros:"                    ${ansible_path}/config/base.yml
            sed -i "1529 i\      '2': /usr/bin/python3"     ${ansible_path}/config/base.yml
            # kylin should use python3. if selinux enalbed, the default python have no selinux
            sed -i "1530 i\    kylin:"                      ${ansible_path}/config/base.yml
            sed -i "1531 i\      '10': /usr/bin/python3"    ${ansible_path}/config/base.yml
            # debian 10.0
            sed -i "1520 i\      '10.0': /usr/bin/python3" ${ansible_path}/config/base.yml
            # ubuntu 20.04 is recoginized as debian bullseye/sid due to /etc/debian_version
            sed -i "1522 i\      'bullseye/sid': /usr/bin/python3" ${ansible_path}/config/base.yml
            # openeuler os use python3 as default python interpreter
            sed -i "1534 i\    openeuler:"                    ${ansible_path}/config/base.yml
            sed -i "1535 i\      '20.03': /usr/bin/python3"     ${ansible_path}/config/base.yml
        fi
    fi
}

function verify_zip_redirect()
{
    echo "The system is busy with checking compressed files, Please wait for a moment..."
    log_info "verify zip"
    rm -rf ${BASE_DIR}/resources/run_from_*_zip
    check_extracted_size
    verify_zip > ${BASE_DIR}/tmp.log 2>&1
    local verify_result=$?
    cat ${BASE_DIR}/tmp.log >> ${BASE_DIR}/install.log
    cat ${BASE_DIR}/tmp.log && rm -rf ${BASE_DIR}/tmp.log
    if [ ${verify_result} -ne 0 ];then
        exit 1
    fi
}

function check_extracted_size()
{
    local IFS_OLD=$IFS
    unset IFS
    for zip_package in $(find ${BASE_DIR}/resources/ -name "*.zip" 2>/dev/null)
    do
        unzip -l ${zip_package} >/dev/null 2>&1
        if [[ $? != 0 ]];then
            echo "Error: ${zip_package} does not look like a zip archive"
            echo "Error: ${zip_package} does not look like a zip archive" >> ${BASE_DIR}/install.log
            exit 1
        fi
        local check_zip=$(unzip -l ${zip_package} | awk -v size_threshold="$SIZE_THRESHOLD" 'END {print ($1 < size_threshold)}')
        if [[ ${check_zip} == 0 ]];then
            echo "Error: ${zip_package} extracted size over 5G"
            echo "Error: ${zip_package} extracted size over 5G" >> ${BASE_DIR}/install.log
            exit 1
        fi
    done
    for tar_package in $(find ${BASE_DIR}/resources/ -type f -name "*.tar" -o -name "*.tar.*z*" 2>/dev/null)
    do
        tar tvf ${tar_package} >/dev/null 2>&1
        if [[ $? != 0 ]];then
            echo "Error: ${tar_package} does not look like a tar archive"
            echo "Error: ${tar_package} does not look like a tar archive" >> ${BASE_DIR}/install.log
            exit 1
        fi
        local check_tar=$(tar tvf ${tar_package} | awk -v size_threshold="$SIZE_THRESHOLD" '{sum += $3} END {print (sum < size_threshold)}')
        if [[ ${check_tar} == 0 ]];then
            echo "Error: ${tar_package} extracted size over 5G"
            echo "Error: ${tar_package} extracted size over 5G" >> ${BASE_DIR}/install.log
            exit 1
        fi
    done
    IFS=${IFS_OLD}
}

function check_npu_scene()
{
    IFS=","
    for product in $1
    do
        if [[ "$2" =~ ${product} ]];then
            echo 1
            unset IFS
            return 0
        fi
    done
    echo 0
    unset IFS
    return 0
}

function verify_zip()
{
    local IFS_OLD=$IFS
    unset IFS
    for zip_package in $(find ${BASE_DIR}/resources/CANN_* 2>/dev/null | grep zip ; find ${BASE_DIR}/resources/*.zip 2>/dev/null)
    do
        rm -rf ${BASE_DIR}/resources/zip_tmp && unzip ${zip_package} -d ${BASE_DIR}/resources/zip_tmp
        local cms_file=$(find ${BASE_DIR}/resources/zip_tmp/*.zip.cms 2>/dev/null || find ${BASE_DIR}/resources/zip_tmp/*.tar.gz.cms 2>/dev/null)
        local zip_file=$(find ${BASE_DIR}/resources/zip_tmp/*.zip 2>/dev/null || find ${BASE_DIR}/resources/zip_tmp/*.tar.gz 2>/dev/null)
        local crl_file=$(find ${BASE_DIR}/resources/zip_tmp/*.zip.crl 2>/dev/null || find ${BASE_DIR}/resources/zip_tmp/*.tar.gz.crl 2>/dev/null)
        openssl cms -verify -in ${cms_file} -inform DER -CAfile ${BASE_DIR}/playbooks/rootca.pem -binary -content ${zip_file} -purpose any -out /dev/null \
        && openssl crl -verify -in ${crl_file} -inform DER -CAfile ${BASE_DIR}/playbooks/rootca.pem -noout
        local verify_success=$?
        if [[ ${verify_success} -eq 0 ]];then
            if [[ "$(basename ${zip_file})" =~ zip ]];then
                if [[ $(check_npu_scene ${CANN_PRODUCT_LIST} $(basename ${zip_file}))  == 1 ]];then
                    local run_from_zip=${BASE_DIR}/resources/run_from_cann_zip
                elif [[ $(check_npu_scene ${INFER_PRODUCT_LIST} $(basename ${zip_file}))  == 1 ]];then
                    local run_from_zip=${BASE_DIR}/resources/run_from_infer_zip
                elif [[ $(check_npu_scene ${TRAIN_PRODUCT_LIST} $(basename ${zip_file}))  == 1 ]];then
                    local run_from_zip=${BASE_DIR}/resources/run_from_train_zip
                elif [[ $(check_npu_scene ${A300I_PRODUCT_LIST} $(basename ${zip_file}))  == 1 ]];then
                    local run_from_zip=${BASE_DIR}/resources/run_from_a300i_zip
                else
                    echo "Error: ${zip_file} not in PRODUCT_LIST"
                    return 1
                fi
                mkdir -p -m 750 ${run_from_zip} && unzip -o ${zip_file} -d ${run_from_zip}
            else
                if [[ "$(basename ${zip_file})" =~ atlasedge.*aarch64 ]];then
                    local atlasedge_dir=${BASE_DIR}/resources/run_from_cann_zip/atlasedge_aarch64
                elif [[ "$(basename ${zip_file})" =~ ha.*aarch64 ]];then
                    local atlasedge_dir=${BASE_DIR}/resources/run_from_cann_zip/ha_aarch64
                elif [[ "$(basename ${zip_file})" =~ atlasedge.*x86_64 ]];then
                    local atlasedge_dir=${BASE_DIR}/resources/run_from_cann_zip/atlasedge_x86_64
                elif [[ "$(basename ${zip_file})" =~ ha.*x86_64 ]];then
                    local atlasedge_dir=${BASE_DIR}/resources/run_from_cann_zip/ha_x86_64
                fi
                mkdir -p -m 750 ${atlasedge_dir}
                cp ${zip_file} ${cms_file} ${crl_file} ${atlasedge_dir}
                tar -xf ${zip_file} -C ${atlasedge_dir}
            fi
        fi
        rm -rf ${BASE_DIR}/resources/zip_tmp
        if [[ ${verify_success} -ne 0 ]];then
            echo "Error: check validation fail"
            return 1
        fi
    done
    IFS=${IFS_OLD}
}

function process_install()
{
    verify_zip_redirect
    local tmp_install_play=${BASE_DIR}/playbooks/tmp_install.yml
    echo "- import_playbook: gather_npu_fact.yml" > ${tmp_install_play}
    if [ "x${nocopy_flag}" != "xy" ];then
        echo "- import_playbook: distribution.yml" >> ${tmp_install_play}
    fi
    IFS=','
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

function process_scene()
{
    verify_zip_redirect
    local tmp_scene_play=${BASE_DIR}/playbooks/tmp_scene.yml
    echo "- import_playbook: gather_npu_fact.yml" > ${tmp_scene_play}
    if [ "x${nocopy_flag}" != "xy" ];then
        echo "- import_playbook: distribution.yml" >> ${tmp_scene_play}
    fi
    echo "- import_playbook: scene/scene_${install_scene}.yml" >> ${tmp_scene_play}
    echo "ansible-playbook ${VAULT_CMD} -i ./inventory_file ${tmp_scene_play} -e hosts_name=ascend ${DEBUG_CMD}"
    cat ${tmp_scene_play}
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${tmp_scene_play} -e "hosts_name=ascend" ${DEBUG_CMD}
    if [ -f ${tmp_scene_play} ];then
        rm -f ${tmp_scene_play}
    fi
}

function process_uninstall()
{
    local tmp_uninstall_play=${BASE_DIR}/playbooks/tmp_uninstall.yml
    echo "- import_playbook: gather_npu_fact.yml" > ${tmp_uninstall_play}
    IFS=','
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
    verify_zip_redirect
    local tmp_upgrade_play=${BASE_DIR}/playbooks/tmp_upgrade.yml
    echo "- import_playbook: gather_npu_fact.yml" > ${tmp_upgrade_play}
    if [ "x${nocopy_flag}" != "xy" ];then
        echo "- import_playbook: distribution.yml" >> ${tmp_upgrade_play}
    fi
    IFS=','
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
    local tmp_test_play=${BASE_DIR}/playbooks/tmp_test.yml
    echo "- import_playbook: gather_npu_fact.yml" > ${tmp_test_play}
    IFS=','
    for target in ${test_target}
    do
        echo "- import_playbook: test/test_${target}.yml" >> ${tmp_test_play}
    done
    unset IFS
    echo "ansible-playbook ${VAULT_CMD} -i ./inventory_file ${tmp_test_play} -e hosts_name=ascend ${DEBUG_CMD}"
    cat ${tmp_test_play}
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${tmp_test_play} -e "hosts_name=ascend" ${DEBUG_CMD}
    if [ -f ${tmp_test_play} ];then
        rm -f ${tmp_test_play}
    fi
}

function process_display()
{
    echo "ansible-playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${BASE_DIR}/playbooks/gather_app_info.yml -e hosts_name=ascend app_name=${display_target}"
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${BASE_DIR}/playbooks/gather_app_info.yml -e "hosts_name=ascend" -e "app_name=${display_target}"

}

function print_usage()
{
    unset IFS
    echo "Usage: ./install.sh [options]"
    echo " Options:"
    echo "--help  -h                     show this help message and exit"
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
    for scene in `find ${BASE_DIR}/playbooks/scene/scene_*.yml`
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
    for test in `find ${BASE_DIR}/playbooks/test/test_*.yml`
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
    echo "The \"npu\" will display driver and firmware together"
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
        --install=*)
            install_target=$(echo $1 | cut -d"=" -f2)
            if $(echo "${install_target}" | grep -Evq '^[a-zA-Z0-9._,]*$');then
                echo "ERROR" "--install parameter is invalid"
                print_usage
            fi
            shift
            ;;
        --install-scene=*)
            install_scene=$(echo $1 | cut -d"=" -f2)
            if $(echo "${install_scene}" | grep -Evq '^[a-zA-Z0-9._,]*$');then
                echo "ERROR" "--install-scene parameter is invalid"
                print_usage
            fi
            shift
            ;;
        --uninstall=*)
            uninstall_target=$(echo $1 | cut -d"=" -f2)
            if $(echo "${uninstall_target}" | grep -Evq '^[a-zA-Z0-9._,]*$');then
                echo "ERROR" "--uninstall parameter is invalid"
                print_usage
            fi
            shift
            ;;
        --uninstall-version=*)
            uninstall_version=$(echo $1 | cut -d"=" -f2)
            if $(echo "${uninstall_version}" | grep -Evq '^[a-zA-Z0-9._,]*$');then
                echo "ERROR" "--uninstall-version parameter is invalid"
                print_usage
            fi
            shift
            ;;
        --upgrade=*)
            upgrade_target=$(echo $1 | cut -d"=" -f2)
            if $(echo "${upgrade_target}" | grep -Evq '^[a-zA-Z0-9._,]*$');then
                echo "ERROR" "--upgrade parameter is invalid"
                print_usage
            fi
            shift
            ;;
        --test=*)
            test_target=$(echo $1 | cut -d"=" -f2)
            if $(echo "${test_target}" | grep -Evq '^[a-zA-Z0-9._,]*$');then
                echo "ERROR" "--test parameter is invalid"
                print_usage
            fi
            shift
            ;;
        --display=*)
            display_target=$(echo $1 | cut -d"=" -f2)
            if $(echo "${display_target}" | grep -Evq '^[a-zA-Z0-9._,]*$');then
                echo "ERROR" "--display parameter is invalid"
                print_usage
            fi
            shift
            ;;
        --output-file=*)
            output_file=$(echo $1 | cut -d"=" -f2)
            if $(echo "${output_file}" | grep -Evq '^[a-zA-Z0-9._,/]*$');then
                echo "ERROR" "--output-file parameter is invalid"
                print_usage
            fi
            shift
            ;;
        --stdout_callback=*)
            STDOUT_CALLBACK=$(echo $1 | cut -d"=" -f2)
            if $(echo "${STDOUT_CALLBACK}" | grep -Evq '^[a-zA-Z0-9._,]*$');then
                echo "ERROR" "--stdout_callback parameter is invalid"
                print_usage
            fi
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
    if [ -z ${install_target} ] && [ -z ${install_scene} ] && [ -z ${uninstall_target} ] && [ -z ${upgrade_target} ] && [ -z ${test_target} ] && [ -z ${display_target} ] && [[ ${check_flag} != "y" ]] && [[ ${clean_flag} != "y" ]];then
        echo "ERROR" "expected one valid argument at least"
        print_usage
    fi

    # --install
    IFS=','
    local unsupport=${FALSE}
    for target in ${install_target}
    do
        if [ ! -z ${target} ] && [ ! -f ${BASE_DIR}/playbooks/install/install_${target}.yml ];then
            echo "Error: not support install for ${target}"
            unsupport=${TRUE}
        fi
    done
    if [ ${unsupport} == ${TRUE} ];then
        print_usage
    fi
    unset IFS

    # --install-scene
    local unsupport=${FALSE}
    if [ ! -z ${install_scene} ] && [ ! -f ${BASE_DIR}/playbooks/scene/scene_${install_scene}.yml ];then
        echo "Error: not support install scene for ${install_scene}"
        unsupport=${TRUE}
    fi
    if [ ${unsupport} == ${TRUE} ];then
        print_usage
    fi

    # --uninstall
    IFS=','
    local not_supported=${FALSE}
    for target in ${uninstall_target}
    do
        if [ ! -z ${target} ] && [ ! -f ${BASE_DIR}/playbooks/uninstall/uninstall_${target}.yml ]; then
            echo "Error: not supported uninstall for ${target}"
            not_supported=${TRUE}
        fi
    done
    if [ "${not_supported}" == "${TRUE}" ]; then
        print_usage
    fi
    unset IFS

    # --upgrade
    IFS=','
    local not_supported=${FALSE}
    for target in ${upgrade_target}
    do
        if [ ! -z ${target} ] && [ ! -f ${BASE_DIR}/playbooks/upgrade/upgrade_${target}.yml ]; then
            echo "Error: not supported upgrade for ${target}"
            not_supported=${TRUE}
        fi
    done
    if [ "${not_supported}" == "${TRUE}" ]; then
        print_usage
    fi
    unset IFS

    # --test
    IFS=','
    local unsupport=${FALSE}
    for target in ${test_target}
    do
        if [ ! -z ${target} ] && [ ! -f ${BASE_DIR}/playbooks/test/test_${target}.yml ];then
            echo "Error: not support test for ${target}"
            unsupport=${TRUE}
        fi
    done
    if [ ${unsupport} == ${TRUE} ];then
        print_usage
    fi
    unset IFS

    # --display
    if [ ! -z ${display_target} ];then
        IFS=' '
        local unsupported=${TRUE}
        for target in ${app_name_list[*]}
        do
            if [ "${target}" == "${display_target}" ];then
                unsupported=${FALSE}
                break
            fi
        done
        if [ ${unsupported} == ${TRUE} ];then
            echo "Error: not support display for ${display_target}"
            print_usage
        fi
        unset IFS
    fi

    # --custom
    if [ "x${install_target}" != "x" ] && [ "x${install_scene}" != "x" ];then
        echo "ERROR" "Unsupported --install and --install-scene at same time"
        print_usage
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
    check_python375
    local py37_status=$?
    if [ ${py37_status} == ${FALSE} ] && [ $UID -eq 0 ];then
        install_sys_packages
        install_python375
    elif [ ${py37_status} == ${FALSE} ] && [ $UID -ne 0 ];then
        install_python375
    fi

    if [ ${have_ansible} -eq 0 ];then
        echo "no ansible"
        install_ansible
    fi
}

rotate_log()
{
    local log_list=$(ls $BASE_DIR/install.log* | sort -r)
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
    if [[ ! -e $BASE_DIR/install.log ]];then
        touch $BASE_DIR/install.log
    fi
    local log_size=$(ls -l $BASE_DIR/install.log | awk '{ print $5 }')
    if [[ ${log_size} -ge ${LOG_SIZE_THRESHOLD} ]];then
        rotate_log
    fi
}

function set_permission()
{
    chmod -R 750  $(find ${BASE_DIR}/  -type d ! -path "${BASE_DIR}/.git*" ! -path "${BASE_DIR}/resources/run_from_*_zip/*") 2>/dev/null
    chmod -R 640  $(find ${BASE_DIR}/  -type f ! -path "${BASE_DIR}/.git*" ! -path "${BASE_DIR}/resources/run_from_*_zip/*") 2>/dev/null
    for f in $(find ${BASE_DIR}/ -maxdepth 2 -type f  -name "*.sh" -o -name "*.py" ! -path "${BASE_DIR}/.git*" ! -path "${BASE_DIR}/resources/run_from_*_zip/*")
    do
        is_exe=$(file ${f} | grep executable | wc -l)
        if [[ ${is_exe} -eq 1 ]];then
            chmod 550 ${f} 2>/dev/null
        fi
    done
    chmod 750 $BASE_DIR/ $BASE_DIR/playbooks/install
    chmod 600 $BASE_DIR/install.log* $BASE_DIR/downloader.log* ${BASE_DIR}/inventory_file $BASE_DIR/ansible.cfg ${BASE_DIR}/downloader/config.ini ${BASE_DIR}/playbooks/rootca.pem 2>/dev/null
}

function prepare_environment()
{
    if [ -z ${ANSIBLE_STDOUT_CALLBACK} ] && [ ! -z ${STDOUT_CALLBACK} ];then
        export ANSIBLE_STDOUT_CALLBACK=${STDOUT_CALLBACK}
    fi
}

main()
{
    check_log
    set_permission
    parse_script_args $*
    check_script_args
    if [ -d ${BASE_DIR}/facts_cache ];then
        rm -rf ${BASE_DIR}/facts_cache
    fi
    if [ ${UID} == 0 ];then
        export PATH=/usr/local/python3.7.5/bin:$PATH
        export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH
        unset PYTHONPATH
    else
        export PATH=${HOME}/.local/python3.7.5/bin:$PATH
        export LD_LIBRARY_PATH=${HOME}/.local/python3.7.5/lib:$LD_LIBRARY_PATH
        unset PYTHONPATH
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
    if [ "x${uninstall_target}" != "x" ];then
        process_uninstall ${uninstall_target} ${uninstall_version}
    fi
    if [ "x${upgrade_target}" != "x" ];then
        process_upgrade ${upgrade_target}
    fi
    if [ "x${display_target}" != "x" ]; then
        process_display
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

}

main $*
