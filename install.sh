#!/bin/bash
readonly TRUE=1
readonly FALSE=0
readonly SIZE_THRESHOLD=$((5*1024*1024*1024))
readonly ZIP_COUNT_THRESHOLD=3000
readonly TAR_COUNT_THRESHOLD=100000
readonly LOG_SIZE_THRESHOLD=$((20*1024*1024))
readonly LOG_COUNT_THRESHOLD=5
readonly kernel_version=$(uname -r)
readonly arch=$(uname -m)
readonly BASE_DIR=$(cd "$(dirname $0)" > /dev/null 2>&1; pwd -P)
readonly PYLIB_PATH=${BASE_DIR}/resources/pylibs
readonly A300I_PRODUCT_LIST="A300i-pro"
readonly INFER_PRODUCT_LIST="A300-3000,A300-3010"
readonly TRAIN_PRODUCT_LIST="A300t-9000,A800-9000,A800-9010,A900-9000"
readonly CANN_PRODUCT_LIST="Ascend-cann,Ascend-mindx"
readonly APP_NAME_LIST=(all npu driver firmware nnrt nnae tfplugin toolbox toolkit atlasedge ha)

readonly ROOT_CA=$(cat << EOF
-----BEGIN CERTIFICATE-----
MIIFTzCCAzegAwIBAgIIRbYUczgwtHkwDQYJKoZIhvcNAQELBQAwNzELMAkGA1UE
BhMCQ04xDzANBgNVBAoTBkh1YXdlaTEXMBUGA1UEAxMOSHVhd2VpIFJvb3QgQ0Ew
IBcNMTUxMDE1MDgwODUwWhgPMjA1MDEwMTUwODA4NTBaMDcxCzAJBgNVBAYTAkNO
MQ8wDQYDVQQKEwZIdWF3ZWkxFzAVBgNVBAMTDkh1YXdlaSBSb290IENBMIICIjAN
BgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA7kxjA5g73QH7nvrTI/ZEJP2Da3Q0
Mg00q8/mM5DAmFkS5/9ru1ZQnKXN5zoq53e4f1r9eUhwjoakWIPjoTdC27hhBoKb
ZbZODbS/uPFu8aXrcDnAnCe+02Dsh5ClHm+Dp37mIe56Nhw/fMVOqZf00cY4GyfJ
KyBRC1cdecg1i2mCApLBe9WZh4/xlmmhCurkl6RyWrXqz6Xmi9glZhlR67g0Y0CU
qtTvyv+GoJyTuH0zq1DUh6VRamKkmoHAMKpDgDfmFkH33UFwgU2X/ef6mJGpYsHu
jlcvon5NZKAYBHmOof2e9mxDyIZH0mZnDsneMF5EDK4jO+qBdFn5KdXy8lOGiVVJ
aeGtux3zG/LgGfil6881mylj3jHszyT0CyIRoQn9HwD5Pn6Punkp5BcyWdzdZ1TF
cBKuIWOGUhbzcFoXnkyz6iDe4gxtH4D3ZQ3x0lpxIHeWUxKl1H0FeoEJx6PL0Koc
/iJ+eMSzoxHx4J5CyTYgF99zpfS7nYXsRhr8y1asXcp7ubLoI8yLkMbBYrg+XFL0
3gOHmkttdX67xKnCxcpYFVWs+nPwyvOCm81SH1YYnJnGP5csjH8hH2xbZpMpwrCZ
n6lZf7tzafmezFgJ6f/A8NZPmzhXe+LXgfWaiE3dBTPFy6ubzBKlWT53BQpP4u11
YvdVxNxSwrKhE4UCAwEAAaNdMFswHwYDVR0jBBgwFoAUcnaWww+QnNRVuK6bSe73
31zJArQwDAYDVR0TBAUwAwEB/zALBgNVHQ8EBAMCAQYwHQYDVR0OBBYEFHJ2lsMP
kJzUVbium0nu999cyQK0MA0GCSqGSIb3DQEBCwUAA4ICAQBwV1EEsMrEarDE0hEq
EyA/N0YpBcUjNWO8UmLYWSzBpv4ePXNtV6PQ8RrGNthcisa56nbb+OfwclPpii01
j89QVI4SlU8BFJUyU/FIRIudlSXWJzAVJcjHatU6Sqi7OdGDoZOIkx0jmyJ5rKoY
oCj4hOjYHeYJIF/CEIF+OnZmj5P6e/MxxC0FvExgJrJyqgIGmRRRkoVEOxjpIHIt
nIFaEa7y8cX9wnvjhYICR6CRmm0jzNsfd0lwdtOedlh3F7nIk8Ot1p3wUMKg1HcM
cxzygWv4CjVTZy6E1/+s6KTEGwX0p/2ISJhfjtlREzvQ6mfwBPbI6NZmD0ymRsy7
mlEEPnkweoEFN9y8P8GITupl20n5C/RD8J+I3ABysW4J57FY6moJawjYvpqGQi+R
4viJ3QWyW+AyMO8hQim924uGNuxij8Avna2K5Mc4Tb/HjSBMJ9glsfTLNqN0xDT7
b7/4o2Fkk5Szt/rKTiSVVbH22US2ri5SV8A+gbH/41NjFNZlAxsxLSN0gHeStDih
kFs9liaQICKYpJToZKHS6hP0paYU61wSqy4lUEyka5KzQZIr7h/BZ8elVI6xGKHg
v2VSpgYKuxC59I+syXRsN6AslVRq8/2Zo1IPcU3k01VsZAlvARrxS+lYfztdiss0
gdNojAmDZwk73Vwty4KrPanEhw==
-----END CERTIFICATE-----
EOF
)

VAULT_CMD=""
DEBUG_CMD=""
STDOUT_CALLBACK=""

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

function log_info()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    echo "[INFO] $*"
    echo "${DATE_N} ${USER_N} [INFO] $*" >> ${BASE_DIR}/install.log
}

function log_warning()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    echo "[WARNING] $*"
    echo "${DATE_N} ${USER_N} [WARNING] $*" >> ${BASE_DIR}/install.log
}

function log_error()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    echo "[ERROR] $*"
    echo "${DATE_N} ${USER_N} [ERROR] $*" >> ${BASE_DIR}/install.log
}

function get_specified_python()
{
    if [ ! -z ${ASCEND_PYTHON_VERSION} ];then
        echo ${ASCEND_PYTHON_VERSION}
    else
        echo $(grep -oP "^ascend_python_version=\K.*" ${BASE_DIR}/downloader/config.ini)
    fi
}

readonly specified_python=$(get_specified_python)

function check_python_version()
{
    if $(echo "${specified_python}" | grep -Evq '^Python-3.(7|8).([0-9]|1[0-1])$');then
        log_error "ascend_python_version is not available, available Python-x.x.x is in 3.7.0~3.7.11 and 3.8.0~3.8.11"
        exit 1
    fi
}

check_python_version

readonly PYTHON_TAR=${specified_python}

readonly PYTHON_VERSION=$( echo ${specified_python} | sed 's/P/p/;s/-//')

readonly PYTHON_MINOR=$( echo ${PYTHON_VERSION%.*} )

if [ ${UID} == 0 ];then
    readonly PYTHON_PREFIX=/usr/local/${PYTHON_VERSION}
else
    readonly PYTHON_PREFIX=${HOME}/.local/${PYTHON_VERSION}
fi

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

    # UOS SP1
    if [ "${id}" == "UOS" ] && [[ "$(grep -oP "^VERSION=\"?\K[\w\ ]+" /etc/os-release | awk '{print $2}')" == "SP1" ]];then
        version="${ver}SP1"
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
        echo "install ${kh_rpm} when installing system packages" >> ${BASE_DIR}/install.log
        rpm -ivh --force --nodeps --replacepkgs ${kh_rpm}
        if [[ $? != 0 ]];then
            log_error "install kernel_header for euler fail"
            exit 1
        fi
    fi
    if [ ${kd} -eq 0 ] && [ -f "${kd_rpm}" ];then
        echo "install ${kd_rpm} when installing system packages" >> ${BASE_DIR}/install.log
        rpm -ivh --force --nodeps --replacepkgs ${kd_rpm}
        if [[ $? != 0 ]];then
            log_error "install kernel_devel for euler fail"
            exit 1
        fi
    fi
}

function install_kernel_header_devel()
{
    local have_rpm=$(command -v rpm | wc -l)
    if [ ${have_rpm} -eq 0 ]; then
        return
    fi
    local kh=$(rpm -q kernel-headers | grep ${kernel_version} | wc -l)
    local kd=$(rpm -q kernel-devel | grep ${kernel_version} | wc -l)
    local kh_rpm=${BASE_DIR}/resources/kernel/kernel-headers-${kernel_version}.rpm
    local kd_rpm=${BASE_DIR}/resources/kernel/kernel-devel-${kernel_version}.rpm
    if [ ${kh} -eq 0 ] && [ -f ${kh_rpm} ];then
        echo "install ${kh_rpm} when installing system packages" >> ${BASE_DIR}/install.log
        rpm -ivh --force --nodeps --replacepkgs ${kh_rpm}
        if [[ $? != 0 ]];then
            log_error "install kernel_header fail"
            exit 1
        fi
    fi
    if [ ${kd} -eq 0 ] && [ -f ${kd_rpm} ];then
        echo "install ${kd_rpm} when installing system packages" >> ${BASE_DIR}/install.log
        rpm -ivh --force --nodeps --replacepkgs ${kd_rpm}
        if [[ $? != 0 ]];then
            log_error "install kernel_devel fail"
            exit 1
        fi
    fi
}

# check if resource of specific os is exists
function check_resources()
{
    if [ -d ${BASE_DIR}/resources/${g_os_ver_arch} ];then
        return
    fi
    log_warning "no resources founded for os ${g_os_ver_arch}, start downloading"
    bash ${BASE_DIR}/start_download.sh --os-list=${g_os_ver_arch}
    if [[ $? != 0 ]];then
        log_error "download ${g_os_ver_arch} fail"
        exit 1
    fi
}

function install_sys_packages()
{
    check_resources
    log_info "install system packages"

    install_kernel_header_devel
    install_kernel_header_devel_euler
    local have_rpm=0
    case ${g_os_name} in
    CentOS|EulerOS|SLES|Kylin|BCLinux|Tlinux|OpenEuler)
        local have_rpm=1
        ;;
    Ubuntu|Debian|Linx|UOS)
        local have_rpm=0
        ;;
    *)
        log_error "check OS ${g_os_name} fail"
        exit 1
        ;;
    esac
    if [[ "${g_os_ver_arch}" == "Kylin_v10juniper_aarch64" ]];then
        local have_rpm=0
    fi

    echo "install system packages are listed as follows:" >> ${BASE_DIR}/install.log
    echo "$(ls ${BASE_DIR}/resources/${g_os_ver_arch} | grep -E "\.(rpm|deb)$")" >> ${BASE_DIR}/install.log
    if [ ${have_rpm} -eq 1 ]; then
        rpm -ivh --force --nodeps --replacepkgs ${BASE_DIR}/resources/${g_os_ver_arch}/*.rpm
    else
        export DEBIAN_FRONTEND=noninteractive && export DEBIAN_PRIORITY=critical; dpkg --force-all -i ${BASE_DIR}/resources/${g_os_ver_arch}/*.deb
    fi
    if [[ $? != 0 ]];then
        log_error "install system packages fail"
        exit 1
    fi
}

function have_no_python_module
{
    ret=`python3 -c "import ${1}" 2>&1 | grep "No module" | wc -l`
    return ${ret}
}

function check_python375()
{
    if [ ! -d ${PYTHON_PREFIX} ];then
        log_warning "no ${PYTHON_VERSION} installed"
        return ${FALSE}
    fi
    module_list="ctypes sqlite3 lzma"
    for module in ${module_list}
    do
        have_no_python_module ${module}
        ret=$?
        if [ ${ret} == ${TRUE} ];then
            log_warning "${PYTHON_VERSION} have no moudle ${module}"
            return ${FALSE}
        fi
    done
    return ${TRUE}
}

# check if resource of specific os is exists
function check_python_resource()
{
    if [ -f ${BASE_DIR}/resources/sources/${PYTHON_TAR}.tar.xz ];then
        return
    fi
    log_warning "can't find ${PYTHON_TAR}.tar.xz, start downloading"
    bash ${BASE_DIR}/start_download.sh --os-list=${g_os_ver_arch}
    if [[ $? != 0 ]];then
        log_error "download ${PYTHON_TAR}.tar.xz fail"
        exit 1
    fi
}

function install_python375()
{
    check_python_resource
    log_info "install ${PYTHON_VERSION}"

    mkdir -p -m 750 ~/build
    tar --no-same-owner -xf ${BASE_DIR}/resources/sources/${PYTHON_TAR}.tar.xz -C ~/build
    cd ~/build/${PYTHON_TAR}
    chmod 750 .
    ./configure --enable-shared --prefix=${PYTHON_PREFIX}
    make -j20
    make install
    cd -
    ${PYTHON_MINOR} -m ensurepip
    ${PYTHON_MINOR} -m pip install --upgrade pip --no-index --find-links ${PYLIB_PATH}
    # install wheel, if not pip will use legacy setup.py install for installation
    ${PYTHON_MINOR} -m pip install wheel --no-index --find-links ${PYLIB_PATH}
    if [[ "${g_os_name}" == "EulerOS" ]] || [[ "${g_os_name}" == "OpenEuler" ]];then
        echo "EulerOS or OpenEuler will install selinux when installing Python 3.7.5" >> ${BASE_DIR}/install.log
        ${PYTHON_MINOR} -m pip install selinux --no-index --find-links ${PYLIB_PATH}
    fi
    echo "export PATH=${PYTHON_PREFIX}/bin:\$PATH" > ${PYTHON_PREFIX}/../ascendrc 2>/dev/null
    echo "export LD_LIBRARY_PATH=${PYTHON_PREFIX}/lib:\$LD_LIBRARY_PATH" >> ${PYTHON_PREFIX}/../ascendrc 2>/dev/null
}

function install_ansible()
{
    log_info "install ansible"
    local ansible_path=${PYTHON_PREFIX}/lib/${PYTHON_MINOR}/site-packages/ansible
    ${PYTHON_MINOR} -m ensurepip
    ${PYTHON_MINOR} -m pip install --upgrade pip --no-index --find-links ${PYLIB_PATH}
    ${PYTHON_MINOR} -m pip install ansible --no-index --find-links ${PYLIB_PATH}
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
            sed -i "1532 i\      'V10': /usr/bin/python3"    ${ansible_path}/config/base.yml
            # debian 10.0
            sed -i "1520 i\      '10.0': /usr/bin/python3" ${ansible_path}/config/base.yml
            # ubuntu 20.04 is recoginized as debian bullseye/sid due to /etc/debian_version
            sed -i "1522 i\      'bullseye/sid': /usr/bin/python3" ${ansible_path}/config/base.yml
            # openeuler os use python3 as default python interpreter
            sed -i "1535 i\    openeuler:"                    ${ansible_path}/config/base.yml
            sed -i "1536 i\      '20.03': /usr/bin/python3"     ${ansible_path}/config/base.yml
            sed -i "1537 i\    uos:"                    ${ansible_path}/config/base.yml
            sed -i "1538 i\      '20': /usr/bin/python3"     ${ansible_path}/config/base.yml
        fi
    fi
}

function check_run_pkg()
{
    run_pkg=$(find ${BASE_DIR}/resources/*.run 2>/dev/null | wc -l)
    if [[ ${run_pkg} != 0 ]];then
        log_error "not support run package, please use zip package instead"
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
            log_error "${zip_package} does not look like a zip compressed file"
            exit 1
        fi
        local check_zip=$(unzip -l ${zip_package} | awk -v size_threshold="${SIZE_THRESHOLD}" -v count_threshold="${ZIP_COUNT_THRESHOLD}" 'END {print ($1 <= size_threshold && $2 <= count_threshold)}')
        if [[ ${check_zip} == 0 ]];then
            log_error "${zip_package} extracted size over 5G or extracted files count over ${ZIP_COUNT_THRESHOLD}"
            exit 1
        fi
    done
    for tar_package in $(find ${BASE_DIR}/resources/ -type f -name "*.tar" -o -name "*.tar.*z*" 2>/dev/null)
    do
        tar tvf ${tar_package} >/dev/null 2>&1
        if [[ $? != 0 ]];then
            log_error "${tar_package} does not look like a tar compressed file"
            exit 1
        fi
        local check_tar=$(tar tvf ${tar_package} | awk -v size_threshold="${SIZE_THRESHOLD}" -v count_threshold="${TAR_COUNT_THRESHOLD}" '{sum += $3} END {print (sum <= size_threshold && NR <= count_threshold)}')
        if [[ ${check_tar} == 0 ]];then
            log_error "${tar_package} extracted size over 5G or extracted files count over ${TAR_COUNT_THRESHOLD}"
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

function compare_crl()
{
    openssl crl -verify -in $1 -inform DER -CAfile $3 -noout
    if [[ $? != 0 ]];then
        return 2
    fi
    if [[ -f $2 ]];then
        openssl crl -verify -in $2 -inform DER -CAfile $3 -noout
        if [[ $? != 0 ]];then
            return 3
        fi
        local zip_crl_lastupdate_time=$(date +%s -d "$(openssl crl -in $1 -inform DER -noout -lastupdate | awk -F'lastUpdate=' '{print $2}')")
        local sys_crl_lastupdate_time=$(date +%s -d "$(openssl crl -in $2 -inform DER -noout -lastupdate | awk -F'lastUpdate=' '{print $2}')")
        if [[ ${zip_crl_lastupdate_time} -gt ${sys_crl_lastupdate_time} ]];then
            rm -rf $2 && mkdir -p -m 750 $(dirname $2) && cp $1 $2
            return 0
        elif [[ ${zip_crl_lastupdate_time} -eq ${sys_crl_lastupdate_time} ]];then
            return 0
        else
            log_info "$2 is newer than $1"
            return 1
        fi
    else
        mkdir -p -m 750 $(dirname $2) && cp $1 $2
    fi
    return 0
}

function verify_zip()
{
    local IFS_OLD=$IFS
    unset IFS
    if [[ ${UID} == 0 ]];then
        local sys_crl=/etc/hwsipcrl/ascendsip.crl
    else
        local sys_crl=~/.local/hwsipcrl/ascendsip.crl
    fi
    for zip_package in $(find ${BASE_DIR}/resources/CANN_* 2>/dev/null | grep zip ; find ${BASE_DIR}/resources/*.zip 2>/dev/null)
    do
        rm -rf ${BASE_DIR}/resources/zip_tmp && unzip ${zip_package} -d ${BASE_DIR}/resources/zip_tmp
        local cms_file=$(find ${BASE_DIR}/resources/zip_tmp/*.zip.cms 2>/dev/null || find ${BASE_DIR}/resources/zip_tmp/*.tar.gz.cms 2>/dev/null)
        local zip_file=$(find ${BASE_DIR}/resources/zip_tmp/*.zip 2>/dev/null || find ${BASE_DIR}/resources/zip_tmp/*.tar.gz 2>/dev/null)
        local crl_file=$(find ${BASE_DIR}/resources/zip_tmp/*.zip.crl 2>/dev/null || find ${BASE_DIR}/resources/zip_tmp/*.tar.gz.crl 2>/dev/null)
        local root_ca_file=${BASE_DIR}/playbooks/rootca.pem
        echo -e "${ROOT_CA}" > ${root_ca_file}
        compare_crl ${crl_file} ${sys_crl} ${root_ca_file}
        local verify_crl=$?
        if [[ ${verify_crl} == 0 ]];then
            local updated_crl=${crl_file}
        elif [[ ${verify_crl} == 1 ]];then
            local updated_crl=${sys_crl}
        else
            rm -rf ${root_ca_file}
            echo "[ERROR] ${crl_file} or ${sys_crl} check validation fail"
            return 1
        fi
        [[ ! "$(openssl crl -in ${updated_crl} -inform DER -noout -text)" =~ "$(openssl x509 -in ${root_ca_file} -serial -noout | awk -F'serial=' '{print $2}')" ]] \
        && openssl cms -verify -in ${cms_file} -inform DER -CAfile ${root_ca_file} -binary -content ${zip_file} -purpose any -out /dev/null
        local verify_success=$?
        rm -rf ${root_ca_file}
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
        chmod -R 750  $(find ${BASE_DIR}/resources/run_from_*_zip  -type d 2>/dev/null) 2>/dev/null
        chmod -R 640  $(find ${BASE_DIR}/resources/run_from_*_zip  -type f 2>/dev/null) 2>/dev/null
        if [[ ${verify_success} -ne 0 ]];then
            return 1
        fi
    done
    IFS=${IFS_OLD}
}

function verify_zip_redirect()
{
    log_info "The system is busy with checking compressed files, Please wait for a moment..."
    rm -rf ${BASE_DIR}/resources/run_from_*_zip ${BASE_DIR}/resources/zip_tmp
    check_run_pkg
    check_extracted_size
    verify_zip > ${BASE_DIR}/tmp.log 2>&1
    local verify_result=$?
    cat ${BASE_DIR}/tmp.log >> ${BASE_DIR}/install.log
    cat ${BASE_DIR}/tmp.log && rm -rf ${BASE_DIR}/tmp.log
    if [ ${verify_result} -ne 0 ];then
        log_error "check validation fail"
        exit 1
    fi
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
    echo "ansible-playbook ${VAULT_CMD} -i ./inventory_file ${tmp_install_play} -e hosts_name=ascend -e python_tar=${PYTHON_TAR} -e python_version=${PYTHON_VERSION} ${DEBUG_CMD}"
    cat ${tmp_install_play}
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${tmp_install_play} -e "hosts_name=ascend" -e python_tar=${PYTHON_TAR} -e python_version=${PYTHON_VERSION} ${DEBUG_CMD}
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
    echo "ansible-playbook ${VAULT_CMD} -i ./inventory_file ${tmp_scene_play} -e hosts_name=ascend -e python_tar=${PYTHON_TAR} -e python_version=${PYTHON_VERSION} ${DEBUG_CMD}"
    cat ${tmp_scene_play}
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${tmp_scene_play} -e "hosts_name=ascend" -e python_tar=${PYTHON_TAR} -e python_version=${PYTHON_VERSION} ${DEBUG_CMD}
    if [ -f ${tmp_scene_play} ];then
        rm -f ${tmp_scene_play}
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
    echo "ansible-playbook ${VAULT_CMD} -i ./inventory_file ${tmp_test_play} -e hosts_name=ascend -e python_tar=${PYTHON_TAR} -e python_version=${PYTHON_VERSION} ${DEBUG_CMD}"
    cat ${tmp_test_play}
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${tmp_test_play} -e "hosts_name=ascend" -e python_tar=${PYTHON_TAR} -e python_version=${PYTHON_VERSION} ${DEBUG_CMD}
    if [ -f ${tmp_test_play} ];then
        rm -f ${tmp_test_play}
    fi
}

function process_check()
{
    echo "ansible-playbook ${VAULT_CMD} -i ./inventory_file playbooks/gather_npu_fact.yml -e hosts_name=ascend -e python_tar=${PYTHON_TAR} -e python_version=${PYTHON_VERSION}"
    ansible_playbook ${VAULT_CMD} -i ${BASE_DIR}/inventory_file ${BASE_DIR}/playbooks/gather_npu_fact.yml -e "hosts_name=ascend" -e python_tar=${PYTHON_TAR} -e python_version=${PYTHON_VERSION}
}

function process_chean()
{
    ansible ${VAULT_CMD} -i ${BASE_DIR}/inventory_file all -m shell -a "rm -rf ~/resources.tar ~/resources"
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
    echo "--test=<target>                test the functions:"
    for test in `find ${BASE_DIR}/playbooks/test/test_*.yml`
    do
        test=$(basename ${test})
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
            ;;
        --install=*)
            install_target=$(echo $1 | cut -d"=" -f2)
            if $(echo "${install_target}" | grep -Evq '^[a-zA-Z0-9._,]*$');then
                log_error "--install parameter is invalid"
                print_usage
            fi
            shift
            ;;
        --install-scene=*)
            install_scene=$(echo $1 | cut -d"=" -f2)
            if $(echo "${install_scene}" | grep -Evq '^[a-zA-Z0-9._,]*$');then
                log_error "--install-scene parameter is invalid"
                print_usage
            fi
            shift
            ;;
        --test=*)
            test_target=$(echo $1 | cut -d"=" -f2)
            if $(echo "${test_target}" | grep -Evq '^[a-zA-Z0-9._,]*$');then
                log_error "--test parameter is invalid"
                print_usage
            fi
            shift
            ;;
        --output-file=*)
            output_file=$(echo $1 | cut -d"=" -f2)
            if $(echo "${output_file}" | grep -Evq '^[a-zA-Z0-9._,/-]*$');then
                log_error "--output-file parameter is invalid"
                print_usage
            fi
            shift
            ;;
        --stdout_callback=*)
            STDOUT_CALLBACK=$(echo $1 | cut -d"=" -f2)
            if $(echo "${STDOUT_CALLBACK}" | grep -Evq '^[a-zA-Z0-9._,]*$');then
                log_error "--stdout_callback parameter is invalid"
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
                log_error "Unsupported parameters: $1"
                print_usage
            fi
            break
            ;;
        esac
    done
}

function check_script_args()
{
    if [ -z ${install_target} ] && [ -z ${install_scene} ] && [ -z ${test_target} ] && [[ ${check_flag} != "y" ]] && [[ ${clean_flag} != "y" ]];then
        log_error "expected one valid argument at least"
        print_usage
    fi

    # --install
    IFS=','
    local unsupport=${FALSE}
    for target in ${install_target}
    do
        if [ ! -z ${target} ] && [ ! -f ${BASE_DIR}/playbooks/install/install_${target}.yml ];then
            log_error "not support install for ${target}"
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
        log_error "not support install scene for ${install_scene}"
        unsupport=${TRUE}
    fi
    if [ ${unsupport} == ${TRUE} ];then
        print_usage
    fi

    # --test
    IFS=','
    local unsupport=${FALSE}
    for target in ${test_target}
    do
        if [ ! -z ${target} ] && [ ! -f ${BASE_DIR}/playbooks/test/test_${target}.yml ];then
            log_error "not support test for ${target}"
            unsupport=${TRUE}
        fi
    done
    if [ ${unsupport} == ${TRUE} ];then
        print_usage
    fi
    unset IFS

    # --custom
    if [ "x${install_target}" != "x" ] && [ "x${install_scene}" != "x" ];then
        log_error "Unsupported --install and --install-scene at same time"
        print_usage
    fi
}

function ansible_playbook()
{
    if [ -z "${output_file}" ]; then
        ansible-playbook $*
    elif [ -f "${output_file}" ];then
        log_error "${output_file} already exists, please specify another output file name"
    else
        ansible-playbook $* > "${output_file}"
    fi
}

function encrypt_inventory() {
    local pass1=$(grep ansible_ssh_pass ${BASE_DIR}/inventory_file | wc -l)
    local pass2=$(grep ansible_sudo_pass ${BASE_DIR}/inventory_file | wc -l)
    local pass3=$(grep ansible_become_pass ${BASE_DIR}/inventory_file | wc -l)
    local pass_cnt=$((pass1 + pass2 + pass3))
    if [ ${pass_cnt} == 0 ];then
        return
    fi
    log_info "The inventory_file need encrypt"
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

function bootstrap()
{
    export PATH=${PYTHON_PREFIX}/bin:$PATH
    export LD_LIBRARY_PATH=${PYTHON_PREFIX}/lib:$LD_LIBRARY_PATH
    unset PYTHONPATH

    check_python375
    local py37_status=$?
    if [ ${py37_status} == ${FALSE} ] && [ $UID -eq 0 ];then
        install_sys_packages
        install_python375
    elif [ ${py37_status} == ${FALSE} ] && [ $UID -ne 0 ];then
        install_python375
    fi

    local have_ansible_cmd=$(command -v ansible | wc -l)
    have_no_python_module "ansible"
    if [[ $? == ${TRUE} ]] || [[ ${have_ansible_cmd} == 0 ]];then
        log_warning "no ansible"
        install_ansible
    fi
}

function rotate_log()
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
    chmod 600 $BASE_DIR/install.log* $BASE_DIR/downloader.log* ${BASE_DIR}/inventory_file $BASE_DIR/ansible.cfg ${BASE_DIR}/downloader/config.ini 2>/dev/null
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
        rm -rf ${BASE_DIR}/facts_cache && mkdir -p -m 750 ${BASE_DIR}/facts_cache
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

}

main $*
