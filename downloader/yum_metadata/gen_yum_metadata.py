# coding: utf-8
import os
import sqlite3 as sqlite
import xml.sax


class YumPackageHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.CurrentData = ""
        self.CurrentAttributes = ""

        self.packages = []

    def set_pkg(self, key, value):
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

    def dump_to_primary_sqlite(self, cur):
        """insert primary data"""
        fields = [
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
        values_placeholder = ','.join([":%s" % key for key in fields])
        op = "insert into packages (%s) values (%s)" % (keys, values_placeholder)

        packages = {
            key: self._get_sqlite_null(self.package.get(key))
            for key in fields
        }

        cur.execute(op, packages)


class YumMetadataSqlite(object):
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

    def create_filelists_db(self):
        pass

    def create_other_db(self):
        pass


def main():
    primary_xml_file = "/home/xxx/primary.xml"
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
