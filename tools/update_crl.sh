#!/bin/bash

readonly LOG_SIZE_THRESHOLD=$((20*1024*1024))
readonly LOG_COUNT_THRESHOLD=5
readonly BASE_DIR=$(cd "$(dirname $0)" > /dev/null 2>&1; pwd -P)
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

function log_info()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    echo "[INFO] $*"
    echo "${DATE_N} ${USER_N} [INFO] $*" >> ${BASE_DIR}/update_crl.log
}

function log_error()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    echo "[ERROR] $*"
    echo "${DATE_N} ${USER_N} [ERROR] $*" >> ${BASE_DIR}/update_crl.log
}

function rotate_log()
{
    local log_list=$(ls ${BASE_DIR}/update_crl.log* | sort -r)
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
    if [[ ! -e ${BASE_DIR}/update_crl.log ]];then
        touch ${BASE_DIR}/update_crl.log
    fi
    local log_size=$(ls -l ${BASE_DIR}/update_crl.log | awk '{ print $5 }')
    if [[ ${log_size} -ge ${LOG_SIZE_THRESHOLD} ]];then
        rotate_log
    fi
}

function set_permission()
{
    chmod 750 ${BASE_DIR}
    chmod 550 ${BASE_DIR}/update_crl.sh
    chmod 600 ${BASE_DIR}/update_crl.log 2>/dev/null
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
            log_info "update system crl"
            rm -rf $(dirname $2) && mkdir -p -m 700 $(dirname $2) && cp $1 $2 && chmod 600 $2
            return 0
        elif [[ ${zip_crl_lastupdate_time} -eq ${sys_crl_lastupdate_time} ]];then
            log_info "$1 is same with $2, no need to update system crl"
            return 0
        else
            log_info "$1 is older than $2, no need to update system crl"
            return 1
        fi
    else
        log_info "update system crl"
        rm -rf $(dirname $2) && mkdir -p -m 700 $(dirname $2) && cp $1 $2 && chmod 600 $2
    fi
    return 0
}

upgrade_crl()
{
    if [[ ${UID} == 0 ]];then
        local sys_crl=/etc/hwsipcrl/ascendsip.crl
    else
        local sys_crl=~/.local/hwsipcrl/ascendsip.crl
    fi
    local root_ca_file=${BASE_DIR}/rootca.pem
    echo -e "${ROOT_CA}" > ${root_ca_file}
    compare_crl $1 ${sys_crl} ${root_ca_file}
    local verify_crl=$?
    if [[ ${verify_crl} == 0 ]];then
        local updated_crl=$1
    elif [[ ${verify_crl} == 1 ]];then
        local updated_crl=${sys_crl}
    else
        rm -rf ${root_ca_file}
        log_error "$1 or ${sys_crl} check validation fail"
        exit 1
    fi
    if [[ "$(openssl crl -in ${updated_crl} -inform DER -noout -text)" =~ "$(openssl x509 -in ${root_ca_file} -serial -noout | awk -F'serial=' '{print $2}')" ]];then
        rm -rf ${root_ca_file}
        log_error "rootca check validation fail"
        exit 1
    fi
    rm -rf ${root_ca_file}
}

main()
{
    check_log
    set_permission
    if [[ $# != 1 ]] || [[ ! -f $1 ]];then
        log_error "expected one valid argument"
        exit 1
    fi
    upgrade_crl $1
}

main $*
