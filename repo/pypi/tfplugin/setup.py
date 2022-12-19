# Copyright 2022 Huawei Technologies Co., Ltd
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
"""setup package."""
import os
import stat
import time
import shutil
import datetime
import setuptools
import platform

from setuptools.command.install import install

package_name = "tfplugin"
arch = platform.processor()

url_map = {}
url_map['aarch64'] = "https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/CANN/CANN%206.0.RC1/Ascend-cann-tfplugin_6.0.RC1_linux-aarch64.zip"

url_map['x86_64'] = "https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/CANN/CANN%206.0.RC1/Ascend-cann-tfplugin_6.0.RC1_linux-x86_64.zip"

home = os.path.expanduser('~')
cache_dir = os.path.join(home, ".cache")
package_dir = os.path.join(cache_dir, "ascend", package_name)
file_name = os.path.basename(url_map[arch])
local_file = os.path.join(package_dir, file_name)


def get_file_prefix(file_name):
    file_names = file_name.split('.')
    prefix = '.'.join(file_names[0:len(file_names) - 1])
    return prefix

def unzip(file_path):
    file_names = file_name.split('.')
    prefix = '.'.join(file_names[0:len(file_names) - 1])
    base_dir = os.path.dirname(file_path)
    dst_dir = os.path.join(base_dir, prefix)
    shutil.unpack_archive(file_path, dst_dir)
    return dst_dir

def install_zip_file(file_path):
    first_dir = unzip(file_path)
    file_name = os.path.basename(file_path)
    inner_file = os.path.join(first_dir, file_name)
    second_dir = unzip(inner_file)
    prefix = get_file_prefix(file_name)
    script = prefix + ".sh"
    cwd =os.getcwd()
    try:
        print(f"package dir = {second_dir} install script = {script}")
        os.chdir(second_dir)
        os.system("bash {0} install".format(script))
    except Exception as e:
        raise e
    finally:
        os.chdir(cwd)

class InstallWrapper(install):

    def run(self):
        try:
            if not os.path.exists(package_dir):
                os.makedirs(package_dir)

            if not os.path.exists(local_file):
                os.system("curl -o {0} {1}".format(local_file, url_map[arch]))

            if os.path.exists(local_file):
                install_zip_file(local_file)
            install.run(self)
        except Exception as e:
            print(f"install failed {e}", file=sys.stderr)
            exit(-1)

setuptools.setup(
    name=package_name,
    version='6.0.rc1',
    platforms=['Linux'],
    description=('ascend tensorflow plugin'),
    url = 'https://hiascend.com',
    long_description='ascend toolkit',
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
    license = 'Apache',
    include_package_data = True,
    packages = ['tfplugin'],
    python_requires= '>= 3.6',
    cmdclass = {'install': InstallWrapper},
)
