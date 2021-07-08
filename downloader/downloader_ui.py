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
"""gui application using tk"""
import configparser
import os
import sys
import tkinter as tk
import tkinter.messagebox
import tarfile
import shutil
import threading
from downloader import download_all


CUR_DIR = os.path.dirname(os.path.realpath(__file__))
OS_LIST = os.listdir(os.path.join(CUR_DIR, 'config'))
PKG_LIST = [pkg.split(".json")[0] for pkg in os.listdir(os.path.join(CUR_DIR, 'software'))]

LOCK = threading.Lock()

def make_tarfile():
    if os.path.exists('./ascend-deployer.tar'):
        os.unlink('./ascend-deployer.tar')

    with tarfile.open('../ascend-deployer.tar', "w:tar") as tar:
        tar.add("./", arcname='ascend-deployer')
    shutil.move('../ascend-deployer.tar', './ascend-deployer.tar')

def downloadThread():
    download_all(OS_LIST, "", "./")
    make_tarfile()

thread = threading.Thread(target=downloadThread)

def start_download_thread():
    thread.start()

class Win(object):
    """
    Note:
        the basic window
    """

    def __init__(self):
        self.config_file = os.path.join(CUR_DIR, 'config.ini')
        self.root = tk.Tk()
        self.root.title('AI质检平台离线安装包下载器')
        self.root.geometry('400x200')
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.frame_os = tk.LabelFrame(self.root, text="操作系统选择")
        self.frame_os.pack(fill="both", side="top")
        self.label_info = tk.Label(self.root, text="请将驱动、固件软件放在resources目录中")
        self.label_info.pack()
        self.frame_bottom = tk.LabelFrame(self.root)
        self.frame_bottom.pack(side="bottom")
        self.all_opt = tk.IntVar()
        self.all_opt.set(1)
        self.all_not_opt = tk.IntVar()
        self.all_not_opt.set(0)
        self.os_dict = {}
        self.pkg_dict = {}
        tk.Button(self.frame_bottom, text='开始下载',
                  command=self.start_download).pack()
        self.read_config()
        self.display()

    def display(self):
        """
        Note:
            display the Checkbutton
        """
        os_idx, pkg_idx = 0, 0
        for os_name, var in sorted(self.os_dict.items()):
            os_idx += 1
            tk.Checkbutton(self.frame_os, width=30, text=os_name,
                           variable=var, anchor='w').grid(row=os_idx, column=0)

    def run(self):
        """
        Note:
            the main loop of the window
        """
        self.root.mainloop()

    def check_status(self):
        print(f"download thread is alive: {thread.isAlive()}")
        if thread.isAlive():
            self.root.after(1000, self.check_status)
        else:
            tk.messagebox.showinfo(title="Success", message="下载成功")

    def start_download(self):
        """
        Note:
            start downading, the window will exit
        """
        self.write_config()
        start_download_thread()
        self.root.after(1000, self.check_status)

    def read_config(self):
        """
        Note:
            read the configuration file
        """
        config = configparser.ConfigParser()
        config.read(self.config_file)
        configured_os = [t.strip() for t in config['download']['os_list'].split(',') if t]
        configured_pkg = [t.strip() for t in config['software']['pkg_list'].split(',') if t]
        not_configured_os = list(set(OS_LIST) - set(configured_os))
        not_configured_pkg = list(set(PKG_LIST) - set(configured_pkg))
        for os_name in configured_os:
            var = tk.IntVar()
            var.set(1)
            self.os_dict[os_name] = var
        for os_name in not_configured_os:
            var = tk.IntVar()
            var.set(0)
            self.os_dict[os_name] = var
        for pkg_name in configured_pkg:
            var = tk.IntVar()
            var.set(1)
            self.pkg_dict[pkg_name] = var
        for pkg_name in not_configured_pkg:
            var = tk.IntVar()
            var.set(0)
            self.pkg_dict[pkg_name] = var

    def write_config(self):
        """
        Note:
            write the configuration file
        """
        config = configparser.ConfigParser()
        config.read(self.config_file)

        oslist = []
        for os_name, var in sorted(self.os_dict.items()):
            if var.get() == 1:
                oslist.append(os_name)
        config['download']['os_list'] = ','.join(oslist)
        print(oslist)
        OS_LIST = oslist

        pkg_list = []
        for pkg_name, var in sorted(self.pkg_dict.items()):
            if var.get() == 1:
                pkg_list.append(pkg_name)
        config['software']['pkg_list'] = ','.join(pkg_list)

        with open(self.config_file, 'w+') as cfg:
            config.write(cfg, space_around_delimiters=False)

    def on_closing(self):
        """
        Note:
            closing the window and exit
        """
        self.root.destroy()
        sys.exit(1)


def win_main():
    """start gui application"""
    app = Win()
    app.run()


if __name__ == '__main__':
    win_main()
