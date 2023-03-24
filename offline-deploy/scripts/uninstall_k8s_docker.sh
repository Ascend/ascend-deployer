#!/bin/bash

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