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


if __name__ == '__main__':
    download_other_packages()
