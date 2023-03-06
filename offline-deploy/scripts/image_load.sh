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

ansible-playbook -i $inventory_file_path --extra-vars "image_file=$image_file" $yamls_dir/yamls/image_load.yaml -vv