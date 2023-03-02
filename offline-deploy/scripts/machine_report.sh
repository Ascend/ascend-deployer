current_dir=$(cd $(dirname $0); pwd)
inventory_file_dir=$(cd $current_dir/..; pwd)
inventory_file_path="$inventory_file_dir/inventory_file"
yamls_dir=$(cd $current_dir/..; pwd)

ansible-playbook -i $inventory_file_path $yamls_dir/yamls/report.yaml -vv