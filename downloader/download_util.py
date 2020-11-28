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
import socket
from urllib import request
from urllib import parse
from urllib.error import ContentTooShortError, URLError

CUR_DIR = os.path.dirname(os.path.realpath(__file__))


class ConfigUtil:
    config_file = os.path.join(CUR_DIR, 'config.ini')

    def __init__(self) -> None:
        self.config = configparser.RawConfigParser()
        self.config.read(self.config_file)

    def get_proxy_enable_status(self):
        return self.config.getboolean('proxy', 'enable')

    def get_proxy_verify(self):
        return self.config.getboolean('proxy', 'verify')

    def get_proxy_hostname(self):
        return self.config.get('proxy', 'hostname')

    def get_proxy_protocol(self):
        return self.config.get('proxy', 'protocol')

    def get_proxy_port(self):
        return self.config.get('proxy', 'port')

    def get_proxy_username(self):
        return self.config.get('proxy', 'username')

    def get_proxy_user_password(self):
        return self.config.get('proxy', 'userpassword')

    def get_download_os_list(self):
        return [x.strip() for x in
                self.config.get('download', 'os_list').split(',')]

    def get_download_arch_list(self):
        return [x.strip() for x in
                self.config.get('download', 'arch_list').split(',')]


CONFIG_INST = ConfigUtil()


class ProxyUtil:
    def __init__(self) -> None:
        self.enable = CONFIG_INST.get_proxy_enable_status()
        self.verify = CONFIG_INST.get_proxy_verify()
        self.protocol = CONFIG_INST.get_proxy_protocol()
        self.hostname = CONFIG_INST.get_proxy_hostname()
        self.port = CONFIG_INST.get_proxy_port()
        self.username = CONFIG_INST.get_proxy_username()
        self.user_password = parse.quote(
            CONFIG_INST.get_proxy_user_password().encode('utf-8'))
        self.proxy_handler = self._init_proxy_handler()

    def _init_proxy_handler(self):
        if not self.verify:
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
        if 'http' in self.protocol:
            proxy_suffix = f'{self.username}:{self.user_password}' \
                           f'@{self.hostname}:{self.port}'
            proxy_option = {
                'http': f'http://{proxy_suffix}',
                'https': f'https://{proxy_suffix}'
            }
            return request.ProxyHandler(proxy_option)
        else:
            print(f'protocol[{self.protocol}] is invalid!')

    def build_proxy_handler(self):
        if self.enable:
            opener = request.build_opener(self.proxy_handler)
            request.install_opener(opener)
        else:
            print('proxy is disabled')


class DownloadUtil:
    proxy_inst = ProxyUtil()

    @classmethod
    def download(cls, url: str, dst_file_name: str):
        parent_dir = os.path.dirname(dst_file_name)
        if not os.path.exists(parent_dir):
            print("mkdir : {0}".format(parent_dir))
            os.makedirs(parent_dir)
        res = cls.download_with_retry(url, dst_file_name)
        if not res:
            print(f'download {url} failed')
        else:
            print(f'download {url} successfully')

    @classmethod
    def download_with_retry(cls, url: str, dst_file_name: str, retry_times=5):
        for retry in [ x + 1 for x in range(retry_times)]:
            try:
                print(f'downloading try: {retry} from {url}')
                cls.delete_if_exist(dst_file_name)
                cls.proxy_inst.build_proxy_handler()
                local_file, _ = request.urlretrieve(url, dst_file_name)
                if os.path.exists(local_file):
                    print('download successfully')
                return True
            except ContentTooShortError as ex:
                print(ex)
            except URLError as err:
                print(err)
            except socket.timeout as timeout:
                socket.setdefaulttimeout(retry * 60)
                print(timeout)
        return False

    @classmethod
    def urlopen(cls, url: str, retry_times=5):
        for retry in [ x + 1 for x in range(retry_times)]:
            try:
                cls.proxy_inst.build_proxy_handler()
                resp = request.urlopen(url)
                return resp
            except ContentTooShortError as ex:
                print(ex)
            except URLError as err:
                print(err)
            except socket.timeout as timeout:
                socket.setdefaulttimeout(retry * 60)
                print(timeout)
        return None

    @staticmethod
    def delete_if_exist(dst_file_name: str):
        if os.path.exists(dst_file_name):
            print(f'{dst_file_name} already exists')
            os.remove(dst_file_name)
            print(f'{dst_file_name} already deleted')


DOWNLOAD_INST = DownloadUtil()
