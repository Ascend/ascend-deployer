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
"""setup package."""
import os
import stat
import shutil
import setuptools

if os.path.exists('ascend_deployer'):
    shutil.rmtree('ascend_deployer')

if os.path.exists('dist'):
    shutil.rmtree('dist')

os.mkdir('ascend_deployer')
shutil.copytree('downloader', 'ascend_deployer/downloader')
shutil.copytree('playbooks', 'ascend_deployer/playbooks')
shutil.copyfile('install.sh', 'ascend_deployer/install.sh')
shutil.copyfile('start_download.sh', 'ascend_deployer/start_download.sh')
shutil.copyfile('inventory_file', 'ascend_deployer/inventory_file')
shutil.copyfile('ansible.cfg', 'ascend_deployer/ansible.cfg')
shutil.copyfile('README.md', 'ascend_deployer/README.md')
shutil.copyfile('README.en.md', 'ascend_deployer/README.en.md')
open('ascend_deployer/__init__.py', 'w+').close()
os.chmod('ascend_deployer/install.sh', stat.S_IEXEC | stat.S_IRUSR | stat.S_IRGRP | stat.S_IXGRP)
os.chmod('ascend_deployer/start_download.sh', stat.S_IEXEC | stat.S_IRUSR | stat.S_IRGRP | stat.S_IXGRP)
shutil.copyfile('LICENSE', 'ascend_deployer/LICENSE')


with open('README.md', encoding='utf-8') as f:
    readme = f.read()

setuptools.setup(
    name='ascend-deployer',
    version='0.0.3',
    description=('ascend offline installer'),
    url = 'https://gitee.com/ascend/ascend-deployer',
    long_description_content_type = "text/markdown",
    long_description=readme,
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
    license = 'Apache',
    python_requires= '>= 3.6',
    include_package_data = True,
    package_dir = {'downloader':'ascend_deployer/downloader', 'playbooks':'ascend_deployer/playbooks'},
    packages = ['ascend_deployer'],
    scripts = ['tools/ascend-deployer'],
    entry_points={  # Optional
        'console_scripts': [
            'ascend-download=ascend_deployer.downloader.downloader:main',
        ]
    },
)

if os.path.exists('ascend_deployer.egg-info'):
    shutil.rmtree('ascend_deployer.egg-info')

if os.path.exists('ascend_deployer'):
    shutil.rmtree('ascend_deployer')

if os.path.exists('build'):
    shutil.rmtree('build')
