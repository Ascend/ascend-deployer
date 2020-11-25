#!/usr/bin/env python3
# coding: utf-8
import os
import json
from download_util import DOWNLOAD_INST


def download_other_packages():
    script = os.path.realpath(__file__)
    script_dir = os.path.dirname(script)
    base_dir = os.path.dirname(script_dir)
    resources_json = os.path.join(script_dir, 'other_resources.json')
    with open(resources_json, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for item in data:
            dest_file = os.path.join(base_dir, item['dest'], item['filename'])
            print('download[{0}] -> [{1}]'.format(item['url'], dest_file))
            DOWNLOAD_INST.download(item['url'], dest_file)


if __name__ == '__main__':
    download_other_packages()
