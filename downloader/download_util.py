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
import sys
import hashlib
import ssl
import json
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
        os_list = os.getenv('DOWNLOAD_OS_LIST')
        if os_list is None:
            os_list = self.config.get('download', 'os_list')
        return [x.strip() for x in os_list.split(',') if len(x.strip()) != 0]

    def get_download_pkg_list(self):
        pkg_list = os.getenv('DOWNLOAD_PKG_LIST')
        if pkg_list is None:
            pkg_list = self.config.get('software', 'pkg_list')
        return [x.strip() for x in pkg_list.split(',') if len(x.strip()) != 0]

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
        self.https_handler = self._init_https_handler()

    def _init_proxy_handler(self):
        if not self.enable:
            LOG.info('use system proxy settings')
            return request.ProxyHandler()
        if 'http' in self.protocol:
            if os.environ.get("http_proxy") and os.environ.get("https_proxy"):
                proxy_option = {
                    'http': os.environ.get("http_proxy"),
                    'https': os.environ.get("https_proxy")
                }
            else:
                proxy_suffix = '{}:{}@{}:{}'.format(
                    self.username, self.user_password,
                    self.hostname, self.port
                    )
                proxy_option = {
                    'http': 'http://{}'.format(proxy_suffix),
                    'https': 'https://{}'.format(proxy_suffix)
                }
            return request.ProxyHandler(proxy_option)
        else:
            print('protocol[{}] is invalid!'.format(self.protocol))
            LOG.error('protocol[%s] is invalid!', self.protocol)

    def _init_https_handler(self):
        if not self.verify:
            context = self.create_unverified_context()
        else:
            context = ssl.create_default_context()
        return request.HTTPSHandler(context=context)

    def build_proxy_handler(self):
        opener = request.build_opener(self.proxy_handler,
                                      self.https_handler)
        request.install_opener(opener)

    @staticmethod
    def create_unverified_context():
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_NONE
        context.check_hostname = False
        return context


def Schedule(blocknum, blocksize, totalsize):
    speed = (blocknum * blocksize) / (time.time() - DownloadUtil.start_time)
    speed = float(speed) / 1024
    speed_str = r" {:.2f} KB/s".format(speed)
    if speed >= 1024:
        speed_str = r" {:.2f} MB/s".format(speed / 1024)
    recv_size = blocknum * blocksize
    # config scheduler
    f = sys.stdout
    pervent = recv_size / totalsize
    if pervent > 1:
        pervent = 1
    percent_str = "{:.2f}%".format(pervent * 100)
    n = round(pervent * 50)
    s = ('=' * (n - 1) + '>').ljust(50, '-')
    if pervent == 1:
        s = ('=' * n).ljust(50, '-')
    f.write('\r' + percent_str.ljust(7, ' ') + '[' + s + ']' + speed_str.ljust(20))
    f.flush()


class DownloadUtil:
    proxy_inst = ProxyUtil()
    start_time = time.time()

    @classmethod
    def download(cls, url: str, dst_file_name: str):
        parent_dir = os.path.dirname(dst_file_name)
        if not os.path.exists(parent_dir):
            LOG.info("mkdir : %s", parent_dir)
            os.makedirs(parent_dir, mode=0o750, exist_ok=True)

        res = cls.download_with_retry(url, dst_file_name)
        if not res:
            print('download {} failed'.format(url))
            LOG.error('download %s failed', url)
            return False
        else:
            LOG.info('download %s successfully', url)
            return True

    @classmethod
    def download_with_retry(cls, url: str, dst_file_name: str, retry_times=5):
        for retry in range(1, retry_times + 1):
            try:
                LOG.info('downloading try: %s from %s', retry, url)
                cls.delete_if_exist(dst_file_name)
                cls.proxy_inst.build_proxy_handler()
                DownloadUtil.start_time = time.time()
                print("downloading {}".format(dst_file_name.split('/')[-1]))
                local_file, _ = request.urlretrieve(url, dst_file_name, Schedule)
                sys.stdout.write('\n')
                if os.path.exists(local_file):
                    LOG.info('%s download successfully', url)
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
            except ConnectionResetError as rest:
                print('connection reset by peer, retry...')

            print('please wait for a moment...')
            LOG.info('please wait for a moment...')
            time.sleep(retry * 2)
        return False

    @classmethod
    def download_no_retry(cls, url: str, dst_file_name: str):
        try:
            LOG.info('downloading from %s', url)
            cls.proxy_inst.build_proxy_handler()
            DownloadUtil.start_time = time.time()
            print("downloading {}".format(dst_file_name.split('/')[-1]))
            local_file, _ = request.urlretrieve(url, dst_file_name, Schedule)
            sys.stdout.write('\n')
            return True
        except ContentTooShortError as ex:
            LOG.error(ex)
        except URLError as err:
            LOG.error(err)
        except socket.timeout as timeout:
            LOG.error(timeout)
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
    def download_to_tmp(cls, url: str, retry_times=5):
        for retry in [ x + 1 for x in range(retry_times)]:
            try:
                cls.proxy_inst.build_proxy_handler()
                tmp_file, _ = request.urlretrieve(url)
                return tmp_file
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
        return False

    @staticmethod
    def delete_if_exist(dst_file_name: str):
        if os.path.exists(dst_file_name):
            LOG.info('%s already exists', dst_file_name)
            os.remove(dst_file_name)
            LOG.info('%s already deleted', dst_file_name)


DOWNLOAD_INST = DownloadUtil()


def calc_sha256(file_path):
    hash_val = None
    if file_path is None or not os.path.exists(file_path):
        return hash_val
    with open(file_path, 'rb') as hash_file:
        sha256_obj = hashlib.sha256()
        sha256_obj.update(hash_file.read())
        hash_val = sha256_obj.hexdigest()
    return hash_val

def calc_md5(file_path):
    hash_val = None
    if file_path is None or not os.path.exists(file_path):
        return hash_val
    with open(file_path, 'rb') as hash_file:
        md5_obj = hashlib.md5()
        md5_obj.update(hash_file.read())
        hash_val = md5_obj.hexdigest()
    return hash_val
