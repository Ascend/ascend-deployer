#!/bin/bash
have_python3=`command -v python3 | wc -l`
have_yum=`command -v yum | wc -l`
have_apt=`command -v apt | wc -l`
if [ ${have_python3} -eq 0 ];then
    if [ ${have_yum} -eq 1 ];then
        yum install -y python3
    fi
    if [ ${have_apt} -eq 1 ];then
        DEBIAN_FRONTEND=noninteractive apt -y install python3
    fi
fi
python3 downloader/downloader.py
python3 downloader/other_downloader.py
