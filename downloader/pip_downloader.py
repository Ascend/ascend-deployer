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
import configparser
import urllib.request
import xml.dom.minidom
from download_util import DOWNLOAD_INST


class MyPip():
    def __init__(self):
        self.cache = {}
        """读取配置"""
        script = os.path.realpath(__file__)
        config_file = os.path.join(os.path.dirname(script), 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_file)
        self.pypi_url = config.get('pypi', 'index_url')

    @staticmethod
    def file_download(url, dest):
        if os.path.exists(dest):
            print('[{0}] exist'.format(dest))
        else:
            DOWNLOAD_INST.download(url, dest)

    @staticmethod
    def is_wheel_match(full_name, version, platform, implement):
        try:
            elements = full_name.split('-')
            wheel_version = elements[1]
            wheel_impl = elements[2]
            wheel_platform = elements[4].split('.')[0]
            if wheel_version != version:
                return False

            if wheel_impl not in ('py3', 'py2.py3', implement):
                return False

            if wheel_platform not in ('any', platform):
                return False

        except IndexError as err:
            print(err)
            return False

        return True

    def get_simple_index(self, distribution):
        if distribution in self.cache.keys():
            index = self.cache.get(distribution)
            print('get from cache')
        else:
            url = '{0}/{1}'.format(self.pypi_url, distribution.lower())
            print('pypi URL = [{0}]'.format(url))
            resp = DOWNLOAD_INST.urlopen(url)
            index = resp.read()
            self.cache[distribution] = index
        dom_tree = xml.dom.minidom.parseString(index)
        collection = dom_tree.documentElement
        idx = collection.getElementsByTagName('a')
        return idx

    def wheel_filter(self, index, version, platform, implement):
        pkg = ''
        url = ''
        for i in index:
            name = i.firstChild.nodeValue
            if 'whl' in name:
                if self.is_wheel_match(name, version, platform, implement):
                    pkg = name
                    url = i.getAttribute('href')
            else:
                continue
        return pkg, url

    @staticmethod
    def source_filter(index, version):
        pkg = ''
        url = ''
        for i in index:
            name = i.firstChild.nodeValue
            if 'tar' in name or 'zip' in name:
                if version in name:
                    pkg = name
                    url = i.getAttribute('href')
            else:
                continue
        return pkg, url

    def download_wheel(self, name, platform, implement, dest_path):
        """
        下载软件包
        """
        distribution, version = name.split('==')
        index = self.get_simple_index(distribution)
        file_name, url = self.wheel_filter(index, version, platform, implement)
        if len(url) == 0:
            print('can find {0} for {1} {2}'.format(name, platform, implement))
            return False
        download_url = '{0}/{1}/{2}'.format(self.pypi_url, distribution, url)
        print("Download {0} from [{1}]".format(file_name, download_url))
        file_path = os.path.join(dest_path, file_name)
        self.file_download(download_url, file_path)
        return True

    def download_source(self, name, dest_path):
        """
        下载源码包
        """
        distribution, version = name.split('==')
        index = self.get_simple_index(distribution)
        file_name, url = self.source_filter(index, version)
        if len(url) == 0:
            return False
        download_url = '{0}/{1}/{2}'.format(self.pypi_url, distribution, url)
        print("Download {0} from [{1}]".format(file_name, download_url))
        file_path = os.path.join(dest_path, file_name)
        self.file_download(download_url, file_path)
        return True

    def download_x86(self, name, dest_path):
        platform_list = ('manylinux1_x86_64', 'manylinux2010_x86_64',
                         'manylinux2014_x86_64')
        for platform in platform_list:
            if self.download_wheel(name, platform, 'cp37', dest_path):
                return True
        return False

    def download_arm(self, name, dest_path):
        platform = 'manylinux2014_aarch64'
        return self.download_wheel(name, platform, 'cp37', dest_path)

    def download(self, name, dest_path):
        x86_64_path = os.path.join(dest_path, 'x86_64')
        aarch64_path = os.path.join(dest_path, 'aarch64')
        if not os.path.exists(x86_64_path):
            os.mkdir(x86_64_path)
        if not os.path.exists(aarch64_path):
            os.mkdir(aarch64_path)

        if not self.download_x86(name, x86_64_path):
            self.download_source(name, x86_64_path)

        if not self.download_arm(name, aarch64_path):
            self.download_source(name, aarch64_path)


def main():
    my_pip = MyPip()
    my_pip.download('six==1.15.0', './')


if __name__ == '__main__':
    main()
