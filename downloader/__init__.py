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
# ============================================================================
"""
ascend-deployer download module
"""

import os
import shutil
import platform


dir_list = ['downloader', 'playbooks', 'docs']
file_list = ['install.sh', 'start_download.sh',
             'inventory_file', 'ansible.cfg',
             'README.md', 'README.en.md',
             'start_download_ui.bat', 'start_download.bat']
CUR_DIR = os.path.dirname(__file__)


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

    ad_path = os.path.join(deployer_home, 'ascend-deployer')
    if not os.path.exists(ad_path):
        os.makedirs(ad_path, mode=0o750, exist_ok=True)
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


copy_scripts()
