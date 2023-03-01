#!/bin/bash

set -e

df_info=$(df -h | grep -E "/var/lib/docker$" || df -h | grep '/var$' || df -h | grep -E "/$")
used_per_str=$(echo "$df_info" | awk '{print $5}')
# 系统已用百分比
used_per=$(echo "scale=2; $(echo "$used_per_str" | grep -Po '[0-9.]*')/ 100" | bc)

total_spa_str=$(echo "$df_info" | awk '{print $2}')
unit=$(echo "$total_spa_str" | grep -Po "[A-Z]")
# 系统总空间
total_spa=$(echo "$total_spa_str" | grep -Po "[0-9.]*")
total_spa_g=$total_spa

# 已用的空间数值
total_used_g=0
if [[ $unit == "M" ]]
then
    echo "bad"
    exit 0
elif [[ $unit == "T" ]]
then
    total_used_g=$(echo "scale=2;$total_spa * 1000 * $used_per"| bc)
    total_spa_g=$(echo "scale=2;$total_spa * 1000"| bc)
elif [[ $unit == "G" ]]
then
    total_used_g=$(echo "scale=2;$total_spa * $used_per"| bc)
else
    echo "bad"
    exit 0
fi

# k8s dl image is 6GB
k8s_dl_size=6
# train/infer image is 12GB
validate_image_size=12

total_used_new_g=$(echo "scale=2;$k8s_dl_size + $validate_image_size + $total_used_g"| bc)
new_userd_per=$(echo "scale=2;$total_used_new_g / $total_spa_g * 100"| bc)

max_used_per="70.00"
# bc返回值为1表示结果为真
if [[ $(echo "$new_userd_per > $max_used_per" | bc) == 1 ]]
then
    echo "bad"
else
    echo "ok"
fi