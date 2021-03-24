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


class Win(object):
    """
    Note:
        the basic window
    """

    def __init__(self):
        self.config_file = os.path.join(CUR_DIR, 'config.ini')
        self.root = tk.Tk()
        self.root.title('离线安装下载器')
        self.root.geometry('300x{}'.format(30 * len(OS_LIST)))
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.check_list = []
        self.os_dict = {}
        self.read_config()
        last_row = 0
        for idx, os_name in enumerate(OS_LIST):
            var = tk.IntVar()
            if os_name in self.os_dict.keys():
                var = self.os_dict[os_name]
            tmp = tk.Checkbutton(self.root, width=30, text=os_name,
                    variable=var, anchor='w')
            tmp.grid(row=idx + 1, column=0)
            last_row = idx + 2
            self.check_list.append(tmp)
            self.os_dict[os_name] = var

        tk.Button(self.root, text='开始下载',
                command=self.start_download).grid(row=last_row, column=0)

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
        self.root.destroy()
        sys.exit(0)

    def read_config(self):
        """
        Note:
            read the configuration file
        """
        config = configparser.ConfigParser()
        config.read(self.config_file)
        all_os = [t.strip() for t in config['download']['os_list'].split(',')]
        for os_name in all_os:
            var = tk.IntVar()
            var.set(1)
            self.os_dict[os_name] = var

    def write_config(self):
        """
        Note:
            write the configuration file
        """
        config = configparser.ConfigParser()
        config.read(self.config_file)

        oslist = []
        for os_name, var in self.os_dict.items():
            if var.get() == 1:
                oslist.append(os_name)

        config['download']['os_list'] = ','.join(oslist)
        with open(self.config_file, 'w+') as cfg:
            config.write(cfg)

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
