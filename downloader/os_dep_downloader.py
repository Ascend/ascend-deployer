#!/usr/bin/env python3
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

import json
import os
import sys
import time

from deb_downloader import Apt
from rpm_downloader import Yum
from download_util import CONFIG_INST
from logger_config import get_logger

LOG = get_logger(__file__)
CUR_DIR = os.path.dirname(os.path.realpath(__file__))


class OsDepDownloader:
    def __init__(self):
        self.os_list = CONFIG_INST.get_download_os_list()
        self.project_dir = os.path.dirname(CUR_DIR)
        self.resources_dir = os.path.join(self.project_dir, 'resources')

    def prepare_download_dir(self):
        for os_item in self.os_list:
            dst_dir = os.path.join(self.resources_dir, os_item)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir, mode=0o755, exist_ok=True)

    def clean_download_dir(self):
        if os.path.exists(self.resources_dir):
            import shutil
            shutil.rmtree(self.resources_dir)
        print('clean resources directory successfully')
        LOG.info('clean resources directory successfully')

    def download_pkg_from_json(self):
        for os_item in self.os_list:
            dst_dir = os.path.join(self.resources_dir, os_item)
            print('item:{} save dir: {}'.format(os_item, dst_dir))
            LOG.info('item:{} save dir: {}'.format(os_item, dst_dir))
            config_file = os.path.join(CUR_DIR,
                                       f'config/{os_item}/pkg_info.json')
            downloader = None
            if 'Ubuntu' in os_item or 'Debian' in os_item or 'Linx' in os_item:
                source_list_file = f'downloader/config/{os_item}/source.list'
                if 'aarch64' in os_item:
                    downloader = Apt(source_list_file, 'aarch64')
                else:
                    downloader = Apt(source_list_file, 'x86_64')
            else:
                source_repo_file = f'downloader/config/{os_item}/source.repo'
                if 'aarch64' in os_item:
                    downloader = Yum(source_repo_file, 'aarch64')
                else:
                    downloader = Yum(source_repo_file, 'x86_64')
            if downloader is not None:
                downloader.make_cache()

            with open(config_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for item in data:
                    downloader.download(item, dst_dir)


def main():
    os_dep = OsDepDownloader()
    if len(sys.argv) == 2 and sys.argv[1] == 'clean':
        print('clean download dir...')
        LOG.info('clean download dir...')
        os_dep.clean_download_dir()
    else:
        time_start = time.time()
        os_dep.prepare_download_dir()
        os_dep.download_pkg_from_json()
        print('total time: {} seconds'.format(time.time() - time_start))
        LOG.info('total time: {} seconds'.format(time.time() - time_start))


if __name__ == "__main__":
    main()
