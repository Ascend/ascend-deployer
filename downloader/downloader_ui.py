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


CUR_DIR = os.path.dirname(os.path.realpath(__file__))
OS_LIST = os.listdir(os.path.join(CUR_DIR, 'config'))
PKG_LIST = [pkg.split(".json")[0] for pkg in os.listdir(os.path.join(CUR_DIR, 'software'))]


class Win(object):
    """
    Note:
        the basic window
    """

    def __init__(self):
        self.config_file = os.path.join(CUR_DIR, 'config.ini')
        self.root = tk.Tk()
        self.root.title('离线安装下载器')
        self.root.geometry('600x{}'.format(30 * len(OS_LIST)))
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.frame_left = tk.LabelFrame(self.root, text="OS_LIST")
        self.frame_left.pack(fill="both", side="left", expand="yes")
        self.frame_right = tk.LabelFrame(self.root, text="PKG_LIST")
        self.frame_right.pack(fill="both", side="right", expand="yes")
        self.frame_bottom = tk.LabelFrame(self.root)
        self.frame_bottom.pack(side="bottom")
        self.all_opt = tk.IntVar()
        self.all_opt.set(1)
        self.all_not_opt = tk.IntVar()
        self.all_not_opt.set(0)
        self.os_dict = {}
        self.pkg_dict = {}
        tk.Button(self.frame_left, text="全选",
                  command=lambda: self.select_os_all(self.all_opt)).grid(row=0, column=0, sticky='w')
        tk.Button(self.frame_left, text="全不选",
                  command=lambda: self.select_os_all(self.all_not_opt)).grid(row=0, column=0)
        tk.Button(self.frame_right, text="全选",
                  command=lambda: self.select_pkg_all(self.all_opt)).grid(row=0, column=0, sticky='w')
        tk.Button(self.frame_right, text="全不选",
                  command=lambda: self.select_pkg_all(self.all_not_opt)).grid(row=0, column=0)
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
            tk.Checkbutton(self.frame_left, width=30, text=os_name,
                           variable=var, anchor='w').grid(row=os_idx,
                                                          column=0)
        for pkg_name, var in sorted(self.pkg_dict.items()):
            pkg_idx += 1
            tk.Checkbutton(self.frame_right, width=30, text=pkg_name,
                           variable=var, anchor='w').grid(row=pkg_idx,
                                                          column=0)

    def run(self):
        """
        Note:
            the main loop of the window
        """
        self.root.mainloop()

    def start_download(self):
        """
        Note:
            start downading, the window will exit
        """
        self.write_config()
        config = configparser.ConfigParser()
        config.read(self.config_file)

        if config['download']['os_list'] or config['software']['pkg_list']:
            self.root.destroy()
            sys.exit(0)
        else:
            tk.messagebox.showwarning(title="Warning", message="至少勾选一项")

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

        pkg_list = []
        for pkg_name, var in sorted(self.pkg_dict.items()):
            if var.get() == 1:
                pkg_list.append(pkg_name)
        config['software']['pkg_list'] = ','.join(pkg_list)

        with open(self.config_file, 'w+') as cfg:
            config.write(cfg, space_around_delimiters=False)

    def select_os_all(self, opt):
        """
        Note:
            select os all
        """
        if opt.get() == 1:
            for os_name in OS_LIST:
                self.os_dict[os_name].set(1)
        else:
            for os_name in OS_LIST:
                self.os_dict[os_name].set(0)

        self.display()

    def select_pkg_all(self, opt):
        """
        Note:
            select pkg all
        """
        if opt.get() == 1:
            for pkg_name in PKG_LIST:
                self.pkg_dict[pkg_name].set(1)
        else:
            for pkg_name in PKG_LIST:
                self.pkg_dict[pkg_name].set(0)

        self.display()

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
