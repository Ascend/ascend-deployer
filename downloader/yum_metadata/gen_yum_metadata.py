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
import sqlite3 as sqlite
import xml.sax

class Require(object):
    def __init__(self, name):
        self.name = name
        self.flags = None
        self.epoch = None
        self.version = None
        self.release = None
        self.pkgKey = None
        self.pre = False


class Provide(object):
    def __init__(self, name):
        self.name = name
        self.flags = None
        self.epoch = None
        self.version = None
        self.release = None
        self.pkgKey = None

class YumPackageHandler(xml.sax.handler.ContentHandler):
    """
    parse xml of rpm packages
    """
    def __init__(self):
        self.super().__init__()
        self.CurrentData = ""
        self.CurrentAttributes = ""
        self.checksum = None
        self.name = None
        self.arch = None
        self.summary = None
        self.description = None
        self.url = None

        self.version_attr = None
        self.time_attr = None
        self.size_attr = None
        self.location_attr = None
        self.checksum_attr = None
        self.entry_attr = None
        self.pkg = None

        self.packages = []
        self.provide_list = []
        self.require_list = []
        self.provide_flag = False
        self.require_flag = False

    def set_pkg(self, key, value):
        """
        set_pkg

        :param key     key
        :param value   value
        :return:
        """
        self.pkg.package[key] = value

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        self.CurrentAttributes = attributes
        if tag == 'package':
            self.pkg = YumPackage({})
            self.packages.append(self.pkg)
        elif tag == 'version':
            self.version_attr = attributes
        elif tag == 'time':
            self.time_attr = attributes
        elif tag == 'size':
            self.size_attr = attributes
        elif tag == 'location':
            self.location_attr = attributes
        elif tag == 'checksum':
            self.checksum_attr = attributes
        elif tag == 'rpm:provides':
            self.provide_flag = True
            self.require_flag = False
            self.provide_list = []
        elif tag == 'rpm:requires':
            self.require_flag = True
            self.provide_flag = False
            self.require_list = []
        elif tag == 'rpm:entry':
            self.entry_attr = attributes

    def endElement(self, tag):
        if self.CurrentData == "checksum":
            self.set_pkg('pkgId', self.checksum)
            self.set_pkg('checksum_type', self.checksum_attr.get('type'))
            self.checksum_attr = {}
        elif self.CurrentData == 'name':
            self.set_pkg('name', self.name)
        elif self.CurrentData == 'arch':
            self.set_pkg('arch', self.arch)
        elif self.CurrentData == 'version':
            self.set_pkg("version", self.version_attr.get('ver'))
            self.set_pkg("epoch", self.version_attr.get('epoch'))
            self.set_pkg("release", self.version_attr.get('rel'))
            self.version_attr = {}
        elif self.CurrentData == 'summary':
            self.set_pkg('summary', self.summary)
        elif self.CurrentData == 'description':
            self.set_pkg('description', self.description)
        elif self.CurrentData == 'url':
            self.set_pkg('url', self.url)
        elif self.CurrentData == 'time':
            self.set_pkg('time_file', self.time_attr.get('file'))
            self.set_pkg('time_build', self.time_attr.get('build'))
            self.time_attr = {}
        elif self.CurrentData == 'size':
            self.set_pkg('size_package', self.size_attr.get('package'))
            self.set_pkg('size_installed', self.size_attr.get('installed'))
            self.set_pkg('size_archive', self.size_attr.get('archive'))
            self.size_attr = {}
        elif self.CurrentData == 'location':
            self.set_pkg('location_href', self.location_attr.get('href'))
            self.set_pkg('location_base', self.location_attr.get('base'))
            self.location_attr = {}
        elif tag == 'rpm:entry':
            if self.provide_flag:
                pro = Provide(self.entry_attr.get('name'))
                pro.flags = self.entry_attr.get('flags')
                pro.epoch = self.entry_attr.get('epoch')
                pro.version = self.entry_attr.get('ver')
                pro.release = self.entry_attr.get('rel')
                self.provide_list.append(pro)
            if self.require_flag:
                req = Require(self.entry_attr.get('name'))
                req.flags = self.entry_attr.get('flags')
                req.epoch = self.entry_attr.get('epoch')
                req.version = self.entry_attr.get('ver')
                req.release = self.entry_attr.get('rel')
                tmp = self.entry_attr.get('pre')
                if tmp is not None and tmp == '1':
                    req.pre = True
                self.require_list.append(req)
        elif tag == 'rpm:provides':
            self.set_pkg('provides', self.provide_list)
            self.provide_flag = False
        elif tag == 'rpm:requires':
            self.set_pkg('requires', self.require_list)
            self.require_flag = False

    def characters(self, content):
        if self.CurrentData == 'checksum':
            self.checksum = content
        elif self.CurrentData == 'name':
            self.name = content
        elif self.CurrentData == 'arch':
            self.arch = content
        elif self.CurrentData == 'summary':
            self.summary = content
        elif self.CurrentData == 'description':
            self.description = content
        elif self.CurrentData == 'url':
            self.url = content


class YumPackage(object):
    def __init__(self, package):

        self.package = package

    def __str__(self):
        return "name: %s, arch %s, version: %s, href: %s" % (
            self.package.get('name'),
            self.package.get('arch'),
            self.package.get('version'),
            self.package.get('location_href'),
        )

    def _get_sqlite_null(self, value):
        return None if not value else value

    def dump_to_primary_sqlite(self, pkgKey, cur):
        """
        dump_to_primary_sqlite

        :param pkgKey database key
        :param cur    database cursor
        :return:
        """
        self.dump_to_packages(pkgKey, cur)
        if 'requires' in self.package:
            self.dump_to_requires(pkgKey, cur)
        if 'provides' in self.package:
            self.dump_to_provides(pkgKey, cur)

    def dump_to_packages(self, pkgKey, cur):
        """insert primary data"""
        fields = [
            'pkgKey',
            'pkgId',
            'name',
            'arch',
            'version',
            'epoch',
            'release',
            'summary',
            'description',
            'url',
            'time_file',
            'time_build',
            'rpm_license',
            'rpm_vendor',
            'rpm_group',
            'rpm_buildhost',
            'rpm_sourcerpm',
            'rpm_header_start',
            'rpm_header_end',
            'rpm_packager',
            'size_package',
            'size_installed',
            'size_archive',
            'location_href',
            'location_base',
            'checksum_type',
        ]
        keys = ','.join(fields)
        values = ','.join([":%s" % key for key in fields])
        sql = "INSERT INTO packages (%s) VALUES (%s)" % (keys, values)

        sql_param = {
            key: self._get_sqlite_null(self.package.get(key))
            for key in fields
        }
        sql_param['pkgKey'] = pkgKey
        cur.execute(sql, sql_param)

    def dump_to_provides(self, pkgKey, cur):
        """
        dump_to_provides

        :param pkgKey database key
        :param cur    database cursor
        :return:
        """
        fields = ['name', 'flags' 'epoch', 'version', 'release', 'pkgKey']
        keys = ','.join(fields)
        values = ','.join([":%s" % key for key in fields])
        sql = "INSERT INTO provides (%s) VALUES (%s)" % (keys, values)

        for provide in self.package.get('provides'):
            sql_param = {
                'name':    provide.name,
                'flags':   provide.flags,
                'epoch':   provide.epoch,
                'version': provide.version,
                'release': provide.release,
                'pkgKey':  pkgKey
            }
            cur.execute(sql, sql_param)

    def dump_to_requires(self, pkgKey, cur):
        """
        dump_to_requires

        :param pkgKey database key
        :param cur    database cursor
        :return:
        """
        fields = ['name', 'flags' 'epoch', 'version', 'release', 'pkgKey', 'pre']
        keys = ','.join(fields)
        values = ','.join([":%s" % key for key in fields])
        sql = "INSERT INTO requires (%s) VALUES (%s)" % (keys, values)

        for require in self.package.get('requires'):
            sql_param = {
                'name':    require.name,
                'flags':   require.flags,
                'epoch':   require.epoch,
                'version': require.version,
                'release': require.release,
                'pkgKey':  pkgKey,
                'pre': False
            }
            cur.execute(sql, sql_param)


class YumMetadataSqlite(object):
    """
    YumMetadataSqlite

    create database for the repository
    """
    def __init__(self, target_dir, db_file_name, overwrite=True):
        """
        connect db
        """
        self.primary_db_file = os.path.join(target_dir, db_file_name)
        if overwrite and os.path.exists(self.primary_db_file):
            os.remove(self.primary_db_file)

        self.primary_connection = sqlite.Connection(self.primary_db_file)
        self.primary_cur = self.primary_connection.cursor()

    def create_primary_db(self):
        """create primary db scheme"""
        cur_path = os.path.abspath(os.path.dirname(__file__))

        with open(os.path.join(cur_path, "create_yum_metadata_primary_db.sql")) as fid:
            sql_as_str = fid.read()

        self.primary_cur.executescript(sql_as_str)


def main():
    """
    main function
    """
    primary_xml_file = "test_primary.xml"
    primary_file_path = os.path.abspath(os.path.dirname(primary_xml_file))
    meta_sqlite = YumMetadataSqlite(primary_file_path, 'oss_primary.sqlite')
    meta_sqlite.create_primary_db()

    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = YumPackageHandler()
    parser.setContentHandler(handler)
    parser.parse(primary_xml_file)

    for pkg in handler.packages:
        print(pkg)
        pkg.dump_to_primary_sqlite(meta_sqlite.primary_cur)
    meta_sqlite.primary_connection.commit()


if __name__ == "__main__":
    main()
