#!/usr/bin/env python3
import urllib.request
import configparser
import os
import gzip
import bz2
import sqlite3
import lzma
from xml.dom import minidom
from download_util import DOWNLOAD_INST


class Yum():
    def __init__(self, source_file, arch):
        self.arch = arch
        self.cache = {}
        """读取源配置"""
        script = os.path.realpath(__file__)
        self.base_dir = os.path.dirname(os.path.dirname(script))
        self.repo_file = os.path.join(self.base_dir, source_file)
        config = configparser.ConfigParser()
        config.read(self.repo_file)

        self.cache_dir = os.path.join(self.base_dir,
                                      os.path.dirname(source_file))
        print(f'repofile={self.repo_file} cache={self.cache_dir}')
        self.sources = {}
        for item in config.keys():
            if 'DEFAULT' == item:
                continue
            self.sources[item] = config.get(item, 'baseurl')
            print(config.get(item, 'baseurl'))

    def make_cache(self):
        for name, url in self.sources.items():
            print('{0}:{1}'.format(name, url + '/repodata/repomd.xml'))
            repomd_url = url + '/repodata/repomd.xml'
            repomd_xml = name + '_repomd.xml'
            repomd_file = os.path.join(self.cache_dir, repomd_xml)
            db_file = os.path.join(self.cache_dir, name + '_primary.sqlite')

            if not os.path.exists(repomd_file):
                """下载repomd.xml文件"""
                self.download_file(repomd_url, repomd_file)

            """解析repomod.xml文件，得到数据库文件的url"""
            db_url = url + '/' + self.parse_repomd(repomd_file)
            url_file_name = os.path.basename(db_url).split('-')[1];
            compressed_file = os.path.join(self.cache_dir,
                                           name + '_' + url_file_name)
            print('dburl=[{0}]'.format(db_url))

            """下载数据库文件"""
            self.download_file(db_url, compressed_file)

            """解压数据库文件"""
            self.uncompress_file(compressed_file, db_file)

    def uncompress_file(self, compress_file, dst_file):
        """
        解压文件
        """
        if os.path.exists(dst_file):
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

    def parse_repomd(self, file_name):
        """
        解析repomd.xml文件，得到primary数据文件的url
        """
        dom = minidom.parse(file_name)
        data_elements = dom.getElementsByTagName('data')
        for i in data_elements:
            if i.getAttribute('type') != 'primary_db':
                continue
            location = i.getElementsByTagName('location')[0]
            print(location.getAttribute('href'))
            return location.getAttribute('href')

    def download_file(self, url, dst_file):
        try:
            print('download from [{0}]'.format(url))
            DOWNLOAD_INST.download(url, dst_file)
        except HTTPError as http_error:
            print('[{0}]->{1}'.format(url, http_error))

    def get_url_by_pkg_name(self, pkg_name):
        """
        在数据库中查询包名对应的url
        """
        for name, url in self.sources.items():
            db_file = os.path.join(self.cache_dir, name + '_primary.sqlite')
            print('searching {0}'.format(db_file))
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()
            sql_param = {"name": pkg_name, "arch": self.arch}
            cur.execute(
                "select location_href from packages \
                where name = :name and (arch = :arch or arch= 'noarch')",
                sql_param)
            result = cur.fetchall()
            print(result)
            if len(result) > 0 and len(result[0]) > 0:
                return url + '/' + result[0][0]
        return None

    def download(self, name, dst_dir):
        url = self.get_url_by_pkg_name(name)
        if url is None:
            print('can not find {0}'.format(name))
            return
        file_name = os.path.basename(url)
        dst_file = os.path.join(dst_dir, file_name)
        print('url of [{0}] = [{1}]'.format(name, url))
        self.download_file(url, dst_file)


def main():
    yum_inst = Yum('downloader/config/CentOS_8.2_x86_64/source.repo', 'x86_64')
    yum_inst.make_cache()
    yum_inst.download('net-tools', './')


if __name__ == '__main__':
    main()
