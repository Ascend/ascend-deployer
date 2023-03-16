#!/bin/bash
set -e
current_dir=$(cd $(dirname $0); pwd)
. $current_dir/utils.sh

echo -e "\n[INFO]\t$(date +"%Y-%m-%d %H:%M:%S")\t ping host ...\n"
ansible -i $inventory_file_path all -m ping

ansible-playbook -i $inventory_file_path $inventory_file_dir/yamls/gather_facts.yaml -vv

ansible-playbook -i $inventory_file_path $inventory_file_dir/yamls/basic.yaml -vv

ansible-playbook -i $inventory_file_path $inventory_file_dir/yamls/check.yaml -vv

ansible-playbook -i $inventory_file_path $inventory_file_dir/yamls/docker.yaml -vv

ansible-playbook -i $inventory_file_path --extra-vars "HARBOR_HTTP=$harbor_server_http" $inventory_file_dir/yamls/harbor.yaml -vv

ansible-playbook -i $inventory_file_path --extra-vars "HARBOR_HTTP=$harbor_server_http" $inventory_file_dir/yamls/k8s.yaml -vv

ansible-playbook -i $inventory_file_path --extra-vars "HARBOR_HTTP=$harbor_server_http" $inventory_file_dir/yamls/mindxdl.yaml -vv