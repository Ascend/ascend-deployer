"""setup package"""
import hashlib
import json
import os
import platform
import shutil
import subprocess
import ssl
import zipfile

try:
    import urllib2 as fetchlib
except:
    import urllib.request as fetchlib

import setuptools.command.install

from npu_info import get_npu

package_name = "PLACE_HOLDER"
max_size_per_time = 102400
meta_data = {}

with open("{}/meta_info.json".format(package_name)) as fid:
    meta_data = json.load(fid)

if not meta_data:
    raise Exception("meta not found")
url_map = meta_data.get("download_url", [])
home = os.path.expanduser("~")
cache_dir = os.path.join(home, ".cache")
package_dir = os.path.join(cache_dir, "ascend", package_name)

npu = get_npu().get("scene", "")


def get_url_and_sha256():
    arch = platform.machine()
    _selected_url, _sha256sum = "", ""
    for url_info in url_map:
        if arch == url_info["arch"] and url_info.get("type", "") in [npu, ""]:
            _selected_url = url_info["url"]
            _sha256sum = url_info["sha256sum"]
    if not _selected_url:
        raise Exception("url not found")
    return _selected_url, _sha256sum


select_url, sha256sum = get_url_and_sha256()
file_name = os.path.basename(select_url)
local_file = os.path.join(package_dir, file_name)


def get_current_os():
    os_release_file = "/etc/os-release"
    with open(os_release_file) as released_fid:
        os_release_content = released_fid.read(max_size_per_time)

    matching_os = {
        "ubuntu_18.04": "Ubuntu 18.04",
        "ubuntu_20.04": "Ubuntu 20.04",
        "openeuler_20.03": "openEuler 20.03",
        "openeuler_22.03": "openEuler 22.03",
        "centos_7": "CentOS Linux 7"
    }
    for os_name in matching_os.keys():
        if matching_os[os_name] in os_release_content:
            return os_name


def get_package_manager():
    current_os = get_current_os()
    managers = {
        "ubuntu_18.04": "apt-get install -y ",
        "ubuntu_20.04": "apt-get install -y ",
        "openeuler_20.03": "yum install -y ",
        "openeuler_22.03": "yum install -y ",
        "centos_7": "yum install -y "
    }
    return managers.get(current_os, "apt-get install -y ")


def get_file_prefix(file_name):
    file_names = file_name.split('.')
    prefix = '.'.join(file_names[0:len(file_names) - 1])
    return prefix


def unzip(file_path):
    file_names = file_name.split('.')
    prefix = '.'.join(file_names[0:len(file_names) - 1])
    base_dir = os.path.dirname(file_path)
    dst_dir = os.path.join(base_dir, prefix)
    print("{} -> {}".format(file_path, dst_dir))
    with zipfile.ZipFile(file_path) as zf:
        zf.extractall(dst_dir)
    return dst_dir


def install_zip_file(file_path):
    first_dir = unzip(file_path)
    file_name = os.path.basename(file_path)
    inner_file = os.path.join(first_dir, file_name)
    second_dir = unzip(inner_file)
    prefix = get_file_prefix(file_name)
    script = prefix + ".sh"
    if str(package_name) == "ascend_driver":
        script = "install.sh"
    cwd = os.getcwd()
    if os.getuid() == 0:
        log_path = "/var/log/ascend_seclog/"
    else:
        log_path = os.path.expanduser("~/var/log/ascend_seclog/")
        if str(package_name) == "ascend_driver":
            raise Exception("none-root user can not install driver!")
    try:
        os.chdir(second_dir)
        if str(package_name) == "ascend_driver":
            res = subprocess.check_output("bash {}/{} install all ".format(second_dir, script).split(),
                                          stderr=subprocess.STDOUT, shell=False)
        elif str(package_name) == "ascend_kernels":
            flag = "nnae"
            if os.getuid() == 0:
                if os.path.exists("/usr/local/Ascend/ascend-toolkit/set_env.sh"):
                    flag = "toolkit"
            else:
                if os.path.exists(os.path.expanduser("~/Ascend/ascend-toolkit/set_env.sh")):
                    flag = "toolkit"
            res = subprocess.check_output("bash {}/{} {} {} ".format(second_dir, script, log_path, flag).split(),
                                          stderr=subprocess.STDOUT, shell=False)
        else:
            res = subprocess.check_output("bash {}/{} {} ".format(second_dir, script, log_path).split(),
                                          stderr=subprocess.STDOUT, shell=False)
        print(str(res.decode()))
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise e
    finally:
        os.chdir(cwd)
        try:
            shutil.rmtree(first_dir)
        except OSError:
            pass


class install(setuptools.command.install.install, object):
    def run(self):
        print("run installing {}".format(local_file))
        if not os.path.exists(package_dir):
            os.makedirs(package_dir)
        download_url(select_url, sha256sum, local_file)
        if os.path.exists(local_file):
            install_zip_file(local_file)
        super(install, self).run()


def download_url(select_url, sha256sum, local_file):
    for i in range(5):
        if os.path.exists(local_file):
            sha256 = hashlib.sha256()
            with open(local_file, "rb") as fid:
                for block in iter(lambda: fid.read(max_size_per_time), b""):
                    sha256.update(block)
            hash = sha256.hexdigest()
            if hash == sha256sum or str(sha256sum) == "":
                break
        print("downloading ", select_url, " to ", local_file, i, " times")
        try:
            os.remove(local_file)
        except OSError:
            pass
        if str(os.environ.get("NO_VERIFY_SSL", "disable")) == "enable":
            context = ssl._create_unverified_context()
            file_stream = fetchlib.urlopen(select_url, context=context)
        else:
            file_stream = fetchlib.urlopen(select_url)
        with open(local_file, "wb") as fid:
            while True:
                content = file_stream.read(max_size_per_time)
                fid.write(content)
                if len(content) != max_size_per_time:
                    break
    else:
        raise Exception("download file failed")
    print("download ok")


def install_system_dependency():
    print("run installing system requires...")
    current_os = get_current_os()
    packages = meta_data.get("system_requires", {}).get(current_os, [])
    real_packages = " ".join(map(lambda p: p['name'], packages))
    if not real_packages.strip():
        return
    if os.getuid() != 0:
        return
    command = "{manager} {packages}".format(manager=get_package_manager(), packages=real_packages)
    print(command)
    try:
        res = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        print(str(res.decode()))
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise e
    return


if sys.argv[1] == 'egg_info':
    install_system_dependency()


setuptools.setup(
    include_package_data = True,
    cmdclass = {'install': install},
    entry_points = {
        "console_scripts": [
            "uninstall_{}={}:uninstall_function".format(package_name, package_name)
        ]
    },
    name = str(meta_data["pip_info"]["name"]),
    url = str(meta_data["pip_info"]["url"]),
    platforms = meta_data["pip_info"]["platforms"],
    version = str(meta_data["pip_info"]["version"]),
    python_requires= str(meta_data["pip_info"]["python_requires"]),
    install_requires = [str(req) for req in meta_data["pip_info"]["install_requires"]],
    packages = [str(meta_data["pip_info"]["packages"][0])],
    description = str(meta_data["pip_info"]["description"])
)
