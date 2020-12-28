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
import bz2
import sqlite3
import lzma
import xml.sax

import logger_config
from xml.dom import minidom
from urllib.error import HTTPError
from download_util import DOWNLOAD_INST
from download_util import calc_sha256
from yum_metadata.gen_yum_metadata import YumMetadataSqlite
from yum_metadata.gen_yum_metadata import YumPackageHandler
from yum_metadata.gen_yum_metadata import Require
from yum_metadata.gen_yum_metadata import Provide
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin


LOG = logger_config.get_logger(__file__)

class Package(object):
    """
    rpm package
    """
    def __init__(self, name):
        self.name = name
        self.repo_url = None
        self.href = None
        self.version = None
        self.release = None
        self.checksum = None

    def get_url(self):
        """
        get_url

        :return: url of the package
        """
        return self.repo_url + '/' + self.href


class Yum(object):
    """
    downloader for yum
    """
    def __init__(self, source_file, arch):
        self.arch = arch
        self.cache = {}
        self.installed = {}
        self.downloaded = []
        self.to_be_download = {}
        # 读取源配置
        script = os.path.realpath(__file__)
        self.base_dir = os.path.dirname(os.path.dirname(script))
        self.repo_file = os.path.join(self.base_dir, source_file)
        config = configparser.ConfigParser()
        config.read(self.repo_file)


        self.cache_dir = os.path.join(self.base_dir,
                                      os.path.dirname(source_file))
        self.installed_file = os.path.join(self.cache_dir, 'installed.txt')
        print('repofile={} cache={}'.format(self.repo_file, self.cache_dir))
        LOG.info('repofile={} cache={}'.format(self.repo_file, self.cache_dir))
        self.sources = {}
        for item in config.keys():
            if 'DEFAULT' == item:
                continue
            self.sources[item] = config.get(item, 'baseurl')
            print(config.get(item, 'baseurl'))
            LOG.info(config.get(item, 'baseurl'))

        if os.path.exists(self.installed_file):
            self.load_installed(self.installed_file)

    def load_installed(self, file_name):
        with open(file_name) as f:
            for item in f.readlines():
                info = [tmp for tmp in item.split(' ') if len(tmp) > 1]
                [name_and_arch, version, repo] = info
                [item_name, item_arch] = name_and_arch.split('.')
                self.installed[item_name] = {'name': item_name, 'arch': item_arch, 'version': version}

    def build_primary_cache(self, primary_xml_file, cache_dir, source_name):
        if primary_xml_file.endswith('.gz'):
            xml_file = primary_xml_file.rstrip('.gz')
            self.uncompress_file(primary_xml_file, xml_file)
        else:
            xml_file = primary_xml_file

        db_file_name = source_name + '_primary.sqlite'
        yum_meta_sqlite = YumMetadataSqlite(cache_dir, db_file_name)
        yum_meta_sqlite.create_primary_db()

        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        handler = YumPackageHandler()
        parser.setContentHandler(handler)
        parser.parse(xml_file)

        for pkgKey, pkg in enumerate(handler.packages):
            pkg.dump_to_primary_sqlite(pkgKey + 1, yum_meta_sqlite.primary_cur)
        yum_meta_sqlite.primary_connection.commit()

    def make_cache(self):
        """
        make_cache

        :return:
        """
        for name, url in self.sources.items():
            repomd_url = urljoin(url if url.endswith('/') else url + '/', 'repodata/repomd.xml')
            print('{0}:{1}'.format(name, repomd_url))
            LOG.info('{0}:{1}'.format(name, repomd_url))
            repomd_xml = name + '_repomd.xml'
            repomd_file = os.path.join(self.cache_dir, repomd_xml)
            db_file = os.path.join(self.cache_dir, name + '_primary.sqlite')

            if os.path.exists(repomd_file):
                os.remove(repomd_file)
            # 下载repomd.xml文件
            self.download_file(repomd_url, repomd_file)

            # 解析repomod.xml文件，得到数据库文件的url
            db_location_href = self.parse_repomd(repomd_file, 'primary_db')
            if not db_location_href:
                msg = "%s db_url is not exist, begin to build db." % name
                print(msg)
                LOG.warning(msg)
                primary_xml_location_href = self.parse_repomd(repomd_file,
                                                              'primary')
                primary_xml_url = urljoin(url, primary_xml_location_href)
                primary_xml_file_name = os.path.basename(primary_xml_url).split('-')[-1]
                primary_xml_file = os.path.join(self.cache_dir, name + '_' + primary_xml_file_name)
                self.download_file(primary_xml_url, primary_xml_file)
                self.build_primary_cache(primary_xml_file, self.cache_dir, name)
                continue

            db_url = url + '/' + db_location_href
            url_file_name = os.path.basename(db_url).split('-')[1]
            compressed_file = os.path.join(self.cache_dir,
                                           name + '_' + url_file_name)
            print('dburl=[{0}]'.format(db_url))
            LOG.info('dburl=[{0}]'.format(db_url))

            if os.path.exists(compressed_file):
                os.remove(compressed_file)
            # 下载数据库文件
            self.download_file(db_url, compressed_file)

            if os.path.exists(db_file):
                os.remove(db_file)
            # 解压数据库文件
            self.uncompress_file(compressed_file, db_file)

    def uncompress_file(self, compress_file, dst_file):
        """
        解压文件
        """
        if os.path.exists(dst_file):
            return

        if compress_file.endswith('.gz'):
            with gzip.GzipFile(compress_file) as gzip_file:
                buf = gzip_file.read()
                with open(dst_file, 'wb') as uncompress_file:
                    uncompress_file.write(buf)
            return

        if 'bz2' in compress_file:
            with bz2.BZ2File(compress_file, 'rb') as bz_file:
                buf = bz_file.read()
                with open(dst_file, 'wb+') as uncompress_file:
                    uncompress_file.write(buf)
        if 'xz' in compress_file:
            with lzma.open(compress_file, 'rb') as xz_file:
                buf = xz_file.read()
                with open(dst_file, 'wb+') as uncompress_file:
                    uncompress_file.write(buf)

    def parse_repomd(self, file_name, data_type):
        """
        解析repomd.xml文件，得到data_type, 如primary_db url
        """
        dom = minidom.parse(file_name)
        data_elements = dom.getElementsByTagName('data')
        for i in data_elements:
            if i.getAttribute('type') != data_type:
                continue
            location = i.getElementsByTagName('location')[0]
            print(location.getAttribute('href'))
            LOG.info(location.getAttribute('href'))
            return location.getAttribute('href')

    def download_file(self, url, dst_file):
        """
        download_file

        :param url:
        :param dst_file:
        :return:
        """
        try:
            LOG.info('download from [{0}]'.format(url))
            DOWNLOAD_INST.download(url, dst_file)
        except HTTPError as http_error:
            print('[{0}]->{1}'.format(url, http_error))
            LOG.error('[{0}]->{1}'.format(url, http_error))

    def get_requires(self, conn, pkg_name):
        """
        get the requires of the package pkg_name

        :param conn: database connecton
        :param pkg_name: package name
        :returns: requite list
        """
        require_list = []
        cur = conn.cursor()
        sql_param = {"name": pkg_name, "arch": self.arch}
        cur.execute("SELECT DISTINCT(requires.name), requires.flags, \
                requires.version, requires.release \
                FROM requires \
                JOIN packages ON packages.pkgKey = requires.pkgKey \
                WHERE packages.name = :name \
                AND (packages.arch = :arch or packages.arch = 'noarch')",
                sql_param)
        result = cur.fetchall()
        for item in result:
            require_name = item[0]
            require_flags = item[1]
            require_ver = item[2]
            require_rel = item[3]
            if require_name in ('kernel-devel-uname-r', 'kernel-headers'):
                continue
            req = Require(require_name)
            req.flags = require_flags
            req.version = require_ver
            req.release = require_rel
            require_list.append(req)

        return require_list

    def get_provides(self, provide, repo_name):
        """
        get the provides of the provide
        for example the package bash provides /bin/bash
        get_provides(/bin/bash) returns bash

        :param provide: package name
        :param repo_name: repository name, the repository will serch first
        :returns: provides list
        """
        provide_list = []
        repo_list = [repo_name]
        repo_list += [repo for repo in self.sources.keys() if repo not in repo_list]
        for cur_repo in repo_list:
            repo_url = self.sources[cur_repo]
            db = os.path.join(self.cache_dir, cur_repo + '_primary.sqlite')
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            sql_param = None
            sql = None
            if provide.flags == 'EQ':
                sql_param = {'name': provide.name, 'version': provide.version,
                        'release': provide.release}
                sql = "SELECT packages.name, packages.version, \
                    packages.release FROM packages \
                    JOIN provides ON packages.pkgKey = provides.pkgKey \
                    WHERE provides.name = :name \
                    AND provides.version = :version \
                    AND provides.release = :release"
            else:
                sql_param = {'name': provide.name}
                sql = "SELECT packages.name, packages.version, \
                    packages.release FROM packages \
                    JOIN provides ON packages.pkgKey = provides.pkgKey \
                    WHERE provides.name = :name"
            cur.execute(sql, sql_param)
            result = cur.fetchall()
            if len(result) > 0 and len(result[0]) > 0:
                name = result[0][0]
                ver = result[0][1]
                rel = result[0][2]
                if name not in self.installed.keys():
                    provide_list.append(name)
                elif provide.flags is not None and len(provide.flags) > 0:
                    if '{0}-{1}'.format(ver, rel) != self.installed[name]['version']:
                        provide_list.append(name)
            if len(provide_list) > 0:
                break

        return provide_list

    def get_dependencies(self, conn, pkg_name, repo_name):
        dependencies = []
        require_list = self.get_requires(conn, pkg_name)
        for require in require_list:
            provide_list = self.get_provides(require, repo_name)
            dependencies = list(set(dependencies + provide_list))

        return dependencies

    def search_url(self, repo_url, conn, name, ver, rel):
        sql_str = None
        sql_param = None
        if ver is None or rel is None:
            sql_str = "SELECT location_href FROM packages \
                WHERE name = :name AND (arch = :arch or arch = 'noarch')"
            sql_param = {"name": name, "arch": self.arch}
        else:
            sql_str = "SELECT location_href FROM packages \
                WHERE name = :name AND (arch = :arch or arch = 'noarch') \
                AND version = :version and release = :release"
            sql_param = {"name": name, "arch": self.arch, "version": ver, "release": rel}
        cur = conn.cursor()
        cur.execute(sql_str, sql_param)
        result = cur.fetchall()
        LOG.info(result)
        if len(result) > 0 and len(result[0]) > 0:
            return repo_url + '/' + result[0][0]
        return None

    def search_package(self, conn, name, ver, rel):
        sql_str = None
        sql_param = None
        if ver is None or rel is None:
            sql_str = "SELECT location_href, pkgId, version, release \
                FROM packages \
                WHERE name = :name AND (arch = :arch or arch = 'noarch')"
            sql_param = {"name": name, "arch": self.arch}
        else:
            sql_str = "SELECT location_href, pkgId, version, release \
                FROM packages \
                WHERE name = :name AND (arch = :arch or arch = 'noarch') \
                AND version = :version and release = :release"
            print(type(name))
            sql_param = {"name": name, "arch": self.arch, "version": ver, "release": rel}
        cur = conn.cursor()
        cur.execute(sql_str, sql_param)
        result = cur.fetchall()
        LOG.info(result)
        if len(result) > 0 and len(result[0]) > 0:
            pkg = Package(name)
            pkg.href = result[0][0]
            pkg.checksum = result[0][1]
            pkg.version = result[0][2]
            pkg.release = result[0][3]
            return pkg

        return None

    def get_package(self, name, ver, rel, dep=False):
        """
        get_package

        :param name: package name
        :param ver: pakcage version
        :param rel: pakcage release
        :param dep:  是否获取依赖列表
        :return: 软件包和依赖列表
        """
        require_list = None
        dep_list = None
        pkg = None
        for repo_name, repo_url in self.sources.items():
            db = os.path.join(self.cache_dir, repo_name + '_primary.sqlite')
            conn = sqlite3.connect(db)
            pkg = self.search_package(conn, name, ver, rel)
            if pkg is not None:
                pkg.repo_url = repo_url
                dep_list = self.get_dependencies(conn, name, repo_name) if dep else None
                return pkg, dep_list

        return pkg, dep_list

    def build_to_be_download(self, name, ver, rel):
        """
        build a list of packages to be downloaded
        the list will include all the dependencies

        :param name: package name
        :param ver: package version
        :param rel: package release
        :returns: pakcages to be download
        """
        if name in self.to_be_download.keys():
            return
        pkg, require_list = self.get_package(name, ver, rel, True)
        if pkg is None:
            print(name.ljust(60), "can't find")
            return
        self.to_be_download[name] = pkg
        for require in require_list:
            self.build_to_be_download(require, None, None)

    def download_with_dep(self, name, dst_dir, ver=None, rel=None):
        """
        download package and it's dependencies

        :param name:
        :param dst_dir:
        :param ver: version
        :param rel: release
        :return:
        """
        if name in self.downloaded:
            return
        self.to_be_download = {}
        self.build_to_be_download(name, ver, rel)
        for name, pkg in self.to_be_download.items():
            if name in self.downloaded:
                continue
            file_name = os.path.basename(pkg.get_url())
            dst_file = os.path.join(dst_dir, file_name)
            if not self.need_download_again(pkg.checksum, dst_file):
                print(file_name.ljust(60), 'exists')
                LOG.info('{0} no need download again'.format(file_name))
                self.downloaded.append(name)
                continue
            self.download_file(pkg.get_url(), dst_file)
            self.downloaded.append(name)
            print(file_name.ljust(60), 'download success')

    def download_without_dep(self, name, dst_dir, ver=None, release=None):
        """
        download the package only. not donwload dependencies

        :param name:
        :param dst_dir:
        :param ver:
        :param release:
        :return:
        """
        pkg, _ = self.get_package(name, ver, release)
        if pkg is None:
            print(name.ljust(60), 'can not find')
            LOG.error('can not find {0}'.format(name))
            return
        file_name = os.path.basename(pkg.href)
        dst_file = os.path.join(dst_dir, file_name)
        LOG.info('url of [{0}] = [{1}]'.format(name, pkg.get_url()))
        if not self.need_download_again(pkg.checksum, dst_file):
            print(file_name.ljust(60), 'exists')
            LOG.info('{0} no need download again'.format(file_name))
            return
        self.download_file(pkg.get_url(), dst_file)
        print(file_name.ljust(60), 'download success')

    def download(self, pkg, dst_dir):
        """
        download the package

        :param pkg: packages information
        :param dst_dir: download target directory
        """
        if 'name' not in pkg:
            return

        name = pkg['name']
        ver = pkg['version'] if 'version' in pkg else None
        rel = pkg['release'] if 'release' in pkg else None

        if 'url' in pkg:
            file_name = os.path.basename(pkg['url'])
            dst_file = os.path.join(dst_dir, file_name)
            checksum = pkg['sha256'] if 'sha256' in pkg else None
            if checksum and not self.need_download_again(checksum, dst_file):
                print(file_name.ljust(60), 'exists')
                return
            self.download_file(pkg['url'], dst_file)
            print(file_name.ljust(60), 'download success')
            return

        if 'autodependency' in pkg and pkg['autodependency'] == 'true':
            self.download_with_dep(name, dst_dir, ver, rel)
        else:
            self.download_without_dep(name, dst_dir, ver, rel)


    @staticmethod
    def need_download_again(target_sha256, dst_file):
        """
        need_download_again

        :param target_sha256:
        :param dst_file:
        :return:
        """
        if target_sha256 is None:
            return True
        if not os.path.exists(dst_file):
            return True
        file_sha256 = calc_sha256(dst_file)
        if target_sha256 != file_sha256:
            LOG.warn('target sha256 : {}, exists file sha256 : {}'.format(target_sha256, file_sha256))
            return True
        else:
            return False


def main():
    """
    need_download_again

    :param target_sha256:
    :param dst_file:
    :return:
    """
    yum_inst = Yum('downloader/config/CentOS_8.2_x86_64/source.repo', 'x86_64')
    yum_inst.make_cache()
    yum_inst.download_with_dep('gcc', './test')


if __name__ == '__main__':
    main()
