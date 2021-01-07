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
from download_util import DOWNLOAD_INST

BASE_URL = "https://gitee.com/ascend/ascend-deployer/raw/master"

EXCLUDE_FILES=['downloader.log', 'config.ini']
EXCLUDE_PATHS=['.git', 'resources', '__pycache__']

def not_upgrade(full_path):
    for p in EXCLUDE_PATHS:
        if p in full_path:
            return True

    file_name = os.path.basename(full_path)
    if file_name in EXCLUDE_FILES:
        return True

    return False

def upgrade_self():
    script = os.path.realpath(__file__)
    deployer_dir = os.path.dirname(os.path.dirname(script))

    cache = {}

    for root, _, fs in os.walk(deployer_dir):
        for f in fs:
            full_path = os.path.join(root, f)
            if not_upgrade(full_path):
                continue

            remote = BASE_URL + full_path[len(deployer_dir):]
            cache[full_path] = remote.replace('\\', '/')

    for local, url in cache.items():
        if DOWNLOAD_INST.download_no_retry(url, local):
            print(local[(len(deployer_dir) + 1):].ljust(60), 'upgrade success')

if __name__ == '__main__':
    upgrade_self()
