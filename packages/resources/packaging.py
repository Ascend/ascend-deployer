import os
import sys
import shutil
import json

def main():
    version = sys.argv[1]
    name = sys.argv[2]
    os.makedirs("./working/{}/{}".format(name, name))
    shutil.copy("setup.py", "./working/{}/".format(name))
    shutil.copy("npu_info.py", "./working/{}/".format(name))
    os.system('sed -i "s/PLACE_HOLDER/{}/g" ./working/{}/setup.py'.format(name, name))
    shutil.copy("__init__.py", "./working/{}/{}".format(name, name))
    shutil.copy("{}/{}/MANIFEST.in".format(version, name), "./working/{}/".format(name))
    os.system("cp {}/{}/* ./working/{}/{} -fa".format(version, name, name, name))
    with open("./working/{}/{}/meta_info.json".format(name, name)) as fid:
        data = json.load(fid)
        inner_version = data['pip_info']['version']
    os.system("cd ./working/{}; zip -r ../{}-{}.zip . ; cd -".format(name, name, inner_version))

if __name__ == "__main__":
    main()