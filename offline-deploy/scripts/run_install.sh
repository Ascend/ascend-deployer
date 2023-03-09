#!/bin/bash

current_dir=$(cd $(dirname $0); pwd)

bash $current_dir/install_ansible.sh && bash $current_dir/install_npu.sh && bash $current_dir/install.sh