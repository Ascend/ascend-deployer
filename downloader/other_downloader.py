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
import json
from download_util import DOWNLOAD_INST, calc_sha256, CONFIG_INST
from logger_config import get_logger
import software_mgr

LOG = get_logger(__file__)
CUR_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = os.path.dirname(CUR_DIR)
PKG_LIST = CONFIG_INST.get_download_pkg_list()


def get_sha256_map():
    """
    从CANN_<Version>.json文件读取sha256字典，其中记录run包的sha256
    """
    sha256_map = {}
    with open(os.path.join(CUR_DIR, 'sha256.txt')) as sha256_cache:
        for line in sha256_cache.readlines():
            [sha256, name] = [t.strip() for t in line.split(' ') if len(t) > 0]
            sha256_map[name] = sha256
    return sha256_map


def download_software(software, dst):
    """
    下载软件的其他资源
    """
    formal_name, version = software_mgr.get_software_name_version(software)
    others = software_mgr.get_software_other(formal_name, version)
    download_dir = os.path.join(dst, "resources", "{0}_{1}".format(formal_name, version))
    sha256_map = get_sha256_map()

    if not os.path.exists(download_dir):
        os.makedirs(download_dir, mode=0o755, exist_ok=True)
    LOG.info('item:{} save dir: {}'.format(software, download_dir))
    results = []
    for item in others:
        dest_file = os.path.join(download_dir, os.path.basename(item['url']))
        if os.path.exists(dest_file) and 'sha256' in item:
            file_hash = calc_sha256(dest_file)
            url_hash = item['sha256']
            if file_hash == url_hash:
                print(item['filename'].ljust(60), 'exists')
                continue
        if os.path.exists(dest_file) and formal_name == "CANN":
            file_name = os.path.basename(dest_file)
            sha256 = calc_sha256(dest_file)
            if file_name in sha256_map and sha256 == sha256_map[file_name]:
                print(item['filename'].ljust(60), 'exists')
                continue
        ret = DOWNLOAD_INST.download(item['url'], dest_file)
        if ret:
            print(item['filename'].ljust(60), 'download success')
        results.append(ret)
    return all(results)


def download(software_list, dst):
    """
    按软件列表下载其他部分
    """
    results = {'ok': [], 'failed': []}
    for software in software_list:
        res = download_software(software, dst)
        if res:
            results['ok'].append(software)
            continue
        results['failed'].append(software)
    return results


def download_pkg_from_json():
    """
    按config.ini下载其他部分
    """
    results = {'ok': [], 'failed': []}
    software_list = [software.replace("_", "==") for software in PKG_LIST]
    for software in software_list:
        res = download_software(software, PROJECT_DIR)
        if res:
            results['ok'].append(software)
            continue
        results['failed'].append(software)
    return results


def download_other_packages(dst=None):
    """
    download_other_packages

    :return:
    """
    script = os.path.realpath(__file__)
    script_dir = os.path.dirname(script)
    if dst is None:
        base_dir = os.path.dirname(script_dir)
    else:
        base_dir = dst
    resources_json = os.path.join(script_dir, 'other_resources.json')
    results = {'ok': [], 'failed': []}
    with open(resources_json, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for item in data:
            dest_file = os.path.join(base_dir, item['dest'], item['filename'])
            if os.path.exists(dest_file) and 'sha256' in item:
                file_hash = calc_sha256(dest_file)
                url_hash = item['sha256']
                if file_hash == url_hash:
                    print(item['filename'].ljust(60), 'exists')
                    continue
            LOG.info('download[{0}] -> [{1}]'.format(item['url'], dest_file))
            if DOWNLOAD_INST.download(item['url'], dest_file):
                results['ok'].append(item['filename'])
                print(item['filename'].ljust(60), 'download success')
                continue
            results['failed'].append(item['filename'])
    return results


if __name__ == '__main__':
    download_other_packages()
