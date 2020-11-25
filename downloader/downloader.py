#!/usr/bin/env python3
import os

from pip_downloader import MyPip
from os_dep_downloader import OsDepDownloader


def download_python_packages():
    script = os.path.realpath(__file__)
    require_file = os.path.join(os.path.dirname(script), 'requirements.txt')
    repo_path = os.path.join(os.path.dirname(script), '../resources')
    if not os.path.exists(repo_path):
        os.mkdir(repo_path)

    pip = MyPip()
    with open(require_file) as file_content:
        for line in file_content.readlines():
            print('[{0}]'.format(line.strip()))
            pip.download(line.strip(), repo_path)


def download_os_packages():
    os_dep = OsDepDownloader()
    os_dep.prepare_download_dir()
    os_dep.download_pkg_from_json()


if __name__ == "__main__":
    download_python_packages()
    download_os_packages()
