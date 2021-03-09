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

LOG = get_logger(__file__)


def download_other_packages():
    """
    download_other_packages

    :return:
    """
    script = os.path.realpath(__file__)
    script_dir = os.path.dirname(script)
    base_dir = os.path.dirname(script_dir)
    resources_json = os.path.join(script_dir, 'other_resources.json')
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
            DOWNLOAD_INST.download(item['url'], dest_file)
            print(item['filename'].ljust(60), 'download success')
    MindsporeDownloader().download_mindspore()


class MindsporeDownloader(object):
    """
    download_mindspore_packages

    :return:
    """
    def __init__(self):
        self.os = None
        self.os_version = None
        self.arch = None
        self.platform = None
        self.support_os_version = ['centos_7.6', 'centos_8.2', 'ubuntu_18.04', 'euleros_2.8']
        self.mindspore_version = None
        self.base_dir = None

    def is_support(self, os_ver_arch):
        tmp = os_ver_arch.split('_')
        if len(tmp) < 3:
            return False
        self.os_version = tmp[0].lower() + '_' + tmp[1]
        self.arch = tmp[2]
        if self.arch == 'x86':
            self.arch = "x86_64"
        if self.os_version and self.arch:
            if self.os_version not in self.support_os_version:
                return False
            if 'euler' in self.os_version and self.arch != 'aarch64':
                return False
            return True
        return False

    def check_platform(self):
        platform_dict = {
            "ubuntu_18.04": {
                "x86_64":(
                    {
                    "device": "Ascend910",
                    "sha256": "d09c5f79ee849a79a43fc039f9f953b191b39749b5bc246ce67731890400e42c"
                    },
                    {
                    "device": "Ascend310",
                    "sha256": "67b713b4f9d132f78aff98ed03a52b61d1171d1bb2d0329814d483d32c58e2f1"
                    },
                    {
                    "device": "CPU",
                    "sha256": "517d44d97e0beee55600f1b5045e7685f6f7ef1377005b91818f8394186066db"
                    },
                ),
                "aarch64":(
                    {
                    "device": "Ascend910",
                    "sha256": "274409037cf8b1af0f8d1f12205323976bdbe9e5972ca52999433d851dc71790"
                    },
                    {
                    "device": "Ascend310",
                    "sha256": "e26aeb12b2d35dd71e3b8a37f2473b3cde7970094a64cd7723521e9426c6c611"
                    },
                    {
                    "device":"CPU",
                    "sha256": "8a7bdf4496fe1d4bcef408c7695be00590e64b7ddd188ba9921de6906eac38e8"
                    },
                )
            },
            "centos_7.6":{
                "x86_64": (
                    {
                    "device": "Ascend910",
                    "sha256": "3b1f9c871b34ffbfa45d7dc55355adc0e828dbc5fb27d380ffed203644ef9155"
                    },),
                "aarch64": (
                    {
                    "device": "Ascend910",
                    "sha256": "e01d0c52c7cf5670368e9bac6f06f9627eb016d109a48fc77dd7debd135599c9"
                    },)
            },
            'centos_8.2': {
                "x86_64": (
                    {
                    "device": "Ascend910",
                    "sha256": "2863bbed0c9cbcf466089eeeda3d9064208ff00ea9ff0ba5510358133f9acb1f"
                    },
                    {
                    "device": "Ascend310",
                    "sha256": "869e514337ecbd37a8f08702af5b509b7f6fd10e53b77ad2647546e77e37e2a3"
                    },),
                "aarch64": (
                    {
                    "device": "Ascend910",
                    "sha256": "e15c6a16194b4d6432dce05207018ee2117a5a5404c1cf86f45b1e52edbd26d9"
                    },
                    {
                    "device": "Ascend310",
                    "sha256": "9c743455d5b9e4362c690794ea2809d1f70b713c749eaf60f9e95a9c5ae79347"
                    },)
            },
            'euleros_2.8':{
                "aarch64": (
                    {
                    "device": "Ascend910",
                    "sha256": "8853ec5ebb488a34e45846c7fac697f1aff279d59bd5f73563fe6bc76452596e"
                    },
                    {
                    "device": "Ascend310",
                    "sha256": "276f4ed73a341db1bcb42319024bf86ee2687c5ee05662d7a828824b3ddba124"
                    },)
            }
        }
        try:
            self.platform = platform_dict[self.os_version][self.arch]
            if self.os_version == 'centos_7.6':
                self.mindspore_version = "1.0.1"
            else:
                self.mindspore_version = '1.1.1'
        except Exception:
            self.platform = None

    def download_mindspore(self):
        script = os.path.realpath(__file__)
        script_dir = os.path.dirname(script)
        base_dir = os.path.dirname(script_dir)
        resources_dir = os.path.join(base_dir, 'resources')
        if not os.path.exists(resources_dir):
            return
        for d in os.listdir(resources_dir):
            if not os.path.isdir(os.path.join(resources_dir, d)):
                continue
            if not self.is_support(d):
                continue
            self.base_dir = os.path.join(resources_dir, d)
            self.check_platform()
            self.download()

    def download(self):
        if self.platform is None:
            return
        ms_version = self.mindspore_version
        arches = {'x86_64': 'x86', "aarch64": "aarch64"}
        arch = self.arch
        os_arch = self.os_version.split('_')[0] + '_' + arches.get(arch)
        base_url = {
            "Ascend910": "https://ms-release.obs.cn-north-4.myhuaweicloud.com/{ms_version}" \
                "/MindSpore/ascend/{os_arch}/mindspore_ascend-{ms_version}-cp37-cp37m-linux_{arch}.whl",
            "Ascend310": "https://ms-release.obs.cn-north-4.myhuaweicloud.com/{ms_version}" \
                "/MindSpore/ascend/ascend310/{os_arch}/mindspore_ascend-{ms_version}-cp37-cp37m-linux_{arch}.whl",
            "CPU": "https://ms-release.obs.cn-north-4.myhuaweicloud.com/{ms_version}" \
                "/MindSpore/cpu/{os_arch}/mindspore-{ms_version}-cp37-cp37m-linux_{arch}.whl",
        }
        for plat in self.platform:
            p = plat['device']
            sha256 = plat['sha256']
            url = base_url.get(p)
            url = url.format(**{'ms_version': ms_version, "os_arch": os_arch, 'arch': arch})
            des_file = os.path.join(self.base_dir, p, url.split('/')[-1])
            if os.path.exists(des_file):
                file_sha256 = calc_sha256(des_file)
                if file_sha256 == sha256:
                    print(des_file.split('/')[-1].ljust(60), 'exists')
                    continue
            DOWNLOAD_INST.download(url, des_file)


if __name__ == '__main__':
    download_other_packages()
