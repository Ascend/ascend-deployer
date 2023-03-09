#!/bin/bash
###
### image_load.sh — load image to host
###
### Usage:
###   image_load.sh <image_file> <host>
###
### Options:
###   <image_file>   Input file for image .
###   <host>  host of ansible inventory,one of master, all, worker.
###   -h        Show this message.
if [[ $# == 0 ]] || [[ "$1" == "-h" ]]; then
	awk -F'### ' '/^###/ { print $2 }' "$0"
	exit 1
fi
current_dir=$(cd $(dirname $0); pwd)
inventory_file_dir=$(cd $current_dir; pwd)
inventory_file_path="$inventory_file_dir/../inventory_file"
yamls_dir=$(cd $current_dir/..; pwd)
image_file=$1
if [ ! -f "$image_file" ]; then
    echo "image file :$image_file does not exist"
    exit 1
fi
if [[ "$image_file" != /* ]]; then
   echo "image file path should be absolute path"
       exit 1
fi
ansible_node=$2
if [[ "$ansible_node" != "master" && "$ansible_node" != "all" && "$ansible_node" != "worker" && "$ansible_node" != "mef" ]]; then
   echo "ansible node must be one of master, all, worker, mef"
       exit 1
fi
ansible-playbook -i $inventory_file_path --extra-vars "image_file=$image_file" --extra-vars "node=$ansible_node" $yamls_dir/yamls/image_load.yaml -vv