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
import stat

from logging.handlers import RotatingFileHandler


DOCUMENTION = r"""
Basic Log Configuration
"""


class BasicLogConfig(object):
    """
    basic logger configuration
    """
    DEBUG = False

    CUR_DIR = os.path.dirname(os.path.realpath(__file__))
    if 'site-packages' not in CUR_DIR and 'dist-packages' not in CUR_DIR:
        deployer_home = os.path.dirname(CUR_DIR)
        LOG_FILE = os.path.join(deployer_home, 'downloader.log')
    else:
        deployer_home = ''
        if platform.system() == 'Linux':
            deployer_home = os.getenv('HOME')
            if os.getenv('ASCEND_DEPLOYER_HOME') is not None:
                deployer_home = os.getenv('ASCEND_DEPLOYER_HOME')
        else:
            deployer_home = os.getcwd()
        parent_dir = os.path.join(deployer_home, 'ascend-deployer')
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, mode=0o750, exist_ok=True)
        LOG_FILE = os.path.join(deployer_home, 'ascend-deployer', 'downloader.log')
    if not os.path.exists(LOG_FILE):
        os.close(
            os.open(
                LOG_FILE, os.O_CREAT,
                stat.S_IRUSR | stat.S_IWUSR
            )
        )
    else:
        os.chmod(LOG_FILE, stat.S_IRUSR | stat.S_IWUSR)
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


ROTATING_FILE_LOG_CONF = dict(
    filename=LOG_CONF.LOG_FILE,
    mode='a',
    maxBytes=20 * 1024 * 1024,
    backupCount=5,
    encoding="UTF-8"
)


def get_logger(name):
    """
    get_logger
    """
    logger = logging.getLogger(name)
    rotating_log_handler = RotatingFileHandler(**ROTATING_FILE_LOG_CONF)
    logger.addHandler(rotating_log_handler)
    return logger
