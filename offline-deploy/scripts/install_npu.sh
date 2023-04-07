#!/bin/bash
set -e
readonly INFER_PRODUCT_LIST="A300-3000,A300-3010"
readonly A310P_PRODUCT_LIST="Ascend-hdk-310p"
readonly TRAIN_PRODUCT_LIST="Ascend-hdk-910"
readonly TRAIN_910B_PRODUCT_LIST="Ascend-hdk-910b,Ascend910B-hdk"
readonly NPU_ZIP_DIR="/root/resources/npu/zip"
readonly NPU_RUN_DIR="/root/resources/npu/run"
CUR_DIR=$(dirname "$(readlink -f $0)")
readonly CUR_DIR
readonly inventory_file_path=${CUR_DIR}/../inventory_file
yamls_dir=$(
    cd $CUR_DIR/..
    pwd
)
readonly yamls_dir

function check_npu_scene() {
    IFS=","
    for product in $1; do
        if [[ "$2" =~ ${product} ]]; then
            echo 1
            unset IFS
            return 0
        fi
    done
    echo 0
    unset IFS
    return 0
}

function zip_extract() {
    unset IFS
    rm -rf ${NPU_ZIP_DIR}/run_from_*_zip
    for zip_package in $(find ${NPU_ZIP_DIR}/*.zip 2>/dev/null); do
        rm -rf ${NPU_ZIP_DIR}/zip_tmp && unzip -q ${zip_package} -d ${NPU_ZIP_DIR}/zip_tmp
        local zip_file=$(find ${NPU_ZIP_DIR}/zip_tmp/*.zip 2>/dev/null)
        if [[ $(check_npu_scene ${A310P_PRODUCT_LIST} $(basename ${zip_file})) == 1 ]]; then
            local run_from_zip=${NPU_ZIP_DIR}/run_from_310p_zip
        elif [[ $(check_npu_scene ${INFER_PRODUCT_LIST} $(basename ${zip_file})) == 1 ]]; then
            local run_from_zip=${NPU_ZIP_DIR}/run_from_310_zip
        elif [[ $(check_npu_scene ${TRAIN_910B_PRODUCT_LIST} $(basename ${zip_file}))  == 1 ]];then
            local run_from_zip=${NPU_ZIP_DIR}/run_from_910b_zip
        elif [[ $(check_npu_scene ${TRAIN_PRODUCT_LIST} $(basename ${zip_file})) == 1 ]]; then
            local run_from_zip=${NPU_ZIP_DIR}/run_from_910_zip
        else
            echo "not support $(basename ${zip_file}), please check"
            return 1
        fi
        mkdir -p -m 750 ${run_from_zip} && unzip -oq ${zip_file} -d ${run_from_zip}
    done
    rm -rf ${NPU_ZIP_DIR}/zip_tmp
}

function run_extract() {
    unset IFS
    rm -rf ${NPU_RUN_DIR}/run_from_*
    for run_file in $(find ${NPU_RUN_DIR} -name '*.run'); do
        if [[ $(check_npu_scene ${A310P_PRODUCT_LIST} $(basename ${run_file})) == 1 ]]; then
            local run_pkg_dir=${NPU_RUN_DIR}/run_from_310p
        elif [[ $(check_npu_scene ${INFER_PRODUCT_LIST} $(basename ${run_file})) == 1 ]]; then
            local run_pkg_dir=${NPU_RUN_DIR}/run_from_310
        elif [[ $(check_npu_scene ${TRAIN_910B_PRODUCT_LIST} $(basename ${run_file}))  == 1 ]];then
            local run_pkg_dir=${NPU_RUN_DIR}/run_from_910b_zip
        elif [[ $(check_npu_scene ${TRAIN_PRODUCT_LIST} $(basename ${run_file})) == 1 ]]; then
            local run_pkg_dir=${NPU_RUN_DIR}/run_from_910
        else
            echo "not support $(basename ${run_file}), please check"
            return 1
        fi
        mkdir -p -m 750 ${run_pkg_dir} && cp ${run_file} ${run_pkg_dir}
    done
}

type=zip
FORCE_UPGRADE_NPU=false

function print_usage() {
    echo "Usage: ./install_npu.sh [options]"
    echo " Options:"
    echo "--help  -h                     show this help message and exit"
    echo "--type=<zip/run>               Specify to use zip package or run package to install driver and firmware, default is zip"
    echo "--force_upgrade_npu            can force upgrade NPU when not all devices have exception"
}

function parse_script_args() {
    while true; do
        case "$1" in
        --help | -h)
            print_usage
            return 6
            ;;
        --type=*)
            type=$(echo $1 | cut -d"=" -f2)
            if [[ "${type}" != zip && "${type}" != run ]]; then
                echo "[ERROR] type should be zip or run"
                print_usage
                return 1
            fi
            shift
            ;;
        --force_upgrade_npu)
            FORCE_UPGRADE_NPU=true
            shift
            ;;
        *)
            if [ "x$1" != "x" ]; then
                echo "[ERROR] Unsupported parameters: $1"
                print_usage
                return 1
            fi
            break
            ;;
        esac
    done
}

function process_install() {
    ansible -i $inventory_file_path all -m ping
    ansible-playbook -i $inventory_file_path $yamls_dir/yamls/npu.yaml -e type=$type -e force_upgrade_npu=${FORCE_UPGRADE_NPU} -v
}

function main() {
    parse_script_args $*
    local parse_script_args_status=$?
    if [[ ${parse_script_args_status} != 0 ]]; then
        return ${parse_script_args_status}
    fi
    if [ $type = zip ]; then
        zip_extract
        process_install
    else
        run_extract
        process_install
    fi
}

main $*
main_status=$?
exit ${main_status}
