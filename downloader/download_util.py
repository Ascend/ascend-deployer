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
import time
import hashlib
from urllib import request
from urllib import parse
from urllib.error import ContentTooShortError, URLError
from logger_config import get_logger

LOG = get_logger(__file__)
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

    def get_download_delete_exists(self):
        return self.config.getboolean('download', 'delete_exists')


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
            print('protocol[{}] is invalid!'.format(self.protocol))
            LOG.error('protocol[{}] is invalid!'.format(self.protocol))

    def build_proxy_handler(self):
        if self.enable:
            opener = request.build_opener(self.proxy_handler)
            request.install_opener(opener)
        else:
            print('proxy is disabled')
            LOG.info('proxy is disabled')


class DownloadUtil:
    proxy_inst = ProxyUtil()

    @classmethod
    def download(cls, url: str, dst_file_name: str):
        parent_dir = os.path.dirname(dst_file_name)
        if not os.path.exists(parent_dir):
            print("mkdir : {0}".format(parent_dir))
            LOG.info("mkdir : {0}".format(parent_dir))
            os.makedirs(parent_dir)
        res = cls.download_with_retry(url, dst_file_name)
        if not res:
            print('download {} failed'.format(url))
            LOG.error('download {} failed'.format(url))
        else:
            print('download {} successfully'.format(url))
            LOG.info('download {} successfully'.format(url))

    @classmethod
    def download_with_retry(cls, url: str, dst_file_name: str, retry_times=5):
        for retry in range(1, retry_times + 1):
            try:
                print('downloading try: {} from {}'.format(retry, url))
                LOG.info('downloading try: {} from {}'.format(retry, url))
                if not cls.check_download_necessary(dst_file_name):
                    print('no need download again')
                    LOG.info('no need download again')
                    return True
                cls.delete_if_exist(dst_file_name)
                cls.proxy_inst.build_proxy_handler()
                local_file, _ = request.urlretrieve(url, dst_file_name)
                if os.path.exists(local_file):
                    print('download successfully')
                    LOG.info('download successfully')
                return True
            except ContentTooShortError as ex:
                print(ex)
                LOG.error(ex)
            except URLError as err:
                print(err)
                LOG.error(err)
            except socket.timeout as timeout:
                socket.setdefaulttimeout(retry * 60)
                print(timeout)
                LOG.error(timeout)
            print('please wait for a moment...')
            LOG.info('please wait for a moment...')
            time.sleep(retry * 2)
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
                LOG.error(ex)
            except URLError as err:
                print(err)
                LOG.error(err)
            except socket.timeout as timeout:
                socket.setdefaulttimeout(retry * 60)
                print(timeout)
                LOG.error(timeout)
            print('please wait for a moment...')
            LOG.info('please wait for a moment...')
            time.sleep(retry * 2)
        return None

    @classmethod
    def check_download_necessary(cls, dst_file_name):
        if not os.path.exists(dst_file_name):
            return True
        return CONFIG_INST.get_download_delete_exists()

    @staticmethod
    def delete_if_exist(dst_file_name: str):
        if os.path.exists(dst_file_name):
            print('{} already exists'.format(dst_file_name))
            LOG.info('{} already exists'.format(dst_file_name))
            os.remove(dst_file_name)
            print('{} already deleted'.format(dst_file_name))
            LOG.info('{} already deleted'.format(dst_file_name))


DOWNLOAD_INST = DownloadUtil()


def calc_sha256(file):
    hash_val = None
    if file is None or not os.path.exists(file):
        return hash_val
    with open(file, 'rb') as hash_file:
        sha256_obj = hashlib.sha256()
        sha256_obj.update(hash_file.read())
        hash_val = sha256_obj.hexdigest()
    return hash_val

