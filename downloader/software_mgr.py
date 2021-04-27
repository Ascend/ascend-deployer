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
"""software manager,管理可选下载的软件"""
import json
import os

CUR_DIR = os.path.dirname(__file__)
g_software_list = []

class Software(object):
    """
    软件类，用于存储软件信息
    """
    def __init__(self, name, default=False):
        self.name = name
        self.default = default
        self.sys_pkgs = {}
        self.other_pkgs = {}
        self.version = ""

    def __lt__(self, other):
        return self.version < other.version

    def get_name(self):
        """get name"""
        return self.name

    def get_default(self):
        """get default"""
        return self.default

    def get_version(self):
        """get version"""
        return self.version

    def set_version(self, version):
        """set version"""
        self.version = version

    def get_sys_pkgs(self, sys_name):
        """get sys dependencies"""
        if sys_name not in self.sys_pkgs:
            return []
        return self.sys_pkgs[sys_name]

    def set_sys_pkgs(self, sys_name, pkg_list):
        """set sys dependencies"""
        self.sys_pkgs[sys_name] = pkg_list

    def get_other_pkgs(self):
        """get other dependencies"""
        return self.other_pkgs

    def set_other_pkgs(self, pkg_list):
        """set other dependencies"""
        self.other_pkgs = pkg_list


def load_software(json_file):
    """从文件读取软件信息"""
    with open(json_file) as file_obj:
        json_obj = json.load(file_obj)
        soft = Software(json_obj['name'], json_obj['default'])
        soft.set_version(json_obj['version'])
        if 'systems' in json_obj:
            for sys_obj in json_obj['systems']:
                soft.set_sys_pkgs(sys_obj['system'], sys_obj['sys'])
        if 'other' in json_obj:
            soft.set_other_pkgs(json_obj['other'])
        g_software_list.append(soft)


def software_init():
    """初始化"""
    soft_dir = os.path.join(CUR_DIR, 'software')
    for _, _, files in os.walk(soft_dir):
        for file_name in files:
            if file_name.endswith('json'):
                load_software(os.path.join(CUR_DIR, 'software', file_name))


def get_software_name_version(software):
    """
    获取软件依包的正式名和版本号
    :param in:  software      软件名,可能带==<version>
    :return:   正式名和版本号。例如 CANN==20.2.RC1->CANN,20.2.RC1; MindStudio==2.0.0->MindStudio,2.0.0
    """
    if len(g_software_list) == 0:
        software_init()

    if '==' in software:
        name = software.split('==')[0]
        version = software.split('==')[1]
    else:
        name = software
        for soft in g_software_list:
            if soft.get_default() and soft.get_name() == name:
                version = soft.get_version()

    return name, version


def get_software_sys(name, sys_name, version=None):
    """
    获取软件依赖的操作系统依赖
    :param in:  name      软件名
    :param in:  sys_name  操作系统
    :param in:  version   软件版本
    :return:   软件name在操作系统sys_name下的系统依赖列表
    """
    if len(g_software_list) == 0:
        software_init()
    g_software_list.reverse()
    for soft in g_software_list:
        if version is None:
            if soft.get_name().lower() == name.lower():
                return soft.get_sys_pkgs(sys_name)
        else:
            if soft.get_name().lower() == name.lower() and soft.get_version() == version:
                return soft.get_sys_pkgs(sys_name)

    return []


def get_software_other(name, version=None):
    """
    获取软件的其他依赖项
    :param in:  name      软件名
    :param in:  version   软件版本
    :return:   安装软件name所需要下载的其他内容列表
    """
    if len(g_software_list) == 0:
        software_init()
    g_software_list.reverse()
    for soft in g_software_list:
        if version is None:
            if soft.get_name().lower() == name.lower():
                return soft.get_other_pkgs()
        else:
            if soft.get_name().lower() == name.lower() and soft.get_version() == version:
                return soft.get_other_pkgs()

    return []


def is_software_support(software):
    """
    check if the software is support
    :param in:  software  like mindstudio
    """
    if len(g_software_list) == 0:
        software_init()
    name = software
    version = None
    if '==' in software:
        name = software.split('==')[0]
        version = software.split('==')[1]

    if version is None:
        for soft in g_software_list:
            if soft.get_name().lower() == name.lower():
                return True
    else:
        for soft in g_software_list:
            if soft.get_name().lower() == name.lower() and version == soft.get_version():
                return True

    return False

