#!/bin/bash

uninstall_flag=$1

if [ "$uninstall_flag" = "--uninstall" ]; then
    cloudcore_status=$(systemctl is-active cloudcore)
    if [ "$cloudcore_status" = "active" ]; then
        systemctl stop cloudcore
    fi
    rm -rf /usr/local/bin/cloudcore /etc/kubeedge /lib/systemd/system/cloudcore.service /var/lib/kubeedge \
        /etc/mindx-dl/edge-manager /etc/mindx-dl/image-manager /etc/systemd/system/multi-user.target.wants/cloudcore.service
    systemctl daemon-reload
    echo "uninstall kubeedge success"
fi

if [ $# -eq 0 ]; then
    if command -v kubectl >/dev/null; then
        ansible-playbook -i ${HOME}/offline-deploy/inventory_file ${HOME}/offline-deploy/playbooks/kubeedge.yaml -v
    else
        echo "please install kubernetes first"
        exit 1
    fi
fi
