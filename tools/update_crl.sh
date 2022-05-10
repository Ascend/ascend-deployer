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

readonly ROOT_CA_G2=$(cat << EOF
-----BEGIN CERTIFICATE-----
MIIGQjCCA/agAwIBAgIDPDrbMEEGCSqGSIb3DQEBCjA0oA8wDQYJYIZIAWUDBAIB
BQChHDAaBgkqhkiG9w0BAQgwDQYJYIZIAWUDBAIBBQCiAwIBIDB8MQswCQYDVQQG
EwJDTjEcMBoGA1UEChMTSHVhd2VpIFRlY2hub2xvZ2llczEnMCUGA1UECxMeSHVh
d2VpIENlcnRpZmljYXRpb24gQXV0aG9yaXR5MSYwJAYDVQQDEx1IdWF3ZWkgSW50
ZWdyaXR5IFJvb3QgQ0EgLSBHMjAgFw0yMTAyMDcwOTM2NDZaGA8yMDUxMDUwNzA5
MzY0NlowfDELMAkGA1UEBhMCQ04xHDAaBgNVBAoTE0h1YXdlaSBUZWNobm9sb2dp
ZXMxJzAlBgNVBAsTHkh1YXdlaSBDZXJ0aWZpY2F0aW9uIEF1dGhvcml0eTEmMCQG
A1UEAxMdSHVhd2VpIEludGVncml0eSBSb290IENBIC0gRzIwggIiMA0GCSqGSIb3
DQEBAQUAA4ICDwAwggIKAoICAQDdiU8j/HUtpiSLjsmr1t1P/nBDTbxuun0OVcia
Q6Oc+E6y1YXCUmFn+p1WwKEJQetkKbCWlcZch8I2G/f86J/Z4m4ZwZJSV04B/uKQ
GAy35FW5bNBtvYH3xN4ne0oGW6qWkgJQsDHG6iFZqRBKLx1O7yOhwvEdG5jfJwg2
6NK5ad75vM6LHA6tEPG9ttMhcmj9VgzUdAFOHOt1IlAkZ+odFn6Prte4i/M0bYZg
D/LShlgtBp+iDrWD+zHfcWADEGEsEzxyX7CJviJBTnoUwKM0/CQGLzaUTcGKfmVR
qvlxCuSGRYsZWlOyoGomiSzmHxCMKzshrHW+RTO6YidFvbt/eKM0TRl3sXm6S1+C
+FRY25es4lrXBm1/7VIcYy8CAmBAzYscFkaJqDiOqZ2wH3nDmonZeLgL0gfhSN5X
ofsOa3+K0FwLGMSs8S6znSyFdmgsdAu53EzQQ/CDolyDKza38sqRMxa2FSvIrbji
lypuUg6QH4p8XZdLac/D63s69rVbDgct9Yt39e7PCx51XLkQZevzW0wacuylvzyW
TCHqvNHo3zVLvfhtfB70LkhTTnZIcJFSi/Qz62BfQwBriMLEtNaFDyVA1/ZyJLPa
O0NvQ7T2tkkfsopSjGq8U9bcirLLyIJT3PW5j+zr96cO4nnO6TK2esXnBC6m/tqr
NhKnQwIDAQABo2MwYTAOBgNVHQ8BAf8EBAMCAQYwDwYDVR0TAQH/BAUwAwEB/zAd
BgNVHQ4EFgQUDjkBfSbLAmrgyjRlUCChRGzsf54wHwYDVR0jBBgwFoAUDjkBfSbL
AmrgyjRlUCChRGzsf54wQQYJKoZIhvcNAQEKMDSgDzANBglghkgBZQMEAgEFAKEc
MBoGCSqGSIb3DQEBCDANBglghkgBZQMEAgEFAKIDAgEgA4ICAQBhnanpVOz0exdF
fSyv8VxBZKL0XIYDue5nmeo0CJ2770Tj6NZawOJPkOAluzSAJpGKZdZgTfZdjKgR
UmGAzL0IBdOf2lbmRyz4Qm1e6nTqB6TvveyeksnxfxDAQq0t2zbIv41OS3RObf5C
T56TKR7mp7t6QR83Er8zaK8WbehFMx0puRTt+kST7b32Nzp2jI7jxlugi7+/oJoR
dwYd7NKTdkpjLSBz3dfigt2Gp8U5BTXxAvO6hsVkb4OHbJ5n+h5avY8q/Hzzd2xc
7bJFHVy5pL4nh/vM1z8/MRZUpxGLKOozNarYESVSzIZc9ovA08WKmaSqXkCgNwEv
7K/cDCnKAp73aknUAGJg6zAN3BZikSLYM+V+Tmc4FR/UQG/+GSkdvg0kmxKt3izw
oVctj/Je350VQLOgYkmOTQXdBCtMo8T5q/ZWq8mct1DtS4KaLxgLQQN214QS5MqY
68mFyuU3eKN7sD7BUzhG6t+phVhFJ6mslPOpaxOSaUFwBXW1nZ4afoKrk7EFXVQ1
xr37Fsc+a2P7DF9GD4liyzLc+0xOJZRVrM7fNPbdID0a2gp65qyTK4wrD/xsS7c6
NtAPvl8SX/H76yV7/XFtqmmfRj3YyGj2DctWZ8qUVTsxHQxVMWkeFzf7G4au6jqn
UCrZxwwkrbPM3H6LA3VdrF1oWN0hjg==
-----END CERTIFICATE-----
EOF
)

function operation_log_info()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    local IP_N=$(who am i | awk '{print $NF}' | sed 's/[()]//g')
    echo "${DATE_N} ${USER_N}@${IP_N} [INFO] $*" >> ${BASE_DIR}/update_crl_operation.log
}

function echo_info()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    local IP_N=$(who am i | awk '{print $NF}' | sed 's/[()]//g')
    echo "${DATE_N} ${USER_N}@${IP_N} [INFO] $*" >> ${BASE_DIR}/update_crl.log
}

function log_info()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    local IP_N=$(who am i | awk '{print $NF}' | sed 's/[()]//g')
    echo "[INFO] $*"
    echo "${DATE_N} ${USER_N}@${IP_N} [INFO] $*" >> ${BASE_DIR}/update_crl.log
}

function log_error()
{
    local DATE_N=$(date "+%Y-%m-%d %H:%M:%S")
    local USER_N=$(whoami)
    local IP_N=$(who am i | awk '{print $NF}' | sed 's/[()]//g')
    echo "[ERROR] $*"
    echo "${DATE_N} ${USER_N}@${IP_N} [ERROR] $*" >> ${BASE_DIR}/update_crl.log
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
    chmod 600 ${BASE_DIR}/update_crl.log ${BASE_DIR}/update_crl_operation.log 2>/dev/null
    chmod 400 ${BASE_DIR}/update_crl.log.? ${BASE_DIR}/update_crl_operation.log.? 2>/dev/null
}

function compare_crl()
{
    openssl crl -verify -in $1 -inform DER -CAfile $3 -noout 2>/dev/null
    if [[ $? != 0 ]];then
        echo_info "$3 check $1 validation not pass"
        return 2
    fi
    if [[ -f $2 ]];then
        openssl crl -verify -in $2 -inform DER -CAfile $3 -noout 2>/dev/null
        if [[ $? != 0 ]];then
            echo_info "$3 check $2 validation not pass"
            return 3
        fi
        local zip_crl_lastupdate_time=$(date +%s -d "$(openssl crl -in $1 -inform DER -noout -lastupdate | awk -F'lastUpdate=' '{print $2}')")
        local sys_crl_lastupdate_time=$(date +%s -d "$(openssl crl -in $2 -inform DER -noout -lastupdate | awk -F'lastUpdate=' '{print $2}')")
        if [[ ${zip_crl_lastupdate_time} -gt ${sys_crl_lastupdate_time} ]];then
            log_info "$2 system crl update success"
            mkdir -p -m 700 $(dirname $2) && cp $1 $2 && chmod 600 $2
            return 0
        elif [[ ${zip_crl_lastupdate_time} -eq ${sys_crl_lastupdate_time} ]];then
            log_info "$1 is same with $2, no need to update system crl"
            return 0
        else
            log_info "$1 is older than $2, no need to update system crl"
            return 1
        fi
    else
        log_info "$2 system crl update success"
        mkdir -p -m 700 $(dirname $2) && cp $1 $2 && chmod 600 $2
    fi
    return 0
}

function zip_extract()
{
    local crl_file=$1
    local sys_crl=$2
    local ca_file=$3
    compare_crl ${crl_file} ${sys_crl} ${ca_file}
    local verify_crl=$?
    if [[ ${verify_crl} == 0 ]];then
        local updated_crl=${crl_file}
    elif [[ ${verify_crl} == 1 ]];then
        local updated_crl=${sys_crl}
    else
        return 1
    fi
    if [[ "$(openssl crl -in ${updated_crl} -inform DER -noout -text)" =~ "$(openssl x509 -in ${ca_file} -serial -noout | awk -F'serial=' '{print $2}')" ]];then
        echo_info "${updated_crl} check ${ca_file} expired"
        return 1
    fi
}

upgrade_crl()
{
    local zip_extract_result=0
    if [[ ${UID} == 0 ]];then
        local sys_crl_file=/etc/hwsipcrl/ascendsip.crl
        local sys_g2_crl_file=/etc/hwsipcrl/ascendsip_g2.crl
    else
        local sys_crl_file=~/.local/hwsipcrl/ascendsip.crl
        local sys_g2_crl_file=~/.local/hwsipcrl/ascendsip_g2.crl
    fi
    local root_ca_g2_file=${BASE_DIR}/rootca_g2.pem
    echo -e "${ROOT_CA_G2}" > ${root_ca_g2_file}
    local root_ca_file=${BASE_DIR}/rootca.pem
    echo -e "${ROOT_CA}" > ${root_ca_file}
    zip_extract $1 ${sys_g2_crl_file} ${root_ca_g2_file} || zip_extract $1 ${sys_crl_file} ${root_ca_file}
    [[ $? != 0 ]] && local zip_extract_result=1 && log_error "check validation fail"
    rm -rf ${root_ca_g2_file} ${root_ca_file}
    return ${zip_extract_result}
}

main()
{
    check_log ${BASE_DIR}/update_crl.log
    check_log ${BASE_DIR}/update_crl_operation.log
    set_permission
    if [[ $# != 1 ]] || [[ ! -f $1 ]];then
        log_error "expected one valid argument"
        return 1
    fi
    if [[ ${UID} == 0 ]];then
        local ascend_cert_path=/usr/local/Ascend/toolbox/latest/Ascend-DMI/bin/ascend-cert
    else
        local ascend_cert_path=~/Ascend/toolbox/latest/Ascend-DMI/bin/ascend-cert
    fi
    if [ -f ${ascend_cert_path} ];then
        echo_info "${ascend_cert_path} -u $1"
        ${ascend_cert_path} -u $1
    else
        echo_info "openssl upgrade $1"
        upgrade_crl $1
    fi
}

main $*
main_status=$?
if [[ ${main_status} == 1 ]];then
    operation_log_info "parameter error,run failed"
else
    operation_log_info "$0 $*: Success"
fi
exit ${main_status}
