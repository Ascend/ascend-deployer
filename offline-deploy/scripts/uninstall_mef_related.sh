current_dir=$(cd $(dirname $0); pwd)
inventory_file_dir=$(cd $current_dir/..; pwd)
inventory_file_path="$inventory_file_dir/inventory_file"
yamls_dir=$(cd $current_dir/..; pwd)

read -n2 -p "Do you want to uninstall Kubernetes and Docker[Y/N]" answer

run_uninstall_all() {
  ansible-playbook -i $inventory_file_path $yamls_dir/playbooks/uninstall_mef_releate.yaml
}

run_uninstall_mef_kubeedge() {
  ansible-playbook -i $inventory_file_path $yamls_dir/playbooks/uninstall_mef_kubeedge.yaml
}

case $answer in
  (Y|y)
      echo "uninstalling all"
      run_uninstall_all
      ;;
  (N|n)
      echo "uninstalling mef and kubeedge"
      run_uninstall_mef_kubeedge
      ;;
esac
