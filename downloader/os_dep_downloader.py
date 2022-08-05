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
"""download os dependencies"""
import json
import os
import sys
import time

from deb_downloader import Apt
from rpm_downloader import Yum
from download_util import CONFIG_INST
import logger_config
import software_mgr
from downloader import get_download_path

LOG = logger_config.LOG


class OsDepDownloader:
    def __init__(self):
        self.os_list = CONFIG_INST.get_download_os_list()
        self.pkg_list = CONFIG_INST.get_download_pkg_list()
        self.project_dir = get_download_path()
        self.resources_dir = os.path.join(self.project_dir, 'resources')

    def download(self, os_list, software_list, dst):
        results = {}
        mindstudio_list = [software for software in software_list if "MindStudio" in software]
        for os_item in os_list:
            res = self.download_os(os_item, mindstudio_list, dst)
            results[os_item] = res
        return results

    def download_pkg_from_json(self):
        results = {}
        software_list = [software.replace("_", "==") for software in self.pkg_list if "MindStudio" in software]
        for os_item in self.os_list:
            res = self.download_os(os_item, software_list, self.resources_dir)
            results[os_item] = res
        return results

    def download_os(self, os_item, software_list, dst):
        """
        download os packages. debs or rpms
        :param os_itme:  Ubuntu_18.04_aarch64, CentOS_8.2_x86_64..
        """
        dst_dir = os.path.join(dst, os_item)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir, mode=0o750, exist_ok=True)
        LOG.info('item:{} save dir: {}'.format(os_item, os.path.basename(dst_dir)))

        config_file = os.path.join(self.project_dir, 'downloader/config/{0}/pkg_info.json'.format(os_item))
        source_list_file = os.path.join(self.project_dir, 'downloader/config/{0}/source.list'.format(os_item))
        downloader = None

        if os.path.exists(source_list_file):
            if 'aarch64' in os_item:
                downloader = Apt(source_list_file, 'aarch64')
            else:
                downloader = Apt(source_list_file, 'x86_64')
        else:
            source_repo_file = os.path.join(self.project_dir, 'downloader/config/{0}/source.repo'.format(os_item))
            if 'aarch64' in os_item:
                downloader = Yum(source_repo_file, 'aarch64')
            else:
                downloader = Yum(source_repo_file, 'x86_64')

        res = {'ok': [], 'failed':[]}
        if downloader is not None:
            if downloader.make_cache() is False:
                LOG.error('downloader make_cache failed')
                res['failed'].append(os_item)
                raise RuntimeError

        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if downloader.download(item, dst_dir):
                    res['ok'].append(item['name'])
                    continue
                print('download failed', item['name'])
                res['failed'].append(item['name'])
                raise RuntimeError

        for software in software_list:
            formal_name, version = software_mgr.get_software_name_version(software)
            pkg_list = software_mgr.get_software_sys(formal_name, os_item, version)
            soft_dst_dir = os.path.join(dst, "{0}_{1}".format(formal_name, version), os_item)
            for pkg in pkg_list:
                if downloader.download(pkg, soft_dst_dir):
                    res['ok'].append(pkg['name'])
                    continue
                print('download failed', pkg['name'])
                res['failed'].append(pkg['name'])
                raise RuntimeError
        if downloader is not None:
            downloader.clean_cache()
        return res
