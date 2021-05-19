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

FILE_PATH=os.path.abspath(__file__)
CUR_DIR = os.path.dirname(__file__)

sys.path.append(CUR_DIR)

import logger_config
import pip_downloader
import os_dep_downloader
import other_downloader
import software_mgr

LOG = logger_config.get_logger(__file__)

dir_list = ['downloader', 'playbooks', 'scene', 'test']
file_list = ['install.sh', 'start_download.sh', 'inventory_file', 'ansible.cfg', 'README.md', 'README.en.md']

support_os_list = os.listdir(os.path.join(CUR_DIR, 'config'))
support_pkg_list = os.listdir(os.path.join(CUR_DIR, 'software'))


def download_other_packages(dst=None):
    """download other resources, such as source code tar ball"""
    return other_downloader.download_other_packages(dst)


def download_other_software(sofware_list, dst):
    """download other resources, such as source code tar ball"""
    return other_downloader.download_other_software(sofware_list, dst)


def download_python_packages(dst=None):
    """download_python_packages"""
    script = os.path.realpath(__file__)
    require_file = os.path.join(os.path.dirname(script), 'requirements.txt')
    if dst is None:
        repo_path = os.path.join(os.path.dirname(script), '../resources/pylibs')
    else:
        repo_path = os.path.join(dst, 'pylibs')

    pip = pip_downloader.MyPip()
    results = {'ok': [], 'failed': []}
    with open(require_file) as file_content:
        for line in file_content.readlines():
            LOG.info('[{0}]'.format(line.strip()))
            if pip.download(line.strip(), repo_path):
                results['ok'].append(line.strip())
                continue
            results['failed'].append(line.strip())
    return results


def download_os_packages(os_list=None, software_list=None, dst=None):
    """download_os_packages"""
    os_dep = os_dep_downloader.OsDepDownloader()
    if os_list is None and dst is None:
        os_dep.prepare_download_dir()
        return os_dep.download_pkg_from_json()
    else:
        return os_dep.download(os_list, software_list, dst)


def download_all(os_list, software_list, dst):
    """ download all resources for specific os list """
    res_dir = os.path.join(dst, "resources")
    download_python_packages(res_dir)
    download_os_packages(os_list, software_list, res_dir)
    download_other_software(software_list, dst)
    download_other_packages(dst)


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


def parse_argument():
    """
    解析参数
    """
    os_list_help = 'Specific OS list to download, supported os are:\n'
    for osname in sorted(support_os_list):
        os_list_help += '{}\n'.format(osname)
    download_help = 'Specific package list to download, supported packages are:\n'
    for pkg in support_pkg_list:
        pkg_name, version = pkg.split('_')
        download_help += '{}=={}\n'.format(pkg_name, version[:-5])

    parser = argparse.ArgumentParser(description="Download resources. Multiple parameter values should be separated by ','.", allow_abbrev=False,
                epilog="notes: When package's version is missing, it will download the latest version.",
                formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--os-list', action='store', dest='os_list',
            help=os_list_help)
    parser.add_argument('--download', action='store', dest='packages',
            help=download_help)

    args = parser.parse_args()
    if args.os_list is None and args.packages is None:
        parser.print_help()
        return

    if args.os_list is not None:
        for os_item in args.os_list.split(','):
            if os_item not in support_os_list:
                print('os {} is not supported'.format(os_item))
                sys.exit(1)
    if args.packages is not None:
        for soft in args.packages.split(','):
            if not software_mgr.is_software_support(soft):
                print('software {} is not supported'.format(soft))
                sys.exit(1)

    return args


def get_download_path():
    """
    get download path
    """
    if 'site-packages' not in CUR_DIR and 'dist-packages' not in CUR_DIR:
        cur = os.path.dirname(FILE_PATH)
        return os.path.dirname(cur)

    deployer_home = ''
    if platform.system() == 'Linux':
        deployer_home = os.getenv('HOME')
        if os.getenv('ASCEND_DEPLOYER_HOME') is not None:
            deployer_home = os.getenv('ASCEND_DEPLOYER_HOME')
    else:
        deployer_home = os.getcwd()

    copy_scripts()
    return os.path.join(deployer_home, 'ascend-deployer')


def main():
    """
    entry for console
    """
    args = parse_argument()

    download_path = get_download_path()
    if args is None:
        sys.exit(0)

    os_list = []
    if args.os_list is not None:
        os_list = args.os_list.split(',')
    software_list = []
    if args.packages is not None:
        software_list = args.packages.split(',')
    download_all(os_list, software_list, download_path)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        download_python_packages()
        download_os_packages()
        download_other_packages()
        sys.exit(0)
    main()
