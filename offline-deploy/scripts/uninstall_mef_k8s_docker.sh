#!/bin/bash

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

shopt -s expand_aliases
# 判断包管理
use_dpkg=$(dpkg --help 2>&1 |wc -l)
if [[ $use_dpkg != 1 ]]
then
  alias LIST="dpkg -l | egrep -i"
  alias UNINSTALL="apt purge -y"
else
  alias LIST="rpm -qa | egrep -i"
  alias UNINSTALL="yum erase -y"
fi
# 卸载K8S
systemctl restart docker
UNINSTALL kubeadm kubectl kubelet kubernetes-cni

# 卸载docker
echo "list docker packages"
for pkg in `LIST docker`;
  do echo $pkg;
done


groupdel docker
for pkg in `LIST "docker|container"`;
do UNINSTALL $pkg;
done