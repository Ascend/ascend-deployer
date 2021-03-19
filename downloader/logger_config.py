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

import logging
import os
import platform

DOCUMENTION=r"""
Basic Log Configuration
"""


class BasicLogConfig(object):
    """basic logger configuration"""
    DEBUG = False

    LOG_DIR = os.path.dirname(os.path.realpath(__file__))
    if platform.system() == 'Linux':
        if 'site-pacakges' in LOG_DIR or 'dist-packages' in LOG_DIR:
            ad_home = os.getenv('ASCEND_DEPLOYER_HOME')
            if ad_home is None:
                ad_home = os.getenv('HOME')
            LOG_DIR = os.path.join(ad_home, 'ascend-deployer', 'downloader')

        if not os.path.exists(LOG_DIR):
            LOG_DIR = os.getcwd()
    else:
        LOG_DIR = os.getcwd()

    LOG_FILE = os.path.join(LOG_DIR, 'downloader.log')
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    LOG_FORMAT_STRING = \
            "[%(asctime)s] downloader %(levelname)s [pid:%(process)d] " \
            "[%(threadName)s] [%(filename)s:%(lineno)d %(funcName)s] %(message)s"
    LOG_LEVEL = logging.INFO


LOG_CONF = BasicLogConfig()

logging.basicConfig(filename=LOG_CONF.LOG_FILE,
             level=LOG_CONF.LOG_LEVEL,
             format=LOG_CONF.LOG_FORMAT_STRING,
             datefmt=LOG_CONF.LOG_DATE_FORMAT)


def get_logger(name):
    """get_logger"""
    return logging.getLogger(name)
