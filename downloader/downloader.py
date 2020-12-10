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

import os

from logger_config import get_logger
from pip_downloader import MyPip
from os_dep_downloader import OsDepDownloader

LOG = get_logger(__file__)


def download_python_packages():
    """download_python_packages"""
    script = os.path.realpath(__file__)
    require_file = os.path.join(os.path.dirname(script), 'requirements.txt')
    repo_path = os.path.join(os.path.dirname(script), '../resources')
    if not os.path.exists(repo_path):
        os.mkdir(repo_path)

    pip = MyPip()
    with open(require_file) as file_content:
        for line in file_content.readlines():
            print('[{0}]'.format(line.strip()))
            LOG.info('[{0}]'.format(line.strip()))
            pip.download(line.strip(), repo_path)


def download_os_packages():
    """download_os_packages"""
    os_dep = OsDepDownloader()
    os_dep.prepare_download_dir()
    os_dep.download_pkg_from_json()


if __name__ == "__main__":
    download_python_packages()
    download_os_packages()
