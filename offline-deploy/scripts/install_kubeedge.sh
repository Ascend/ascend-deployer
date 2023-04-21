#!/bin/bash

if [ $# -eq 0 ]; then
    if command -v kubectl >/dev/null; then
        ansible-playbook -i ${HOME}/offline-deploy/inventory_file ${HOME}/offline-deploy/playbooks/kubeedge.yaml -v
    else
        echo "please install kubernetes first"
        exit 1
    fi
fi
