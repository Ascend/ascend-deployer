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

import configparser
import json
import os
import shutil
import sys
from download_util import calc_sha256, get_arch, get_specified_python, CONFIG_INST, DOWNLOAD_INST, CANN_DOWNLOAD_INST
import logger_config
from software_mgr import get_software_name_version, get_software_other, get_software_mindspore

LOG = logger_config.LOG
CUR_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = os.path.dirname(CUR_DIR)
PKG_LIST = CONFIG_INST.get_download_pkg_list()
OS_LIST = CONFIG_INST.get_download_os_list()


def download_software(software, dst, arch):
    """
    下载软件的其他资源
    """
    formal_name, version = get_software_name_version(software)
    others = get_software_other(formal_name, version)
    download_dir = os.path.join(dst, "resources", "{0}_{1}".format(formal_name, version))

    if not os.path.exists(download_dir):
        os.makedirs(download_dir, mode=0o750, exist_ok=True)
    LOG.info('item:{} save dir: {}'.format(software, os.path.basename(download_dir)))
    results = []
    if formal_name == "CANN":
        if arch == "x86_64" or arch == "aarch64":
            others = (item for item in others if arch in item['filename'])
        try:
            for item in others:
                dest_file = os.path.join(download_dir, item['filename'])
                if os.path.exists(dest_file) and 'sha256' in item:
                    file_hash = calc_sha256(dest_file)
                    if file_hash == item['sha256']:
                        print(item['filename'].ljust(60), 'exists')
                        LOG.info('{0} no need download again'.format(item['filename']))
                        continue
                ret = CANN_DOWNLOAD_INST.download(item['url'], dest_file)
                if ret:
                    print(item['filename'].ljust(60), 'download success')
                results.append(ret)
        finally:
            CANN_DOWNLOAD_INST.quit()
    else:
        for item in others:
            dest_file = os.path.join(download_dir, item['filename'])
            if os.path.exists(dest_file) and 'sha256' in item:
                file_hash = calc_sha256(dest_file)
                if file_hash == item['sha256']:
                    print(item['filename'].ljust(60), 'exists')
                    LOG.info('{0} no need download again'.format(item['filename']))
                    continue
            ret = DOWNLOAD_INST.download(item['url'], dest_file)
            if ret:
                print(item['filename'].ljust(60), 'download success')
            results.append(ret)
    return all(results)


def download(os_list, software_list, dst):
    """
    按软件列表下载其他部分
    """
    if os_list is None:
        os_list = []
    arch = get_arch(os_list)
    LOG.info('software arch is {0}'.format(arch))

    results = {'ok': [], 'failed': []}
    no_mindspore_list = [software for software in software_list if "MindSpore" not in software]
    for software in no_mindspore_list:
        res = download_software(software, dst, arch)
        if res:
            results['ok'].append(software)
            continue
        results['failed'].append(software)
    return results


def download_pkg_from_json():
    """
    按config.ini下载其他部分
    """
    arch = get_arch(OS_LIST)
    LOG.info('software arch is {0}'.format(arch))

    results = {'ok': [], 'failed': []}
    software_list = [software.replace("_", "==") for software in PKG_LIST if "MindSpore" not in software]
    for software in software_list:
        res = download_software(software, PROJECT_DIR, arch)
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
    if dst is None:
        base_dir = PROJECT_DIR
    else:
        base_dir = dst
    resources_json = os.path.join(CUR_DIR, 'other_resources.json')
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
                    LOG.info('{0} no need download again'.format(item['filename']))
                    continue
            LOG.info('download[{0}] -> [{1}]'.format(item['url'], os.path.basename(dest_file)))
            if DOWNLOAD_INST.download(item['url'], dest_file):
                results['ok'].append(item['filename'])
                print(item['filename'].ljust(60), 'download success')
                continue
            results['failed'].append(item['filename'])
    return results


def download_specified_python(dst=None):
    """
    download ascend_python_version=Python-3.7.5

    :return:
    """
    if dst is None:
        base_dir = PROJECT_DIR
    else:
        base_dir = dst
    specified_python = get_specified_python()
    resources_json = os.path.join(CUR_DIR, 'python_version.json')
    with open(resources_json, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        results = {'ok': [], 'failed': []}
        for item in data:
            if specified_python == item['filename'].rstrip('.tar.xz'):
                dest_file = os.path.join(base_dir, item['dest'], item['filename'])
                if os.path.exists(dest_file) and 'sha256' in item:
                    file_hash = calc_sha256(dest_file)
                    url_hash = item['sha256']
                    if file_hash == url_hash:
                        print(item['filename'].ljust(60), 'exists')
                        LOG.info('{0} no need download again'.format(item['filename']))
                        break
                LOG.info('download[{0}] -> [{1}]'.format(item['url'], os.path.basename(dest_file)))
                if DOWNLOAD_INST.download(item['url'], dest_file):
                    results['ok'].append(item['filename'])
                    print(item['filename'].ljust(60), 'download success')
                    break
                results['failed'].append(item['filename'])
                break
        return results


def download_ms_whl(os_item, software, dst):
    """
    下载软件的其他资源
    """
    formal_name, version = get_software_name_version(software)
    download_dir = os.path.join(dst, "resources", "{}".format(os_item))
    results = []
    if version in ["1.2.1", "1.1.1"]:
        whl_list = get_software_mindspore(formal_name, os_item, version)
        for item in whl_list:
            dest_file = os.path.join(download_dir, item["dst_dir"], os.path.basename(item['url']))
            if os.path.exists(dest_file) and 'sha256' in item:
                file_hash = calc_sha256(dest_file)
                url_hash = item['sha256']
                if file_hash == url_hash:
                    print(item['filename'].ljust(60), 'exists')
                    LOG.info('{0} no need download again'.format(item['filename']))
                    continue
                else:
                    LOG.info('{0} need download again'.format(item['filename']))
            ret = DOWNLOAD_INST.download(item['url'], dest_file)
            if ret:
                print(item['filename'].ljust(60), 'download success')
            results.append(ret)
    else:
        os_item_split = os_item.split("_")
        os_name, arch = "_".join(os_item_split[:2]), "_".join(os_item_split[2:])
        specified_python = get_specified_python()
        implement_flag = "cp37"
        if "Python-3.7" in specified_python:
            implement_flag = "cp37"
        if "Python-3.8" in specified_python:
            implement_flag = "cp38"
        if "Python-3.9" in specified_python:
            implement_flag = "cp39"
        if os_name == "Ubuntu_18.04":
            whl_list = get_software_mindspore(formal_name, "{}".format(os_item), version)
            for item in whl_list:
                if item.get('python', 'cp37') != implement_flag:
                    print("Try to get {} on {}, but it does not match {}".format
                    (item['filename'], item.get('python'), implement_flag))
                    continue
                dest_file = os.path.join(download_dir, "CPU", os.path.basename(item['url']))
                if os.path.exists(dest_file) and 'sha256' in item:
                    file_hash = calc_sha256(dest_file)
                    url_hash = item['sha256']
                    if file_hash == url_hash:
                        print(item['filename'].ljust(60), 'exists')
                        LOG.info('{0} no need download again'.format(item['filename']))
                        continue
                    else:
                        LOG.info('{0} need download again'.format(item['filename']))
                ret = DOWNLOAD_INST.download(item['url'], dest_file)
                if ret:
                    print(item['filename'].ljust(60), 'download success')
                results.append(ret)
        if os_name in ["Ubuntu_18.04", "CentOS_7.6", "EulerOS_2.8", "OpenEuler_20.03LTS", "Kylin_V10Tercel"]:
            whl_list = get_software_mindspore(formal_name, "linux_{}".format(arch), version)
            for item in whl_list:
                if item.get('python', 'cp37') != implement_flag:
                    print("Try to get {} on {}, but it does not match {}".format
                    (item['filename'], item.get('python'), implement_flag))
                    continue
                dest_file = os.path.join(download_dir, "Ascend910", os.path.basename(item['url']))
                if os.path.exists(dest_file) and 'sha256' in item:
                    file_hash = calc_sha256(dest_file)
                    url_hash = item['sha256']
                    if file_hash == url_hash:
                        print(item['filename'].ljust(60), 'exists')
                        LOG.info('{0} no need download again'.format(item['filename']))
                        continue
                    else:
                        LOG.info('{0} need download again'.format(item['filename']))
                ret = DOWNLOAD_INST.download(item['url'], dest_file)
                if ret:
                    print(item['filename'].ljust(60), 'download success')
                results.append(ret)
            
            for item in whl_list:
                if item.get('python', 'cp37') != implement_flag:
                    print("Try to get {} on {}, but it does not match {}".format
                    (item['filename'], item.get('python'), implement_flag))
                    continue
                A910_dest_file = os.path.join(download_dir, "Ascend910", os.path.basename(item['url']))
                if os.path.exists(A910_dest_file) and os_name in ["Ubuntu_18.04", "CentOS_7.6", "EulerOS_2.8"]:
                    dest_file = os.path.join(download_dir, "Ascend310", os.path.basename(item['url']))
                    if os.path.exists(dest_file) and 'sha256' in item:
                        file_hash = calc_sha256(dest_file)
                        url_hash = item['sha256']
                        if file_hash == url_hash:
                            LOG.info('{0} exist, no need copy again'.format(os.path.basename(dest_file)))
                        else:
                            LOG.info('{0} exist but not completed, need copy again'.format(os.path.basename(dest_file)))
                            os.remove(dest_file)
                            shutil.copy(A910_dest_file, dest_file)
                    else:
                        parent_dir = os.path.dirname(dest_file)
                        if not os.path.exists(parent_dir):
                            os.makedirs(parent_dir, mode=0o750, exist_ok=True)
                        LOG.info('{0} not exist, copy from Ascend910'.format(os.path.basename(dest_file)))
                        shutil.copy(A910_dest_file, dest_file)
    return all(results)


def download_ms(os_list, software_list, dst):
    """
    按传参下载mindspore
    """
    results = {'ok': [], 'failed': []}
    mindspore_list = [software for software in software_list if "MindSpore" in software]
    for os_item in os_list:
        for software in mindspore_list:
            res = download_ms_whl(os_item, software, dst)
            if res:
                results['ok'].append(software)
                continue
            results['failed'].append(software)
    return results


def download_ms_from_json():
    """
    按config.ini下载mindspore
    """
    results = {'ok': [], 'failed': []}
    software_list = [software.replace("_", "==") for software in PKG_LIST if "MindSpore" in software]
    for os_item in OS_LIST:
        for software in software_list:
            res = download_ms_whl(os_item, software, PROJECT_DIR)
            if res:
                results['ok'].append(software)
                continue
            results['failed'].append(software)
    return results
