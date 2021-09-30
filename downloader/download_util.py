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
import json
import socket
import time
import sys
import hashlib
import ssl
import platform
import logger_config

from urllib import request
from urllib import parse
from urllib.error import ContentTooShortError, URLError


def get_ascend_path():
    """
    get download path
    """
    cur_dir = os.path.dirname(__file__)
    if 'site-packages' not in cur_dir and 'dist-packages' not in cur_dir:
        cur = os.path.dirname(cur_dir)
        return cur

    deployer_home = ''
    if platform.system() == 'Linux':
        deployer_home = os.getenv('HOME')
        if os.getenv('ASCEND_DEPLOYER_HOME') is not None:
            deployer_home = os.getenv('ASCEND_DEPLOYER_HOME')
    else:
        deployer_home = os.getcwd()

    return os.path.join(deployer_home, 'ascend-deployer')


LOG = logger_config.LOG
CUR_DIR = get_ascend_path()
ROOT_DIR = os.path.dirname(CUR_DIR)


def get_support_url():
    """
    get support url
    """
    resources_json = os.path.join(CUR_DIR, 'downloader', 'support_url.json')
    with open(resources_json, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data

class ConfigUtil:
    config_file = os.path.join(CUR_DIR, 'downloader/config.ini')

    def __init__(self) -> None:
        self.config = configparser.RawConfigParser()
        self.config.read(self.config_file)

    def get_pypi_url(self):
        return self.config.get('pypi', 'index_url')

    def get_proxy_verify(self):
        return self.config.getboolean('proxy', 'verify')

    def get_download_os_list(self):
        os_list = self.config.get('download', 'os_list')
        return [x.strip() for x in os_list.split(',') if len(x.strip()) != 0]

    def get_download_pkg_list(self):
        pkg_list = self.config.get('software', 'pkg_list')
        return [x.strip() for x in pkg_list.split(',') if len(x.strip()) != 0]

    def get_python_version(self):
        return self.config.get('python', 'ascend_python_version')

CONFIG_INST = ConfigUtil()


class ProxyUtil:
    def __init__(self) -> None:
        self.verify = CONFIG_INST.get_proxy_verify()
        self.proxy_handler = self._init_proxy_handler()
        self.https_handler = self._init_https_handler()

    def _init_proxy_handler(self):
        return request.ProxyHandler()


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


def schedule(blocknum, blocksize, totalsize):
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
            print(url.ljust(60), 'download failed')
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
                delete_if_exist(dst_file_name)
                cls.proxy_inst.build_proxy_handler()
                DownloadUtil.start_time = time.time()
                print("start downloading {}".format(url.split('/')[-1].split('#')[0]))
                local_file, _ = request.urlretrieve(url, dst_file_name, schedule)
                sys.stdout.write('\n')
                return is_exists(local_file)
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
            finally:
                pass
            print('please wait for a moment...')
            LOG.info('please wait for a moment...')
            time.sleep(retry * 2)
        return False

    @classmethod
    def urlopen(cls, url: str, retry_times=5):
        for retry in [x + 1 for x in range(retry_times)]:
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
            finally:
                pass
            print('please wait for a moment...')
            LOG.info('please wait for a moment...')
            time.sleep(retry * 2)

    @classmethod
    def download_to_tmp(cls, url: str, retry_times=5):
        for retry in [x + 1 for x in range(retry_times)]:
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
            finally:
                pass
            print('please wait for a moment...')
            LOG.info('please wait for a moment...')
            time.sleep(retry * 2)


class Cann_Download:
    browser = None

    def __init__(self):
        self.download_dir = None

    @classmethod
    def quit(cls):
        if cls.browser:
            cls.browser.quit()
            cls.browser = None

    def download(self, url: str, dst_file_name: str):
        file_name = os.path.basename(dst_file_name)

        try:
            import selenium
        except ImportError:
            print("[ERROR] import selenium error, please install selenium first")
            print(file_name.ljust(60), 'download failed')
            LOG.error('import selenium error, download %s failed', file_name)
            return False

        try:
            res = self.download_with_selenium(url, dst_file_name)
        except selenium.common.exceptions.WebDriverException as err:
            print("[ERROR] some problem has occured when runing selenium")
            LOG.error('selenium.common.exceptions.WebDriverException: %s', err)
            res = False

        if not res:
            print(file_name.ljust(60), 'download failed')
            LOG.error('download %s failed', file_name)
            return False
        else:
            LOG.info('download %s successfully', file_name)
            return True

    def get_firefox_driver(self):
        import selenium
        from selenium import webdriver

        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.helperApps.alwaysAsk.force", False)
        fp.set_preference("browser.download.manager.showAlertOnComplete", True)
        fp.set_preference('browser.helperApps.neverAsk.saveToDisk',
                          'application/zip,application/octet-stream,'
                          'application/x-zip-compressed,multipart/x-zip,'
                          'application/x-rar-com'
                          'pressed, application/octet-stream')
        fp.set_preference("browser.download.dir", self.download_dir)
        if platform.system() == 'Linux':
            driver_path = os.path.join(ROOT_DIR, 'geckodriver')
            if not os.path.exists(driver_path):
                print("[ERROR] {} not exists, please check the file".format(driver_path))
                LOG.error("{} not exists, please check the file".format(driver_path))
                raise FileNotFoundError
            try:
                os.chmod(driver_path, mode=0o500)
            except PermissionError as err:
                print("[ERROR] {} no permission to be chmod to 500, please chown the file to the current user".format(driver_path))
                LOG.error("{} no permission to be chmod to 500, please chown the file to the current user: {}".format(driver_path, err))
                raise PermissionError
            try:
                browser = webdriver.Firefox(firefox_profile=fp,
                                            port=56003,
                                            service_args=['--marionette-port',
                                                          '56004'],
                                            service_log_path='/dev/null',
                                            executable_path=driver_path)
            except selenium.common.exceptions.SessionNotCreatedException as err:
                print("[ERROR] firefox or geckodriver is not available, please check")
                LOG.error("firefox or geckodriver is not available: %s", err)
                raise
        else:
            driver_path = os.path.join(ROOT_DIR, 'geckodriver.exe')
            if not os.path.exists(driver_path):
                print("[ERROR] {} not exists, please check the file".format(driver_path))
                LOG.error("{} not exists, please check the file".format(driver_path))
                raise FileNotFoundError
            try:
                browser = webdriver.Firefox(firefox_profile=fp,
                                            service_log_path='NUL',
                                            executable_path=driver_path)
            except selenium.common.exceptions.SessionNotCreatedException as err:
                print("[ERROR] firefox or geckodriver is not available, please check")
                LOG.error("firefox or geckodriver is not available: %s", err)
                raise
        return browser

    def login(self):
        login_url = get_support_url().get('login_url')
        Cann_Download.browser = self.get_firefox_driver()
        self.browser.get(login_url)
        count = 0
        while Cann_Download.browser.current_url != \
                get_support_url().get('support_site'):
            count += 1
            if count > 300:
                print("[ERROR] login timeout or not logged in, please try again")
                LOG.error("login timeout or not logged in")
                raise ConnectionRefusedError()
            time.sleep(1)

    def download_with_selenium(self, url: str, dst_file_name: str):
        from selenium import webdriver

        file_name = os.path.basename(dst_file_name)
        self.download_dir = os.path.dirname(dst_file_name)

        if self.browser is None:
            try:
                self.login()
            except (ConnectionRefusedError, FileNotFoundError, PermissionError):
                LOG.error('download %s failed', file_name)
                return False

        delete_if_exist(dst_file_name)
        delete_if_exist(dst_file_name + '.asc')
        print("start downloading {}".format(file_name))

        self.browser.get(url)
        webdriver.support.wait.WebDriverWait(self.browser, 30).until(
            lambda _driver:
            _driver.find_element_by_partial_link_text('直接下载'))
        self.browser.find_element_by_partial_link_text('直接下载').click()
        self.wait_download_complete(file_name)
        if get_support_url().get('apply_right') in \
                self.browser.current_url:
            print("[ERROR] no permission to download, please apply for permission first")
            LOG.error('no permission to download, download %s failed', file_name)
            return False
        self.browser.find_element_by_partial_link_text('pgp').click()
        self.wait_download_complete(file_name + '.asc')

        return is_exists(dst_file_name) and is_exists(dst_file_name + '.asc')

    def wait_download_complete(self, file_name):
        while file_name + '.part' in \
                [_file_name for _file_name in os.listdir(self.download_dir)]:
            time.sleep(1)


DOWNLOAD_INST = DownloadUtil()
CANN_DOWNLOAD_INST = Cann_Download()


def calc_sha256(file_path):
    hash_val = None
    if file_path is None or not os.path.exists(file_path):
        return hash_val
    with open(file_path, 'rb') as hash_file:
        sha256_obj = hashlib.sha256()
        sha256_obj.update(hash_file.read())
        hash_val = sha256_obj.hexdigest()
    return hash_val

def get_specified_python():
    if os.environ.get("ASCEND_PYTHON_VERSION"):
        specified_python = os.environ.get("ASCEND_PYTHON_VERSION")
    else:
        specified_python = CONFIG_INST.get_python_version()
    resources_json = os.path.join(CUR_DIR, 'downloader', 'python_version.json')
    with open(resources_json, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        available_python_list = [item['filename'].rstrip('.tar.xz') for item in data]
        if specified_python not in available_python_list:
            tips = "[ERROR] ascend_python_version is not available, available Python-x.x.x is in 3.7.0~3.7.11 and 3.8.0~3.8.11"
            print(tips)
            LOG.error(tips)
            sys.exit(1)
    return specified_python

def delete_if_exist(dst_file_name: str):
    if os.path.exists(dst_file_name):
        LOG.info('{} already exists'.format(dst_file_name))
        os.remove(dst_file_name)
        LOG.info('{} already deleted'.format(dst_file_name))

def is_exists(dst_file_name: str):
    if os.path.exists(dst_file_name):
        LOG.info('{} exists after downloading, success'.format(dst_file_name))
        return True
    else:
        print('[ERROR] {} not exists after downloading, failed'.format(dst_file_name))
        LOG.info('{} not exists after downloading, failed'.format(dst_file_name))
        return False
