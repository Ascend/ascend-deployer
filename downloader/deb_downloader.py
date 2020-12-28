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

import urllib.request
import configparser
import os
import gzip
from urllib.error import HTTPError
from download_util import DOWNLOAD_INST
from download_util import calc_sha256
from logger_config import get_logger


DOC = r"""
ubuntu的子仓
main:完全的自由软件。
restricted:不完全的自由软件。
universe:ubuntu官方不提供支持与补丁，全靠社区支持。
muitiverse：非自由软件，完全不提供支持和补丁。
"""

LOG=get_logger(__file__)


class Package(object):
    """
    Package
    """
    def __init__(self, package, filename, sha256=None):
        self.package = package
        self.filename = filename
        self.sha256 = sha256

    def get_packagename(self):
        """get_packagename"""
        return self.package

    def get_filename(self):
        """get_filename"""
        return self.filename

    def get_sha256(self):
        """get_sha256"""
        return self.sha256


class Apt(object):
    """downloader for apt"""
    def __init__(self, source_file, arch):
        self.arch = arch
        self.cache = {}
        """读取源配置"""
        self.source = {}
        self.source_list = []
        self.mirror_url = None
        script = os.path.realpath(__file__)
        self.base_dir = os.path.dirname(os.path.dirname(script))
        self.repo_file = os.path.join(self.base_dir, source_file)
        with open(self.repo_file) as file:
            for line in file.readlines():
                tmp = line.split(' ')
                self.mirror_url = tmp[1]
                url = tmp[1] + 'dists/' + tmp[2]
                self.source[url] = tmp[3:]

        for url, type_list in self.source.items():
            for k in type_list:
                self.source_list.append("{0}/{1}".format(url, k).strip('\n'))

    def make_cache(self):
        """make_cache"""
        for sub_repo in self.source_list:
            binary_path = 'binary-amd64'
            if 'x86' not in self.arch:
                binary_path = 'binary-arm64'
            packages_url = '{0}/{1}/Packages.gz'.format(
                sub_repo, binary_path)
            print('packages_url=[{0}]'.format(packages_url))
            LOG.info('packages_url=[{0}]'.format(packages_url))
            packages = self.fetch_packages(packages_url)
            self.make_cache_from_packages(packages)

    def fetch_packages(self, packages_url):
        """
        fetch_packages

        :param packages_url:
        :return:
        """
        resp = DOWNLOAD_INST.urlopen(packages_url)
        if resp is not None:
            html = resp.read()
            return gzip.decompress(html).decode('utf-8')
        else:
            print('resp is None')
            LOG.warn('resp is None')
            return ''

    @staticmethod
    def version_compare(ver_a, ver_b):
        """
        version_compare 

        :param ver_a:
        :param ver_b:
        :return:
        """
        if len(ver_a) == len(ver_b):
            return ver_a > ver_b
        else:
            return len(ver_a) > len(ver_b)

    def make_cache_from_packages(self, packages_content):
        """
        make_cache_from_packages 

        :param packages_content:
        :return:
        """

        lines = packages_content.split('\n')
        package = ''
        filename = ''
        sha256 = None
        for line in lines:
            if "Package:" in line:
                package = line.split(': ')[1]

            if "SHA256" in line:
                sha256 = line.split(': ')[1]

            if "Filename:" in line:
                filename = line.split(': ')[1]
                
            if len(line.strip()) == 0:
                if package == 'cmake':
                    print('cmake =[{0}]'.format(filename))
                    LOG.info('cmake =[{0}]'.format(filename))
                if package in self.cache:
                    pkg = self.cache[package]
                    if self.version_compare(filename, pkg.get_filename()):
                        self.cache[package] = Package(package, filename, sha256)
                else:
                    self.cache[package] = Package(package, filename, sha256)

    def download(self, pkg, dst_dir):
        """
        download 

        :param name:
        :param dst_dir:
        :return:
        """
        if 'name' not in pkg:
            return
        name = pkg['name']
        url = None
        if name in self.cache.keys():
            url = self.mirror_url + self.cache[name].get_filename()
        else:
            print("can't find package {0}".format(name))
            LOG.error("can't find package {0}".format(name))
            return

        try:
            LOG.info('[{0}] download from [{1}]'.format(name, url))
            file_name = os.path.basename(self.cache[name].get_filename())
            dst_file = os.path.join(dst_dir, file_name)
            target_sha256 = self.cache[name].get_sha256()
            if not self.need_download_again(target_sha256, dst_file):
                LOG.info("{0} no need download again".format(name))
                print(name.ljust(60), 'exists')
                return
            DOWNLOAD_INST.download(url, dst_file)
            print(name.ljust(60), 'download success')
        except HTTPError as http_error:
            print('[{0}]->{1}'.format(url, http_error))
            LOG.error('[{0}]->{1}'.format(url, http_error))

    def need_download_again(self, target_sha256, dst_file):
        """
        need_download_again

        :param name:
        :param dst_dir:
        :return:
        """
        if target_sha256 is None:
            return True
        if not os.path.exists(dst_file):
            return True
        file_sha256 = calc_sha256(dst_file)
        if target_sha256 != file_sha256:
            LOG.info('target sha256 : {}, existed file sha256 : {}'.format(
                target_sha256, file_sha256))
            print('target sha256 : {}, existed file sha256 : {}'.format(
                target_sha256, file_sha256))
            return True
        else:
            return False


def main():
    """main"""
    apt_inst = Apt('downloader/config/Ubuntu_18.04_x86_64/source.list', 'x86_64')
    apt_inst.make_cache()
    apt_inst.download('libaec', "./")


if __name__ == '__main__':
    main()
