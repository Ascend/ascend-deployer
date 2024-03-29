import glob
import json
import os
import platform
import shlex
import subprocess
import sys


class ChipMetaData():
    "metadata includes vid, did, svid, sdid, arch"

    def __init__(self, vid, did, svid, sdid, arch):
        self.vid = vid
        self.did = did
        self.svid = svid
        self.sdid = sdid
        self.arch = arch

    def __hash__(self):
        return hash((self.vid, self.did, self.svid, self.sdid, self.arch))

    def __eq__(self, other):
        return (self.vid, self.did, self.svid, self.sdid, self.arch) == (
            other.vid, other.did, other.svid, other.sdid, other.arch)


CHIPS_DICT = {
    ChipMetaData('0x19e5', '0xd100', '0x0200', '0x0100',
                 'x86_64'): 'A300-3010',
    ChipMetaData('0x19e5', '0xd100', '0x0200', '0x0100',
                 'aarch64'): 'A300-3000',
    ChipMetaData('0x19e5', '0xd801', '0x0200', '0x0100',
                 'aarch64'): 'A300T-9000',
    ChipMetaData('0x19e5', '0xd801', '0x0200', '0x0100',
                 'x86_64'): 'A300T-9000',
    ChipMetaData('0x19e5', '0xd802', '0x0200', '0x0100',
                 'aarch64'): 'A900T',
    ChipMetaData('0x19e5', '0xd500', '0x0200', '0x0100',
                 'aarch64'): 'A300i-pro',
    ChipMetaData('0x19e5', '0xd500', '0x0200', '0x0100',
                 'x86_64'): 'A300i-pro',
    ChipMetaData('0x19e5', '0xd500', '0x0200', '0x0110',
                 'x86_64'): 'A300i-duo',
    ChipMetaData('0x19e5', '0xd500', '0x0200', '0x0110',
                 'aarch64'): 'A300i-duo',
}
FIND_METADATA = 'grep 0x1200 /sys/bus/pci/devices/*/class | awk -F \/ \'{print $6}\''
FIND_PRODUCT_CMD = 'dmidecode -t 1'
FIND_SOC_PRODUCT_CMD = 'dmidecode -t 2'
FIND_PRODUCT = 'dmidecode -t 1 | grep Product | awk -F: \'{print $2}\''


def get_profile_model(arch, model):
    if model == '--':
        return 'unknown'

    if 'Atlas' in model and 'Model' in model:
        model = "A" + model.split("(")[0].split()[1].strip() + \
                "-" + model.split(")")[0].split("Model")[1].strip()

    if model == 'A300T-9000':
        if arch == 'aarch64':
            model = 'A800-9000'
        else:
            model = 'A800-9010'

    if model in ['A500-3000', 'A800-3000']:
        model = 'A300-3000'
    if model == 'A800-3010':
        model = 'A300-3010'

    return model


def get_scene(profile_model):
    scene = ''
    if profile_model in ['A300i-pro']:
        scene = 'a300i'
    if profile_model in ['A300-3000', 'A300-3010', 'A200-3000']:
        scene = 'infer'
    if profile_model in ['A800-9000', 'A800-9010', 'Atlas 900 Compute Node']:
        scene = 'train'
    if profile_model in ['A900T']:
        scene = 'a910b'
    if profile_model in ['A300i-duo']:
        scene = 'a300iduo'

    return scene


def get_chip_info(vid, did, svid, sdid, arch):
    chip_meta_data = ChipMetaData(vid.lower(), did.lower(), svid, sdid, arch)
    return CHIPS_DICT.get(chip_meta_data, '--')


def check_metadata_file_existance(bdf_path):
    metadata_file = os.path.join(bdf_path, 'vendor')
    ret = os.path.exists(metadata_file)
    if not ret:
        return False

    metadata_file = os.path.join(bdf_path, 'device')
    ret = os.path.exists(metadata_file)
    if not ret:
        return False

    metadata_file = os.path.join(bdf_path, 'subsystem_device')
    ret = os.path.exists(metadata_file)
    if not ret:
        return False

    metadata_file = os.path.join(bdf_path, 'subsystem_vendor')
    ret = os.path.exists(metadata_file)
    if not ret:
        return False

    return True


def get_metadatas(bdf_path):
    metadata_file = os.path.join(bdf_path, 'device')
    with open(metadata_file) as f:
        did = f.read().replace('\t', '').replace('\n', '')
        if not did:
            return {}

    metadata_file = os.path.join(bdf_path, 'vendor')
    with open(metadata_file) as f:
        vid = f.read().replace('\t', '').replace('\n', '')
        if not vid:
            return {}

    metadata_file = os.path.join(bdf_path, 'subsystem_device')
    with open(metadata_file) as f:
        sdid = f.read().replace('\t', '').replace('\n', '')
        if not sdid:
            return {}

    metadata_file = os.path.join(bdf_path, 'subsystem_vendor')
    with open(metadata_file) as f:
        svid = f.read().replace('\t', '').replace('\n', '')
        if not svid:
            return {}

    return dict(did=did, vid=vid, sdid=sdid, svid=svid)


def get_model():
    bdf_file_paths = []
    DEVNULL = open(os.devnull, 'w')
    for candidate_dir in glob.glob('/sys/bus/pci/devices/*'):
        find_metadata_cmd = ["grep", "0x1200",
                             os.path.join(candidate_dir, "class")]
        return_code = subprocess.call(find_metadata_cmd, shell=False,
                                      stdout=DEVNULL, stderr=subprocess.STDOUT)
        if return_code == 0:
            bdf_file_paths.append(candidate_dir)
    for bdf_file_path in bdf_file_paths:
        model = _get_model(bdf_file_path, DEVNULL)
        if model != '--':
            return model
    try:
        cp = subprocess.Popen(args=shlex.split(FIND_SOC_PRODUCT_CMD),
                              shell=False,
                              universal_newlines=True,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    except Exception:
        return '--'
    dmi_info_lines = cp.stdout.readlines()
    raw_product = ""
    for i in dmi_info_lines:
        if 'Product' in i:
            product_infos = i.split(':')
            if len(product_infos) < 2:
                return '--'
            raw_product = product_infos[1]
            break
    product = raw_product.replace('\t', '').replace('\n', '').strip()
    if product == 'Atlas 200I SoC A1':
        return product
    return '--'

def _get_model(bdf_file_path, DEVNULL):
    ret = check_metadata_file_existance(bdf_file_path)
    if not ret:
        return '--'

    metadata_dict = get_metadatas(bdf_file_path)
    if not metadata_dict:
        return '--'

    arch = platform.machine()

    chip_info = get_chip_info(
        metadata_dict['vid'], metadata_dict['did'], metadata_dict['svid'],
        metadata_dict['sdid'], arch)
    if chip_info == '--' or chip_info == 'A300i-pro':
        return chip_info

    find_a500_cmd = ["stat", "/run/board_cfg.ini"]
    return_code = subprocess.call(find_a500_cmd, shell=False,
                                  stdout=DEVNULL, stderr=subprocess.STDOUT)
    if return_code == 0:
        return "Atlas 500 (Model 3000)"

    try:
        cp = subprocess.Popen(args=shlex.split(FIND_PRODUCT_CMD),
                              shell=False,
                              universal_newlines=True,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    except Exception:
        return chip_info
    dmi_info_lines = cp.stdout.readlines()
    raw_product = ""
    for item in dmi_info_lines:
        if 'Product' in item:
            product_infos = item.split(':')
            if len(product_infos) < 2:
                return chip_info
            raw_product = product_infos[1]
            break
    product = raw_product.replace('\t', '').replace('\n', '').strip()
    product_name = (
        "Atlas 800 (Model 9000)",
        "Atlas 800 (Model 9010)",
        "Atlas 900 (Model 9000)",
        "Atlas 900 Compute Node",
        "Atlas 500 Pro (Model 3000)",
        "Atlas 500 Pro(Model 3000)",
        "Atlas 500 (Model 3000)",
    )
    if product in product_name:
        return product

    return chip_info


def get_product(model):
    product_dict = {
        'Atlas 800 (Model 9000)': 'A800',
        'Atlas 800 (Model 9010)': 'A800',
        'Atlas 900 (Model 9000)': 'A900',
        'Atlas 900 Compute Node': 'A900',
        'A300T-9000': 'A300t',
        'Atlas 800 (Model 3000)': 'A300',
        'Atlas 800 (Model 3010)': 'A300',
        'Atlas 500 Pro (Model 3000)': 'A300',
        'Atlas 500 Pro(Model 3000)': 'A300',
        'A300-3010': 'A300',
        'A300-3000': 'A300',
        'Atlas 500 (Model 3000)': 'A300',
        'A300i-pro': 'A300i',
        'A200-3000': 'A200',
        'A300i-duo': 'Atlas-300i-duo'
    }
    if model in product_dict.keys():
        return product_dict[model]
    return ""


def get_model_number(model):
    model_dict = {
        'Atlas 800 (Model 9000)': '9000',
        'Atlas 800 (Model 9010)': '9010',
        'Atlas 900 (Model 9000)': '9000',
        'Atlas 900 Compute Node': '9000',
        'A300T-9000': '9000',
        'Atlas 800 (Model 3000)': '3000',
        'Atlas 800 (Model 3010)': '3010',
        'Atlas 500 Pro (Model 3000)': '3000',
        'Atlas 500 Pro(Model 3000)': '3000',
        'A300-3010': '3010',
        'A300-3000': '3000',
        'Atlas 500 (Model 3000)': '3000',
        'A300i-pro': 'pro',
        'A200-3000': '3000',
        'A300i-duo': 'duo'
    }
    if model in model_dict.keys():
        return model_dict[model]
    return ""


ALL_MODEL_DICT = {
'Atlas 800 (Model 9000)': 'A800-9000',
'Atlas 800 (Model 9010)': 'A800-9010',
'A300T-9000': 'A300t-9000',
'Atlas 800 (Model 3000)': 'A300-3000',
'Atlas 800 (Model 3010)': 'A300-3010',
'Atlas 500 Pro (Model 3000)': 'A300-3000',
'Atlas 500 Pro(Model 3000)': 'A300-3000',
'A300-3010': 'A300-3010',
'A300-3000': 'A300-3000',
'Atlas 500 (Model 3000)': 'A300-3000',
'A300i-pro': 'A300i-pro',
'A300i-duo': 'A300i-duo'
}


def get_npu():
    arch = platform.machine()
    model = get_model()
    profile_model = get_profile_model(arch, model)
    scene = get_scene(profile_model)

    ret = {
        "model": model,
        "scene": scene,
        "python375_installed": os.path.exists('/usr/local/python3.7.5') if os.getuid() == 0 else os.path.exists(os.path.expanduser('~/.local/python3.7.5')),
        "product": get_product(model),
        "model_number": get_model_number(model),
        "all_model_dict": ALL_MODEL_DICT
    }
    return ret

def is_installed():
    if os.path.exists("/usr/local/Ascend/driver"):
        return True
    return False
