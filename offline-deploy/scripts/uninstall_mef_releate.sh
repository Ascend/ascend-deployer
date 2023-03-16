current_dir=$(cd $(dirname $0); pwd)
inventory_file_dir=$(cd $current_dir/..; pwd)
inventory_file_path="$inventory_file_dir/inventory_file"
yamls_dir=$(cd $current_dir/..; pwd)

read -n2 -p "This operation will cause other Kubernetes and Docker associated services to be unavailable. Do you want to continue[Y/N]" answer

run_ansible() {
  ansible-playbook -i $inventory_file_path $yamls_dir/playbooks/uninstall_mef_releate.yaml -vv
}

case $answer in
(Y|y)
    echo "uninstalling continue"
    run_ansible
esac
