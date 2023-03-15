# -*- coding:utf-8 -*-
import csv
import logging
import os.path
import subprocess
import sys
import time

PARAMETER_DICT = {'character': 0, 'ip': 1, 'user': 2, 'pwd': 3, 'become_pwd': 4, 'host': 5, 'api': 6, 'interface': 7}

CSV_SIZE = 1024 * 1024
SCENE_LIST = ['1', '2', '3', '4']
TOOLS_LIST = ['npu-exporter', 'noded', 'hccl-controller']
CHARACTER_DICT = {'master': 0, 'worker': 1, 'mef': 2}
MEF_OPTIONS = {'no': 0, 'mef-only': 1, "mef+k8s": 2}
RAW_FILE = """#           *********************主机变量配置区域*********************
# 配置信息示例:10.10.10.10 ansible_ssh_user="test" ansible_become_password="test1234" set_hostname=master-1 k8s_api_server_ip=10.10.10.10 kube_interface=enp125s0f0
# 示例说明:
# 10.10.10.10:服务器的ip地址。
# ansible_ssh_user:ssh登录远程服务器的账号，该账号可以是普通账号，也可以是root账号，账号必须有sudo权限，且权限与root相近；如果配置了免密登录且root用户可以登录，则无需配置ansible_ssh_pass和ansible_become_password变量。ansible_ssh_user仍需配置。
# ansible_ssh_pass:ssh登录远程服务器账号的密码
# ansible_ssh_port:ssh连接的端口，如果使用了非默认的22端口，则需要增加该变量
# ansible_become_password:账号执行sudo命令时输入的密码，该变量与账号ssh登录时输入的密码一致。root账号可不设置该变量，如果ansible_ssh_user中配置的是普通账号且/etc/sudoers中账号配置了NOPASSWD选项，则该变量可不设置，否则必须设置
# set_hostname:设置节点在K8s集群中的节点名字,建议用“[a-z]-[0-9]”的格式；如果已有K8s集群，则该名字需要为节点在K8s中的名字，不可随意填写。
# k8s_api_server_ip:k8s对外提供服务的入口，配置为master节点的IP地址。
# kube_interface:对应服务器ip地址网卡名字，单master场景下可以不设置
# [master]下配置控制节点信息,第一行信息为k8s主控节点信息，配置参考注释
# [master]下面给出几个配置示例
# 第一行 root账号配置了免密登录，使用root账号登录，且ssh使用22端口，单master场景
# 第二行 test账号配置了免密登录，使用test账号登录，ssh使用默认22端口，未配置NOPASSWD，多master场景
# 第三行 未配置免密登录，使用普通账号登录，ssh使用默认22端口，配置了NOPASSWD，多master场景
# 第四行 未配置免密登录，使用普通账号登录，ssh使用默认22端口，未配置了NOPASSWD，多master场景
[master]
{master}
#10.10.10.10 ansible_ssh_user="root" ansible_ssh_port=22 set_hostname=master-1 k8s_api_server_ip=10.10.10.10
#10.10.10.11 ansible_ssh_user="test" ansible_become_password="test1234" set_hostname=master-2 k8s_api_server_ip=10.10.10.11 kube_interface=enp125s0f0
#10.10.10.12 ansible_ssh_user="test" ansible_ssh_pass="test1234" set_hostname=master-3 k8s_api_server_ip=10.10.10.12 kube_interface=enp125s0f0
#10.10.10.13 ansible_ssh_user="test" ansible_ssh_pass="test1234" ansible_become_password="test1234" set_hostname=master-4 k8s_api_server_ip=10.10.10.13 kube_interface=enp125s0f0

# worker,工作节点信息，可以配置多个工作节点，每个节点信息占据一行，配置参考注释
# 已在[master]中的节点并且设置了set_hostname，则[worker]中不需要再配置set_hostname，如下面[worker]配置的第一行, 如有驱动安装, ansible_ssh_user需配置为root
[worker]
{worker}
#10.10.10.12 ansible_ssh_user="root" ansible_ssh_port=22
#10.10.10.13 ansible_ssh_user="test" ansible_ssh_pass="test1234" ansible_become_password="test1234" ansible_ssh_port=9090
#10.10.10.14 ansible_ssh_user="test" ansible_ssh_pass="test1234" ansible_become_password="test1234" ansible_ssh_port=9090 set_hostname=worker-1

# mef,待安装的mef节点，配置参考注释
[mef]
{mef}
#10.10.10.12 ansible_ssh_user="root" ansible_ssh_port=22

# k8s集群中存在与master节点架构不一致的服务器时，并且该节点(或多个异构节点)会部署MindX DL，任选其中一台异构节点配置到如下主机组即可，配置参考注释
[other_build_image]
#10.10.10.11 ansible_ssh_user="test" ansible_ssh_pass="test1234" ansible_become_password="test1234" ansible_ssh_port=9090
#           *********************以下为worker变量配置区域**************************
[worker:vars]
user=HwHiAiUser
group=HwHiAiUser

#           *********************以下为全局变量配置区域**************************
[all:vars]
# 场景1安装组件: Docker, Kubernetes, Ascend Docker Runtime, Ascend Device Plugin, Volcano, HCCL-Controller, NodeD, NPU-Exporter
# 场景2安装组件: Ascend Docker Runtime, Ascend Device Plugin, Volcano，HCCL-Controller(可选), NodeD(可选), NPU-Exporter(可选)
# 场景3安装组件: Ascend Docker Runtime, Ascend Device Plugin, NPU-Exporter(可选)
# 场景4安装组件: Docker, Kubernetes
# SCENE_NUM:安装场景选择，可选1，2，3，4场景,默认场景1
SCENE_NUM={sn}

# EXTRA_COMPONENT: 为可选组件，组件间逗号隔开，可选值如下；
# 	npu-exporter     表示安装NPU-Exporter组件
# 	noded            表示安装NodeD组件
# 	hccl-controller  表示安装HCCL-Controller组件
# 配置示例：EXTRA_COMPONENT="npu-exporter,noded,hccl-controller"
EXTRA_COMPONENT="{extra}"

# k8s集群使用的子网IP网段，如果与服务器IP网段重合，需要修改下面的值为其他私有网段。如：192.168.0.0/16
POD_NETWORK_CIDR="192.168.0.0/16"

# 多master场景下配置虚拟IP，kube_vip需跟k8s集群节点ip在同一子网，且为闲置、未被他人使用的ip
KUBE_VIP=""

# 使用harbor镜像仓时配置
# harbor服务地址，格式为ip:port，不含协议，如"192.0.0.1:1234"
HARBOR_SERVER=""
# 配置harbor管理员账号信息，用于在harbor中创建名为项目，以及推送、拉取k8s相关、MindX DL相关的镜像
HARBOR_ADMIN_USER=""
HARBOR_ADMIN_PASSWORD=""
# MindX DL相关镜像的项目公开状态，默认为私有，可选值false或true
HARBOR_PUBLIC_PROJECT="false"
# 使用https协议时，配置harbor镜像仓根CA文件路径
HARBOR_CA_FILE=""
"""


class InventoryDTO:
    def __init__(self):
        self.character = ""
        self.ip = ""
        self.user = ""
        self.pwd = ""
        self.become_pwd = ""
        self.hostName = ""
        self.api = ""
        self.interface = ""
        self.master = ""
        self.worker = ""
        self.mef = ""

    def solve_device(self):
        if self.character == 'master':
            self.append_node(CHARACTER_DICT['master'])
        elif self.character == 'worker':
            self.append_node(CHARACTER_DICT['worker'])
        elif self.character == 'mef':
            self.append_node(CHARACTER_DICT['mef'])
        self.character = ''
        self.ip = ''
        self.user = ''
        self.pwd = ''
        self.become_pwd = ''
        self.hostName = ''
        self.api = ''
        self.interface = ''

    def append_node(self, num):
        attr_str = ''
        if self.ip == '':
            return
        attr_str += self.ip
        attr_str += self.get_item("ansible_ssh_user", self.user)
        attr_str += self.get_item("ansible_ssh_pass", self.pwd)
        attr_str += self.get_item("ansible_ssh_become", self.become_pwd)
        attr_str += self.get_item("set_hostname", self.hostName)
        if num == 0:
            attr_str += self.get_item("k8s_api_server_ip", self.api)
            attr_str += self.get_item("kube_interface", self.interface) + '\n'
            self.master += attr_str
        if num == 1:
            attr_str += '\n'
            self.worker += attr_str
        if num == 2:
            attr_str += '\n'
            self.mef += attr_str

    @staticmethod
    def get_item(item_name, item_value):
        if item_value.strip() != "":
            item = ' {}="{}"'.format(item_name, item_value)
        else:
            return ""
        return item


def verify_parameter(num, tools, obj):
    if num not in SCENE_LIST:
        return 'scene_num invalid !'
    tool_list = tools.split(',')
    for tool in tool_list:
        tool = tool.lower()
        if tool not in TOOLS_LIST and tool != "":
            return 'EXTRA_COMPONENT name incorrect !'
    master = obj.master
    if len(master.split('\n')) % 2 == 1:
        return 'master num not illegal !'
    return ''


def append_inventory(num, tools, obj):
    if num != '4':
        result = verify_parameter(num, tools, obj)
        if result != '':
            hwlog.error(result)
            sys.exit(1)
    do_append_inventory(num, tools, obj)


def do_append_inventory(num, tools, obj):
    raw_file = RAW_FILE.format(master=obj.master, worker=obj.worker, mef=obj.mef, sn=num, extra=tools)
    with open("../inventory_file", mode="w") as file:
        for line in raw_file:
            file.write(line)


def file_check(file):
    path = os.path.expanduser(file)
    abs_path = os.path.abspath(path)
    real_path = os.path.realpath(path)
    if abs_path != real_path:
        raise Exception("Not a safe_realpath, not allow symbolic link file")
    if not os.path.realpath(real_path):
        raise Exception("{} not a file or not exists".format(os.path.basename(real_path)))
    return real_path


class HWLog:
    @staticmethod
    def hwlog(msg, level):

        logger = logging.getLogger("hw_log")
        logger.setLevel('DEBUG')

        formatter = logging.Formatter('%(levelname)s:%(asctime)s-%(filename)s:%(message)s')

        ch = logging.StreamHandler()
        ch.setLevel('DEBUG')
        ch.setFormatter(formatter)

        now = time.strftime('%Y-%m-%d')

        path = "ascend_deploy_" + now + ".log"
        fh = logging.FileHandler(path, encoding='UTF-8')
        fh.setLevel('DEBUG')
        fh.setFormatter(formatter)

        logger.addHandler(ch)
        logger.addHandler(fh)

        if level == 'DEBUG':
            logger.debug(msg)
        elif level == 'INFO':
            logger.info(msg)
        elif level == 'WARNING':
            logger.warning(msg)
        elif level == 'ERROR':
            logger.error(msg)
        elif level == 'CRITICAL':
            logger.critical(msg)
        logger.removeHandler(ch)
        logger.removeHandler(fh)

    def debug(self, msg):
        self.hwlog(msg, 'DEBUG')

    def info(self, msg):
        self.hwlog(msg, 'INFO')

    def warning(self, msg):
        self.hwlog(msg, 'WARNING')

    def error(self, msg):
        self.hwlog(msg, 'ERROR')

    def critical(self, msg):
        self.hwlog(msg, 'CRITICAL')


def run_install(scene_num, mef_option):
    working_env = os.environ.copy()
    log_path = "{}/.log/ascend-deployer-dl.log".format(working_env.get("HOME", "/root"))
    folder = os.path.exists(os.path.dirname(log_path))
    if not folder:
        os.makedirs(os.path.dirname(log_path))
    script_path = os.path.dirname(os.path.abspath(__file__)) + "/"
    cmd = "bash " + script_path + "install_ansible.sh && bash " + script_path + "install_npu.sh && bash " \
          + script_path + "install.sh && bash " + script_path + "hccn_set.sh"
    if scene_num == '4':
        if mef_option == 1:
            cmd = "bash " + script_path + "install_ansible.sh && bash " + script_path + "install_kubeedge.sh"
        if mef_option == 2:
            cmd = "bash " + script_path + "install_ansible.sh && bash " + script_path + "install.sh && bash " + \
                  script_path + "install_kubeedge.sh"

    hwlog.info("starting run install script")
    working_env['ANSIBLE_LOG_PATH'] = log_path
    working_env['ANSIBLE_CALLBACK_PLUGINS'] = "/root/offline-deploy/scripts"
    working_env['ANSIBLE_STDOUT_CALLBACK'] = "common_log"
    _ = subprocess.Popen(cmd, shell=True, env=working_env)


def mef_check(scene_num, mef_option):
    mef_key = mef_option.strip().lower()
    if MEF_OPTIONS.get(mef_key) is None:
        hwlog.error("mef option not valid !")
        sys.exit(1)
    if scene_num != '4' and MEF_OPTIONS[mef_key] != 0:
        hwlog.error("mef option not fit !")
        sys.exit(1)
    if scene_num == '4':
        mef_key = 'no'
    return mef_key


def main(inv_file):
    hwlog.info("starting parse csv file")
    with open(inv_file) as f:
        reader = csv.reader(f)
        top = next(reader)
        if len(top) < 6:
            raise Exception("missing parameter !")
        scene_num = top[1]
        extra_component = top[3]
        mef_option = top[5]
        mef_option = mef_check(scene_num, mef_option)

        next(reader)
        dto = InventoryDTO()
        for row in reader:
            dto.character = row[PARAMETER_DICT['character']]
            dto.ip = row[PARAMETER_DICT['ip']]
            dto.user = row[PARAMETER_DICT['user']]
            dto.pwd = row[PARAMETER_DICT['pwd']]
            dto.become = row[PARAMETER_DICT['become_pwd']]
            dto.hostName = row[PARAMETER_DICT['host']]
            dto.api = row[PARAMETER_DICT['api']]
            dto.interface = row[PARAMETER_DICT['interface']]
            dto.solve_device()
        hwlog.info("starting gen inventory file")
        append_inventory(scene_num, extra_component, dto)
    run_install(scene_num, MEF_OPTIONS[mef_option])


if __name__ == '__main__':
    hwlog = HWLog()
    if len(sys.argv) != 2:
        hwlog.error("csv file path need to be add to argv")
    else:
        inventory_file = sys.argv[1]
        try:
            inv_file_path = file_check(inventory_file)
        except Exception as err:
            hwlog.error(err)
        else:
            main(inv_file_path)
