#!/usr/bin/env python3
# coding: utf-8
import json
import os
import sys
import time

from deb_downloader import Apt
from rpm_downloader import Yum
from download_util import CONFIG_INST

CUR_DIR = os.path.dirname(os.path.realpath(__file__))


class OsDepDownloader:
    def __init__(self):
        arch_list = CONFIG_INST.get_download_arch_list()
        os_list = CONFIG_INST.get_download_os_list()
        self.dir_list = [f'{os_info}_{arch_info}'
                         for os_info in os_list for arch_info in arch_list]
        self.project_dir = os.path.dirname(CUR_DIR)
        self.resources_dir = os.path.join(self.project_dir, 'resources')

    def prepare_download_dir(self):
        for dir_item in self.dir_list:
            dst_dir = os.path.join(self.resources_dir, dir_item)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir, mode=0o755, exist_ok=True)

    def clean_download_dir(self):
        if os.path.exists(self.resources_dir):
            import shutil
            shutil.rmtree(self.resources_dir)
        print('clean resources directory successfully')

    def download_pkg_from_json(self):
        for dir_item in self.dir_list:
            dst_dir = os.path.join(self.resources_dir, dir_item)
            print(f'item:{dir_item} save dir: {dst_dir}')
            config_file = os.path.join(CUR_DIR,
                                       f'config/{dir_item}/pkg_info.json')
            downloader = None
            if 'Ubuntu' in dir_item:
                source_list_file = f'downloader/config/{dir_item}/source.list'
                if 'aarch64' in dir_item:
                    downloader = Apt(source_list_file, 'aarch64')
                else:
                    downloader = Apt(source_list_file, 'x86_64')
            else:
                source_repo_file = f'downloader/config/{dir_item}/source.repo'
                if 'aarch64' in dir_item:
                    downloader = Yum(source_repo_file, 'aarch64')
                else:
                    downloader = Yum(source_repo_file, 'x86_64')
            if downloader is not None:
                downloader.make_cache()

            with open(config_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for item in data:
                    downloader.download(item['name'], dst_dir)


def main():
    os_dep = OsDepDownloader()
    if len(sys.argv) == 2 and sys.argv[1] == 'clean':
        print('clean download dir...')
        os_dep.clean_download_dir()
    else:
        time_start = time.time()
        os_dep.prepare_download_dir()
        os_dep.download_pkg_from_json()
        print(f'total time: {time.time() - time_start} seconds')


if __name__ == "__main__":
    main()
