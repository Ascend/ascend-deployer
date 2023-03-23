import json
import glob
import os
import platform
import subprocess

meta_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meta_info.json")
print(meta_path)


def is_root():
    return 0 == os.getuid()


def uninstall_function():
    with open(meta_path) as fid:
        meta = json.load(fid)
        if is_root():
            current_working_path = meta["install_path"]["root"]
        else:
            current_working_path = meta["install_path"]["none-root"]
        current_working_path = os.path.expanduser(current_working_path)
        commands = meta.get("commands", {}).get("uninstall", "echo empty uninstall").format(path=current_working_path,
                                                                                            arch=platform.machine())
        print("running ", commands)
        cwd = os.getcwd()
        try:
            os.chdir(os.path.expanduser("~"))
            res = subprocess.check_output(commands.split(), stderr=subprocess.STDOUT, shell=False)
            print(str(res.decode()))
            if meta["pip_info"]["name"] == "ascend_driver":
                res = subprocess.check_output("bash /usr/local/Ascend/firmware/script/uninstall.sh".split(), stderr=subprocess.STDOUT, shell=False)
                print(str(res.decode()))
            remove_package(meta)

        except subprocess.CalledProcessError as e:
            print(e.output)
            raise e
        finally:
            os.chdir(cwd)


def remove_package(meta):
    for file in glob.glob("{}/{}-{}-*egg-info/installed-files.txt".format(
            os.path.dirname(os.path.dirname(meta_path)),
            meta["pip_info"]["name"], meta["pip_info"]["version"])):
        base_dir = os.path.dirname(file)
        with open(file) as fid:
            lines = fid.readlines()
        try:
            os.remove(file)
        except OSError:
            pass
        for line in lines:
            full_path = os.path.join(base_dir, line.rstrip())
            try:
                os.remove(full_path)
            except OSError:
                pass
            if not len(os.listdir(os.path.dirname(full_path))):
                try:
                    os.rmdir(os.path.dirname(full_path))
                except OSError:
                    pass
