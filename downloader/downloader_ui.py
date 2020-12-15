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
import subprocess
import configparser
import tkinter as tk

os_list = [
'CentOS_7.6_aarch64',
'CentOS_7.6_x86_64',
'CentOS_8.2_aarch64',
'CentOS_8.2_x86_64',
'Ubuntu_18.04_aarch64',
'Ubuntu_18.04_x86_64',
'BigCloud_7.6_aarch64',
'BigCloud_7.6_x86_64',
'SLES_12.4_x86_64'
]

CUR_DIR = os.path.dirname(os.path.realpath(__file__))

class Win(object):
    def __init__(self):
        self.config_file = os.path.join(CUR_DIR, 'config.ini')
        self.root = tk.Tk()
        self.root.title('离线安装下载器')
        self.root.geometry('300x300')
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.check_list = []
        self.os_dict = {}
        self.read_config()
        last_row = 0
        for idx, os_name in enumerate(os_list):
            var = tk.IntVar()
            if os_name in self.os_dict.keys():
                var = self.os_dict[os_name]
            tmp = tk.Checkbutton(self.root, width=30, text = os_name, variable = var, anchor = 'w')
            tmp.grid(row = idx + 1, column = 0)
            last_row = idx + 2
            self.check_list.append(tmp)
            self.os_dict[os_name] = var

        tk.Button(self.root, text = '开始下载', command = lambda : self.start_download()).grid(row = last_row, column = 0);

    def run(self):
        self.root.mainloop()

    def start_download(self):
        self.write_config()
        self.root.destroy()

    def read_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        all_os = [ tmp.strip() for tmp in config['download']['os_list'].split(',') ]
        for os_name in all_os:
            var = tk.IntVar()
            var.set(1)
            self.os_dict[os_name] = var

    def write_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)

        oslist = []
        for k, v in self.os_dict.items():
            if v.get() == 1:
                oslist.append(k)

        config['download']['os_list'] = ','.join(oslist)
        with open(self.config_file, 'w+') as cfg:
            config.write(cfg)

    def on_closing(self):
        self.root.destroy()

if __name__ == '__main__':
    app = Win()
    app.run()
