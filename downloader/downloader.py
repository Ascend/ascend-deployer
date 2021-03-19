#!/usr/bin/env python3
# coding: utf-8
# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===========================================================================
"""downloader"""
import os
import sys
import shutil
import argparse
import platform

CUR_DIR = os.path.dirname(__file__)
sys.path.append(CUR_DIR)

import logger_config
import pip_downloader
import os_dep_downloader
import other_downloader

LOG = logger_config.get_logger(__file__)

dir_list = ['downloader', 'playbooks', 'scene', 'test']
file_list = ['install.sh', 'start_download.sh', 'inventory_file', 'ansible.cfg', 'README.md', 'README.en.md']

support_os_list = [
'Ubuntu_18.04_x86_64',
'Ubuntu_18.04_aarch64',
'CentOS_8.2_x86_64',
'CentOS_8.2_aarch64',
'CentOS_7.6_x86_64',
'CentOS_7.6_aarch64',
'EulerOS_2.8_aarch64',
'EulerOS_2.9_x86_64',
'EulerOS_2.9_aarch64',
'BCLinux_7.6_x86_64',
'BCLinux_7.6_aarch64',
'BCLinux_7.7_aarch6',
'Debian_9.9_x86_64',
'Debian_9.9_aarch64',
'Debian_10.0_x86_64',
'SLES_12.4_x86_64',
'SLES_12.5_x86_64',
'Kylin_V10Tercel_x86_64',
'UOS_20_x86_64',
'UOS_20_aarch64',
'Kylin_V10Tercel_aarch64',
'Linx_9_aarch64']


def download_other_packages(dst=None):
    """download other resources, such as source code tar ball"""
    other_downloader.download_other_packages(dst)


def download_python_packages(dst=None):
    """download_python_packages"""
    script = os.path.realpath(__file__)
    require_file = os.path.join(os.path.dirname(script), 'requirements.txt')
    if dst is None:
        repo_path = os.path.join(os.path.dirname(script), '../resources/pylibs')
    else:
        repo_path = os.path.join(dst, 'pylibs')

    pip = pip_downloader.MyPip()
    with open(require_file) as file_content:
        for line in file_content.readlines():
            LOG.info('[{0}]'.format(line.strip()))
            pip.download(line.strip(), repo_path)


def download_os_packages(os_item=None, dst=None):
    """download_os_packages"""
    os_dep = os_dep_downloader.OsDepDownloader()
    if os_item is None and dst is None:
        os_dep.prepare_download_dir()
        os_dep.download_pkg_from_json()
    else:
        os_dep.download(os_item, dst)


def download_all(os_item, dst):
    """ download all resources for specific os list """
    res_dir = os.path.join(dst, "resources")
    download_python_packages(res_dir)
    download_other_packages(dst)
    download_os_packages(os_item, res_dir)


def copy_scripts():
    """
    copy scripts from library to ASCEND_DEPLOY_HOME
    the default ASCEND_DEPLOYER_HOME is HOME
    """
    root_path = os.path.dirname(CUR_DIR)
    deployer_home = os.getenv('HOME')
    if platform.system() == 'Linux':
        if os.getenv('ASCEND_DEPLOYER_HOME') is not None:
            deployer_home = os.getenv('ASCEND_DEPLOYER_HOME')
    else:
        deployer_home = os.getcwd()

    ad_path= os.path.join(deployer_home, 'ascend-deployer')
    for dirname in dir_list:
        src = os.path.join(root_path, dirname)
        dst = os.path.join(ad_path, dirname)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copytree(src, dst)

    for filename in file_list:
        src = os.path.join(root_path, filename)
        dst = os.path.join(ad_path, filename)
        if not os.path.exists(dst) and os.path.exists(src):
            shutil.copy(src, dst)


def main():
    """
    entry for console
    """
    parser = argparse.ArgumentParser(description='download resources.', allow_abbrev=False)
    parser.add_argument('--os-list', action='store', dest='os_list',
            help='Specific OS list to download, supported os are:')
    args = parser.parse_args()
    if args.os_list is None:
        parser.print_help()
        for osname in support_os_list:
            print('                     {}'.format(osname))
        return

    deployer_home = ''
    if platform.system() == 'Linux':
        deployer_home = os.getenv('HOME')
        if os.getenv('ASCEND_DEPLOYER_HOME') is not None:
            deployer_home = os.getenv('ASCEND_DEPLOYER_HOME')
    else:
        deployer_home = os.getcwd()

    copy_scripts()
    download_path = os.path.join(deployer_home, 'ascend-deployer')
    download_all(args.os_list, download_path)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        download_python_packages()
        download_os_packages()
        download_other_packages()
        sys.exit(0)
    main()
