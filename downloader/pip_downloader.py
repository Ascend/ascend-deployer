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
import http.client
import time
from download_util import DOWNLOAD_INST
from download_util import calc_sha256, calc_md5
from logger_config import get_logger

LOG = get_logger(__file__)


class MyPip(object):
    """downloader for pip"""
    def __init__(self):
        self.cache = {}
        self.downloaded = []
        """读取配置"""
        script = os.path.realpath(__file__)
        config_file = os.path.join(os.path.dirname(script), 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_file)
        self.pypi_url = config.get('pypi', 'index_url')

    @staticmethod
    def file_download(url, dest):
        """
        file_download

        :param url:  待下载文件的url
        :param dest: 下载时本地文件名,带路径
        :return:
        """
        if os.path.exists(dest):
            LOG.info('[{0}] exist'.format(dest))
            os.remove(dest)
            LOG.info('[{0}] deleted'.format(dest))
        DOWNLOAD_INST.download(url, dest)

    @staticmethod
    def is_wheel_match(full_name, version, platform, implement):
        """
        is_wheel_match

        :param full_name:
        :param version:
        :param platform:
        :param implement:
        :return:
        """
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
            LOG.error(err)
            return False

        return True

    def get_simple_index(self, distribution):
        """
        get_simple_index

        :param distribution:
        :return:
        """
        if distribution in self.cache.keys():
            index = self.cache.get(distribution)
        else:
            url = '{0}/{1}'.format(self.pypi_url, distribution.lower())
            LOG.info('pypi URL = [{0}]'.format(url))
            index = ''
            for retry in [x + 1 for x in range(5)]:
                success = False
                try:
                    resp = DOWNLOAD_INST.urlopen(url)
                    index = resp.read()
                    success = True
                except http.client.HTTPException as e:
                    print(e)
                    LOG.error(e)
                    time.sleep(2 * retry)
                if success:
                    break
            self.cache[distribution] = index
        dom_tree = xml.dom.minidom.parseString(index)
        collection = dom_tree.documentElement
        idx = collection.getElementsByTagName('a')
        return idx

    def wheel_filter(self, index, version, platform, implement):
        """
        wheel_filter

        :param index:
        :param version:
        :param platform:
        :param implement:
        :return:
        """
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
        """
        source_filter

        :param index:
        :param version:
        :return:
        """
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
            LOG.error('can not find {0} for {1} {2}'.format(name, platform, implement))
            return False
        if file_name in self.downloaded:
            return
        download_url = '{0}/{1}/{2}'.format(self.pypi_url, distribution, url)
        LOG.info("Download {0} from [{1}]".format(file_name, download_url))
        file_path = os.path.join(dest_path, file_name)
        if not self.need_download_again(file_path, url):
            print(file_name.ljust(60), "exists")
            self.downloaded.append(file_name)
            LOG.info('no need download again')
            return True
        self.file_download(download_url, file_path)
        print(file_name.ljust(60), "download success")
        self.downloaded.append(file_name)
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
        if file_name in self.downloaded:
            return
        download_url = '{0}/{1}/{2}'.format(self.pypi_url, distribution, url)
        #print("Download {0} from [{1}]".format(file_name, download_url))
        LOG.info("Download {0} from [{1}]".format(file_name, download_url))
        file_path = os.path.join(dest_path, file_name)
        if not self.need_download_again(file_path, url):
            print(file_name.ljust(60), "exists")
            LOG.info('no need download again')
            self.downloaded.append(file_name)
            return True
        self.file_download(download_url, file_path)
        print(file_name.ljust(60), "download success")
        self.downloaded.append(file_name)
        return True

    def need_download_again(self, dst_file, url_with_hash):
        """
        need_download_again
        校验目的文件的hash值与url中的hash值是否相等，来决定是否重新下载

        :param dst_file: 目的文件
        :param url_with_hash:  带hash值的URL
        :return:
        """
        if url_with_hash is None or len(url_with_hash) == 0:
            return True
        if not os.path.exists(dst_file):
            return True

        key_word = ''
        file_hash = ''
        if 'sha256=' in url_with_hash:
            key_word = 'sha256='
            file_hash = calc_sha256(dst_file)
        elif 'md5=' in url_with_hash:
            key_word = 'md5='
            file_hash = calc_md5(dst_file)
        else:
            return True

        index_of_hash = str(url_with_hash).index(key_word) + len(key_word)
        target_hash = url_with_hash[index_of_hash:]
        if target_hash != file_hash:
            LOG.info('hash {0} in url: {1} != file: {2}'.format(key_word,
                target_hash, file_hash))
        return target_hash != file_hash

    def download_x86(self, name, dest_path):
        """
        download_x86

        :param name:
        :param dest_path:
        :return:
        """
        platform_list = ('manylinux1_x86_64', 'manylinux2010_x86_64',
                         'manylinux2014_x86_64')
        for platform in platform_list:
            if self.download_wheel(name, platform, 'cp37', dest_path):
                return True
        return False

    def download_arm(self, name, dest_path):
        """
        download_arm

        :param name:
        :param dest_path:
        :return:
        """
        platform = 'manylinux2014_aarch64'
        return self.download_wheel(name, platform, 'cp37', dest_path)

    def download(self, name, dest_path):
        """
        download

        :param name:
        :param dest_path:
        :return:
        """
        try:
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            if self.download_wheel(name, "none", 'cp37', dest_path):
                return

            if not self.download_x86(name, dest_path):
                self.download_source(name, dest_path)

            if not self.download_arm(name, dest_path):
                self.download_source(name, dest_path)
        except Exception as e:
            print(name.ljust(60), "download failed")


def main():
    """main"""
    my_pip = MyPip()
    my_pip.download('six==1.15.0', './')


if __name__ == '__main__':
    main()
