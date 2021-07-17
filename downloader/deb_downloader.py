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
import sys
import gzip
import re
import sqlite3 as sqlite
import urllib.request
import configparser
from urllib.error import HTTPError
from downloader import get_download_path
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

LOG = get_logger(__file__)


class DebianSource(object):
    """
    source
    """
    def __init__(self, line):
        tmp = line.split(' ')
        self.url = tmp[1].strip()
        self.distro = tmp[2].strip()
        self.repoList = [i.strip() for i in tmp[3:]]

    def get_url(self):
        """
        get source url
        """
        return self.url

    def repos(self):
        """
        get source repos
        """
        repos = {}
        for repo in self.repoList:
            repo_url = "{0}dists/{1}/{2}".format(self.url, self.distro, repo)
            yield repo, repo_url


class Package(object):
    """
    Package
    """
    def __init__(self, package, filename, sha256=None):
        self.package = package
        self.filename = filename
        self.sha256 = sha256

    def get_packagename(self):
        """
        get_packagename
        """
        return self.package

    def get_filename(self):
        """
        get_filename
        """
        return self.filename

    def get_sha256(self):
        """
        get_sha256
        """
        return self.sha256


class Apt(object):
    """
    downloader for apt
    """
    def __init__(self, source_file, arch):
        self.arch = arch
        self.binary_path = 'binary-amd64' \
            if 'x86' in self.arch else 'binary-arm64'
        # 读取源配置
        self.source_list = []
        self.base_dir = get_download_path()
        self.repo_file = os.path.join(self.base_dir, source_file)
        self.resources_dir = os.path.join(self.base_dir, 'resources')
        with open(self.repo_file) as file:
            for line in file.readlines():
                source = DebianSource(line)
                self.source_list.append(source)

    def make_cache(self):
        """
        make_cache
        """
        self.primary_connection = sqlite.Connection(':memory:')
        self.primary_cur = self.primary_connection.cursor()
        try:
            self.primary_cur.executescript("CREATE TABLE packages \
                    (name TEXT, version TEXT, source TEXT, repo TEXT, \
                    url TEXT, sha256 TEXT);")
        except sqlite.OperationalError as e:
            pass
        finally:
            pass

        for source in self.source_list:
            for repo, url in source.repos():
                index_url = '{0}/{1}/Packages.gz'.format(url, self.binary_path)
                LOG.info('packages_url=[%s]', index_url)
                packages = self.fetch_package_index(index_url)
                self.make_cache_from_packages(source.get_url(), repo, packages)
        self.primary_connection.commit()
        self.primary_cur.close()

    def clean_cache(self):
        """
        clean sqlite Connection
        """
        self.primary_connection.close()

    @staticmethod
    def fetch_package_index(packages_url):
        """
        fetch_package_index

        :param packages_url:
        :return:
        """
        tmp_file = DOWNLOAD_INST.download_to_tmp(packages_url)
        with gzip.open(tmp_file) as resp:
            html = resp.read()
        os.unlink(tmp_file)
        return html.decode('utf-8')

    @staticmethod
    def version_compare(ver_a, ver_b):
        """
        version_compare

        :param ver_a:
        :param ver_b:
        :return:
        """
        ver_a_list = str(ver_a).split(".")
        ver_b_list = str(ver_b).split(".")
        for i in range(len(ver_a_list)) if len(ver_a_list) < len(ver_b_list) else range(len(ver_b_list)):
            ver_a_list[i] = re.sub(r'\D', '', ver_a_list[i])
            ver_b_list[i] = re.sub(r'\D', '', ver_b_list[i])
            try:
                ver_a_list[i] = int(ver_a_list[i])
                ver_b_list[i] = int(ver_b_list[i])
            except ValueError:
                ver_a_list[i] = str(ver_a_list[i])
                ver_b_list[i] = str(ver_b_list[i])
            finally:
                pass
            if ver_a_list[i] == ver_b_list[i]:
                continue
            else:
                return ver_a_list[i] > ver_b_list[i]
        return len(ver_a) > len(ver_b)

    def make_cache_from_packages(self, source_url, repo, packages_content):
        """
        make_cache_from_packages

        :param packages_content:
        :return:
        """

        lines = packages_content.split('\n')
        package = ''
        version = ''
        filename = ''
        sha256 = None
        for line in lines:
            if line.startswith("Package:"):
                package = line.split(': ')[1]

            if line.startswith("Version:"):
                version = line.split(': ')[1]

            if line.startswith("SHA256:"):
                sha256 = line.split(': ')[1]

            if line.startswith("Filename:"):
                filename = line.split(': ')[1]

            if len(line.strip()) == 0:
                params = {'name': package,
                    'version': version,
                    'source': source_url,
                    'repo': repo,
                    'url': filename,
                    'sha256': sha256}
                self.primary_cur.execute("INSERT INTO \
                        PACKAGES (name, version, source, repo, url, sha256) \
                        VALUES (:name, :version, :source, :repo, :url, \
                        :sha256);", params)

    def download_by_url(self, pkg, dst_dir):
        """
        download_by_url
        :param pkg:  package information
        :return:
        """
        download_dir = dst_dir
        if 'dst_dir' in pkg:
            download_dir = os.path.join(os.path.dirname(dst_dir), pkg['dst_dir'])
            if not os.path.exists(download_dir):
                os.makedirs(download_dir, mode=0o750, exist_ok=True)

        url = pkg['url']
        file_name = os.path.basename(url)
        dst_file = os.path.join(download_dir, file_name)

        checksum = pkg['sha256'] if 'sha256' in pkg else None
        if checksum and not self.need_download_again(checksum, dst_file):
            print(file_name.ljust(60), 'exists')
            return True

        try:
            LOG.info('download from [%s]', url)
            return DOWNLOAD_INST.download(url, dst_file)
        except HTTPError as http_error:
            print('[{0}]->{1}'.format(url, http_error))
            LOG.error('[%s]->[%s]', url, http_error)
            return False
        finally:
            pass

    def download_by_name(self, pkg, dst_dir):
        """
        download

        :param name:
        :param dst_dir:
        :return:
        """
        if 'name' not in pkg:
            return False
        if 'dst_dir' in pkg:
            dst_dir = os.path.join(dst_dir, pkg['dst_dir'])

        url = None
        name = pkg['name']
        cur = self.primary_connection.cursor()
        sql = 'SELECT packages.version, packages.url, packages.sha256, \
                packages.source, packages.repo \
                FROM packages \
                WHERE name=:name ORDER by packages.version;'
        param = {'name': name}
        cur.execute(sql, param)
        results = cur.fetchall()
        cur.close()

        if len(results) == 0:
            print("can't find package {0}".format(name))
            LOG.error("can't find package %s", name)
            return False

        pkg_sha256 = ''
        version = results[0][0]
        url = results[0][3] + results[0][1]
        pkg_sha256 =  results[0][2]
        for item in results:
            [cur_ver, cur_url, cur_sha256, cur_source, cur_repo] = item
            if not self.version_compare(version, cur_ver):
                version = cur_ver
                url =  cur_source + cur_url
                pkg_sha256 =  cur_sha256
            if 'version' in pkg and pkg['version'] in cur_ver:
                url =  cur_source + cur_url
                pkg_sha256 =  cur_sha256
                break

        try:
            LOG.info('[%s] download from [%s]', name, url)
            file_name = os.path.basename(url)
            dst_file = os.path.join(dst_dir, file_name)
            if not self.need_download_again(pkg_sha256, dst_file):
                LOG.info("%s no need download again", name)
                print(name.ljust(60), 'exists')
                return True
            if DOWNLOAD_INST.download(url, dst_file):
                print(name.ljust(60), 'download success')
                return True
            print(name.ljust(60), 'download failed')
            return False
        except HTTPError as http_error:
            print('[{0}]->{1}'.format(url, http_error))
            LOG.error('[%s]->[%s]', url, http_error)
            return False
        finally:
            pass

    def download(self, pkg, dst_dir):
        """
        download
        """
        if 'url' in pkg:
            return self.download_by_url(pkg, dst_dir)
        else:
            return self.download_by_name(pkg, dst_dir)

    @staticmethod
    def need_download_again(target_sha256, dst_file):
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
            LOG.info('target sha256 : %s, existed file sha256 : %s',
                     target_sha256, file_sha256)
            print('target sha256 : {}, existed file sha256 : {}'.format(
                target_sha256, file_sha256))
            return True
        else:
            return False
