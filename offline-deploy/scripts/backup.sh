#!/bin/bash
set -e
time="$(date +"%Y-%m-%d-%HH")"

# 备份旧的resources.tar.gz解压出的内容
cd /root
rm -rf offline-deploy.$time 2>/dev/null || true
mv offline-deploy offline-deploy.$time 2>/dev/null || true
rm -rf resources.$time 2>/dev/null || true
mv resources resources.$time 2>/dev/null || true

# 使用新的resources.tar.gz
cp -rf /root/upgrade/resources /root
cp -rf /root/upgrade/offline-deploy /root

# 备份旧的inventory_file
mv /root/offline-deploy/inventory_file /root/offline-deploy/inventory_file.bak || true

# 使用旧的inventory_file中的信息进行升级
cp -f /root/offline-deploy.$time/inventory_file /root/offline-deploy/

echo -e "[INFO]\t$(date +"%Y-%m-%d %H:%M:%S")\t old offline-deploy dir back up to /root/offline-deploy.$time"
echo -e "[INFO]\t$(date +"%Y-%m-%d %H:%M:%S")\t old resources dir back up to /root/resources.$time"