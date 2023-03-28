#!/bin/bash

# 卸载kubeedge
cloudcore_status=$(systemctl is-active cloudcore)
if [ "$cloudcore_status" = "active" ]; then
    systemctl stop cloudcore
fi
rm -rf /usr/local/bin/cloudcore /etc/kubeedge /lib/systemd/system/cloudcore.service /var/lib/kubeedge \
    /etc/mindx-dl/edge-manager /etc/mindx-dl/image-manager /etc/systemd/system/multi-user.target.wants/cloudcore.service
systemctl daemon-reload
echo "uninstall kubeedge success"

# 卸载MEF-Center
run_file=/usr/local/MEF-Center/mef-center/run.sh
if [ ! -f "$run_file" ]; then
  echo "MEF-Center is not installed."; exit 1;
fi

bash /usr/local/MEF-Center/mef-center/run.sh uninstall