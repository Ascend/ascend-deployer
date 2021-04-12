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
from download_util import DOWNLOAD_INST, calc_sha256
from logger_config import get_logger
import software_mgr

LOG = get_logger(__file__)


def download_software(software, dst):
    """
    下载软件的其他资源
    """
    formal_name = software_mgr.get_software_name(software)
    others = software_mgr.get_software_other(software)
    download_dir = os.path.join(dst, "resources", formal_name)
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)
    results = []
    for item in others:
        dest_file = os.path.join(download_dir, os.path.basename(item['url']))
        if os.path.exists(dest_file) and 'sha256' in item:
            file_hash = calc_sha256(dest_file)
            url_hash = item['sha256']
            if file_hash == url_hash:
                print(item['filename'].ljust(60), 'exists')
                continue
        results.append(DOWNLOAD_INST.download(item['url'], dest_file))
        print(item['filename'].ljust(60), 'download success')
    return all(results)


def download_other_software(software_list, dst):
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
