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


CUR_DIR = os.path.dirname(os.path.realpath(__file__))
OS_LIST = os.listdir(os.path.join(CUR_DIR, 'config'))
PKG_LIST = [pkg.split(".json")[0] for pkg in os.listdir(os.path.join(CUR_DIR, 'software'))]


class Win(object):
    """
    the basic window
    """

    def __init__(self):
        self.config_file = os.path.join(CUR_DIR, 'config.ini')
        self.root = tk.Tk()
        self.root.title('离线安装下载器')
        self.root.geometry('620x500')
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.frame_left = self._create_frame("OS_LIST", 0, 0, 250, 480, "left")
        self.frame_right = self._create_frame("PKG_LIST", 0, 2, 250, 480, "left")
        self.frame_bottom = tk.LabelFrame(
            tk.Button(self.root, text="开始下载").grid(row=0, column=1)
        )
        self.frame_bottom.grid(row=0, column=1)
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

    def _create_frame(self, text, row, column, width, heigh, pack_side):
        box = tk.LabelFrame(self.root, text=text)
        box.grid(row=row, column=column)
        canvas = tk.Canvas(box)
        canvas.pack(side=pack_side, fill="both", expand=True)
        frame = tk.Frame(canvas)
        scrollbar = tk.Scrollbar(box, orient="vertical", command=canvas.yview)
        canvas.configure(
            yscrollcommand=scrollbar.set, width=width, height=heigh
        )
        scrollbar.pack(side=pack_side, fill="y")
        frame.bind(
            "<Configure>",
            lambda event, canvas=canvas: self._on_frame_configure(canvas)
        )
        canvas.create_window((4, 4), window=frame, anchor="nw", tags="frame")
        return frame

    @staticmethod
    def _on_frame_configure(canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def display(self):
        """
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
        the main loop of the window
        """
        self.root.mainloop()

    def start_download(self):
        """
        start downading, the window will exit
        """
        self.write_config()
        config = configparser.ConfigParser()
        config.read(self.config_file)

        if not config['download']['os_list'] and not config['software']['pkg_list']:
            tkinter.messagebox.showwarning(title="Warning", message="至少勾选一项")
        elif not config['download']['os_list'] and "MindSpore" in config['software']['pkg_list']:
            tkinter.messagebox.showwarning(title="Warning", message="下载MindSpore时OS_LIST至少勾选一项")
        else:
            self.root.destroy()
            sys.exit(0)

    def read_config(self):
        """
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
        fd = os.open(self.config_file, os.O_WRONLY, 0o640)
        cfg = os.fdopen(fd, 'w+')
        cfg.truncate()
        config.write(cfg, space_around_delimiters=False)
        cfg.close()

    def select_os_all(self, opt):
        """
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
        closing the window and exit
        """
        self.root.destroy()
        sys.exit(1)


def win_main():
    """
    start gui application
    """
    app = Win()
    app.run()


if __name__ == '__main__':
    win_main()
