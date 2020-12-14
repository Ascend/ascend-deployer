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
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin


LOG = logger_config.get_logger(__file__)


class Yum(object):
    """
    downloader for yum
    """
    def __init__(self, source_file, arch):
        self.arch = arch
        self.cache = {}
        # 读取源配置
        script = os.path.realpath(__file__)
        self.base_dir = os.path.dirname(os.path.dirname(script))
        self.repo_file = os.path.join(self.base_dir, source_file)
        config = configparser.ConfigParser()
        config.read(self.repo_file)

        self.cache_dir = os.path.join(self.base_dir,
                                      os.path.dirname(source_file))
        print('repofile={} cache={}'.format(self.repo_file, self.cache_dir))
        LOG.info('repofile={} cache={}'.format(self.repo_file, self.cache_dir))
        self.sources = {}
        for item in config.keys():
            if 'DEFAULT' == item:
                continue
            self.sources[item] = config.get(item, 'baseurl')
            print(config.get(item, 'baseurl'))
            LOG.info(config.get(item, 'baseurl'))

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

        for pkg in handler.packages:
            pkg.dump_to_primary_sqlite(yum_meta_sqlite.primary_cur)
        yum_meta_sqlite.primary_connection.commit()

    def make_cache(self):
        """
        make_cache

        :return:
        """ 
        for name, url in self.sources.items():
            repomd_url = urljoin(url, 'repodata/repomd.xml')
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
            print('download from [{0}]'.format(url))
            LOG.info('download from [{0}]'.format(url))
            DOWNLOAD_INST.download(url, dst_file)
        except HTTPError as http_error:
            print('[{0}]->{1}'.format(url, http_error))
            LOG.error('[{0}]->{1}'.format(url, http_error))

    def get_url_by_pkg_name(self, pkg_name):
        """
        在数据库中查询包名对应的url
        """
        for name, url in self.sources.items():
            db_file = os.path.join(self.cache_dir, name + '_primary.sqlite')
            print('searching {0}'.format(db_file))
            LOG.info('searching {0}'.format(db_file))
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()
            sql_param = {"name": pkg_name, "arch": self.arch}
            cur.execute(
                "select location_href from packages \
                where name = :name and (arch = :arch or arch= 'noarch')",
                sql_param)
            result = cur.fetchall()
            print(result)
            LOG.info(result)
            if len(result) > 0 and len(result[0]) > 0:
                return url + '/' + result[0][0]
        return None

    def get_url(self, pkg_name, ver, release):
        """
        在数据库中查询包名对应的url
        """
        for name, url in self.sources.items():
            db_file = os.path.join(self.cache_dir, name + '_primary.sqlite')
            print('searching {0}'.format(db_file))
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()
            sql_param = {"name": pkg_name, "arch": self.arch,
                    "version": ver, "release": release}
            cur.execute(
                "select location_href from packages \
                where name = :name and (arch = :arch or arch= 'noarch') \
                and version = :version and release = :release",
                sql_param)
            result = cur.fetchall()
            print(result)
            if len(result) > 0 and len(result[0]) > 0:
                return url + '/' + result[0][0]
        return None

    def get_sha256_by_sql_and_params(self, pkg_name, version=None, release=None):
        """
        get_sha256_by_sql_and_params

        :param pkg_name:
        :param version:
        :param release:
        :return:
        """ 
        sql_param = {"name": pkg_name, "arch": self.arch,
                    "version": version, "release": release}
        sql_str = "select pkgId from packages \
                where name = :name and (arch = :arch or arch = 'noarch')"
        if version is not None:
            sql_param["version"] = version
            sql_str += ' and version = :version'
        if release is not None:
            sql_param['release'] = release
            sql_str += ' and release = :release'
        # 在数据库中查询包名对应的url
        for name, url in self.sources.items():
            db_file = os.path.join(self.cache_dir, name + '_primary.sqlite')
            print('searching {0}'.format(db_file))
            LOG.info('searching {0}'.format(db_file))
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()
            cur.execute(sql_str, sql_param)
            result = cur.fetchall()
            print(result)
            LOG.info(result)
            if len(result) > 0 and len(result[0]) > 0:
                return result[0][0]
        return None

    def download(self, name, dst_dir, ver=None, release=None):
        """
        download

        :param name:
        :param dst_dir:
        :param ver:
        :param release:
        :return:
        """
        url = ""
        if ver is not None and release is not None:
            url = self.get_url(name, ver, release)
        else:
            url = self.get_url_by_pkg_name(name)
        if url is None:
            print('can not find {0}'.format(name))
            LOG.error('can not find {0}'.format(name))
            return
        file_name = os.path.basename(url)
        dst_file = os.path.join(dst_dir, file_name)
        print('url of [{0}] = [{1}]'.format(name, url))
        LOG.info('url of [{0}] = [{1}]'.format(name, url))
        target_sha256 = self.get_sha256_by_sql_and_params(name, ver, release)
        if not self.need_download_again(target_sha256, dst_file):
            print('no need download again')
            LOG.info('no need download again')
            return
        self.download_file(url, dst_file)

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
            print('target sha256 : {}, exists file sha256 : {}'.format(target_sha256, file_sha256))
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
    yum_inst.download('net-tools', './')


if __name__ == '__main__':
    main()
