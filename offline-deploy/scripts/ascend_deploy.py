# -*- coding:utf-8 -*-
import csv
import os.path
import subprocess
import sys
import common_log

INVENTORY_DICT = {'group': 0, 'ssh_host': 1, 'ssh_user': 2, 'ssh_pass': 3, 'ssh_become_pass': 4, 'host_name': 5,
                  'k8s_api_server_ip': 6, 'kube_interface': 7,
                  }
HCCN_INVENTORY_DICT = {'hccn_mode': 8, 'device_netmask': 9, 'detect_ip': 10, 'device_ips': 11}
ROW1_DICT = {'scene_num': 1, 'extra_component': 3, 'mef_option': 5, 'pod_network_cidr': 7, 'kube_vip': 9,
             'harbor_server': 11, 'harbor_admin_user': 13, 'harbor_admin_password': 15, 'harbor_public_project': 17,
             'harbor_ca_file': 19}
CSV_SIZE = 1024 * 1024
SCENE_LIST = ['1', '2', '3', '4']
TOOLS_LIST = ['npu-exporter', 'noded', 'hccl-controller']
MEF_OPTIONS = {'no': 0, 'mef-only': 1, "mef-all": 2}
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
OFFLINE_DEPLOY_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANSIBLE_PATH = os.path.join(SCRIPT_PATH, "install_ansible.sh")
BASH = " bash "
AND = " && "
HCCN_PATH = os.path.join(SCRIPT_PATH, "hccn_set.sh")
NPU_PATH = os.path.join(SCRIPT_PATH, "install_npu.sh")
INSTALL_PATH = os.path.join(SCRIPT_PATH, "install.sh")
KUBEEDGE_PATH = os.path.join(SCRIPT_PATH, "install_kubeedge.sh")
REPORT_PATH = os.path.join(SCRIPT_PATH, "machine_report.sh")
INVENTORY_FILE = """#           *********************主机变量配置区域*********************
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
{other}
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
EXTRA_COMPONENT="{extra_component}"

# k8s集群使用的子网IP网段，如果与服务器IP网段重合，需要修改下面的值为其他私有网段。如：192.168.0.0/16
POD_NETWORK_CIDR="{pod_network_cidr}"

# 多master场景下配置虚拟IP，kube_vip需跟k8s集群节点ip在同一子网，且为闲置、未被他人使用的ip
KUBE_VIP="{kube_vip}"

# 使用harbor镜像仓时配置
# harbor服务地址，格式为ip:port，不含协议，如"192.0.0.1:1234"
HARBOR_SERVER="{harbor_server}"
# 配置harbor管理员账号信息，用于在harbor中创建名为项目，以及推送、拉取k8s相关、MindX DL相关的镜像
HARBOR_ADMIN_USER="{harbor_admin_user}"
HARBOR_ADMIN_PASSWORD="{harbor_admin_password}"
# MindX DL相关镜像的项目公开状态，默认为私有，可选值false或true
HARBOR_PUBLIC_PROJECT="{harbor_public_project}"
# 使用https协议时，配置harbor镜像仓根CA文件路径
HARBOR_CA_FILE="{harbor_ca_file}"
"""
HCCN_INVENTORY_FILE = """
[tools]
{hccn_tools}
# localhost ansible_connection='local' action=config mode=SMP ip=192.168.100.106 detectip=192.168.100.108 netmask=255.255.255.0
# 10.10.10.10 ansible_ssh_user='root' action=config mode=SMP ip=192.168.100.101 detectip=192.168.100.1 netmask=255.255.255.0
# 10.10.10.11 ansible_ssh_user='root' action=config mode=SMP ip=192.168.100.108 detectip=192.168.100.1 netmask=255.255.255.0

[tools:vars]
user=HwHiAiUser
group=HwHiAiUser
ansible_ssh_user='root'
"""


class InventoryDTO:
    def __init__(self):
        self.inventory_param = self.init_inventory_param(INVENTORY_DICT)
        self.hccn_inventory_param = self.init_inventory_param(HCCN_INVENTORY_DICT)
        self.row1_param = self.init_inventory_param(ROW1_DICT)

        self.master = ""
        self.worker = ""
        self.mef = ""
        self.other = ""
        self.hccn_tool = ""
        self.run_hccn_set = False

    @staticmethod
    def init_inventory_param(param_dict):
        gen_dict = {}
        for k, _ in param_dict.items():
            gen_dict[k] = ""
        return gen_dict

    def append_node(self, group):
        attr_str = ''
        if self.inventory_param["ssh_host"] == '':
            return
        attr_str += self.inventory_param["ssh_host"]
        attr_str += self.get_item("ansible_ssh_user", self.inventory_param["ssh_user"])
        attr_str += self.get_item("ansible_ssh_pass", self.inventory_param["ssh_pass"])
        attr_str += self.get_item("ansible_ssh_become", self.inventory_param["ssh_become_pass"])
        attr_str += self.get_item("set_hostname", self.inventory_param["host_name"])
        if group == 'master':
            attr_str += self.get_item("k8s_api_server_ip", self.inventory_param["k8s_api_server_ip"])
            attr_str += self.get_item("kube_interface", self.inventory_param["kube_interface"]) + '\n'
            self.master += attr_str
        if group == 'worker' or group == 'other':
            if self.verify_hccn_param(self.hccn_inventory_param):
                self.run_hccn_set = True
                hccn_str = ''
                hccn_str += self.inventory_param["ssh_host"]
                hccn_str += self.get_item("ansible_ssh_user", self.inventory_param["ssh_user"])
                hccn_str += " action=config"
                hccn_str += self.get_item("mode", self.hccn_inventory_param["hccn_mode"])
                hccn_str += self.get_item("ip", self.hccn_inventory_param["device_ips"])
                hccn_str += self.get_item("detectip", self.hccn_inventory_param["detect_ip"])
                hccn_str += self.get_item("netmask", self.hccn_inventory_param["device_netmask"])
                hccn_str += '\n'
                self.hccn_tool += hccn_str
            attr_str += '\n'
            if group == 'worker':
                self.worker += attr_str
            else:
                self.other += attr_str
        if group == 'mef':
            attr_str += '\n'
            self.mef += attr_str

    @staticmethod
    def verify_hccn_param(param):
        if param["hccn_mode"] != 'SMP' and param["hccn_mode"] != 'AMP':
            return False
        if param["hccn_mode"] == '' or param["device_netmask"] == '' or param["detect_ip"] == '' or param[
            "device_ips"] == '':
            return False
        return True

    @staticmethod
    def get_item(item_name, item_value):
        if item_value.strip() != "":
            if item_name == 'ip':
                item_value = item_value.replace('/', ',')
            item = ' {}="{}"'.format(item_name, item_value)
        else:
            return ""
        return item

    def parse_other_row_info(self, row):
        for k, v in INVENTORY_DICT.items():
            self.inventory_param[k] = row[v]

        for k, v in HCCN_INVENTORY_DICT.items():
            self.hccn_inventory_param[k] = row[v]
        self.solve_device()

    def parse_row1_info(self, row):
        for k, v in ROW1_DICT.items():
            if k == "harbor_ca_file" and row[v] == "no":
                self.row1_param[k] = ""
            else:
                self.row1_param[k] = row[v]
        self.row1_param['mef_option'] = self.mef_check(self.row1_param['scene_num'], self.row1_param['mef_option'])

    @staticmethod
    def mef_check(scene_num, mef_option):
        mef_key = mef_option.strip().lower()
        if MEF_OPTIONS.get(mef_key) is None:
            hwlog.error("mef option not valid !")
            sys.exit(1)
        if scene_num == '4' and MEF_OPTIONS[mef_key] == 0:
            hwlog.error("mef option not fit !")
            sys.exit(1)
        if scene_num != '4':
            mef_key = 'no'
        return mef_key

    def solve_device(self):
        if self.inventory_param["group"] == 'master':
            self.append_node('master')
        elif self.inventory_param["group"] == 'worker':
            self.append_node('worker')
        elif self.inventory_param["group"] == 'mef':
            self.append_node('mef')
        elif self.inventory_param["group"] == 'other':
            self.append_node('other')
        else:
            hwlog.error("group must be one of master,worker,mef,other")
            sys.exit(1)
        self.clear_inventory_param()

    def clear_inventory_param(self):
        for k, _ in self.inventory_param.items():
            self.inventory_param[k] = ''
        for k, _ in self.hccn_inventory_param.items():
            self.hccn_inventory_param[k] = ''

    def append_inventory(self):
        if self.row1_param['scene_num'] != '4':
            result = self.verify_parameter()
            if result != '':
                hwlog.error(result)
                sys.exit(1)
        self.do_append_inventory()

    def verify_parameter(self):
        if self.row1_param['scene_num'] not in SCENE_LIST:
            return 'scene_num invalid !'
        tool_list = self.row1_param['extra_component'].split(',')
        for tool in tool_list:
            tool = tool.lower()
            if tool not in TOOLS_LIST and tool != "":
                return 'EXTRA_COMPONENT name incorrect !'
        master = self.master
        if len(master.split('\n')) % 2 == 1:
            return 'master num not illegal !'
        return ''

    def do_append_inventory(self):
        raw_inventory_file = INVENTORY_FILE.format(master=self.master, worker=self.worker, mef=self.mef,
                                                   other=self.other,
                                                   sn=self.row1_param['scene_num'],
                                                   extra_component=self.row1_param['extra_component'],
                                                   pod_network_cidr=self.row1_param['pod_network_cidr'],
                                                   kube_vip=self.row1_param['kube_vip'],
                                                   harbor_server=self.row1_param['harbor_server'],
                                                   harbor_admin_user=self.row1_param['harbor_admin_user'],
                                                   harbor_admin_password=self.row1_param['harbor_admin_password'],
                                                   harbor_public_project=self.row1_param['harbor_public_project'],
                                                   harbor_ca_file=self.row1_param['harbor_ca_file'])
        with open(OFFLINE_DEPLOY_PATH + "/inventory_file", mode="w") as file:
            for line in raw_inventory_file:
                file.write(line)
        raw_hccn_inventory_file = HCCN_INVENTORY_FILE.format(hccn_tools=self.hccn_tool)
        with open(OFFLINE_DEPLOY_PATH + "/hccn_inventory_file", mode="w") as file:
            for line in raw_hccn_inventory_file:
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


def run_install(mef_option, run_hccn_set, scene_num):
    working_env = os.environ.copy()
    log_path = "{}/.log/ascend-deployer-dl.log".format(working_env.get("HOME", "/root"))
    folder = os.path.exists(os.path.dirname(log_path))
    if not folder:
        os.makedirs(os.path.dirname(log_path))
    install_cmd = get_install_cmd(mef_option, run_hccn_set, scene_num)
    hwlog.info("starting run install script")
    working_env['ANSIBLE_LOG_PATH'] = log_path
    ansible_plugin_path = os.path.dirname(os.path.abspath(__file__)) + "/../ansible_plugin"
    working_env['ANSIBLE_CALLBACK_PLUGINS'] = ansible_plugin_path
    working_env['ANSIBLE_STDOUT_CALLBACK'] = "ansible_log"
    working_env['ANSIBLE_LOAD_CALLBACK_PLUGINS'] = "True"
    install_process = subprocess.Popen(install_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       env=working_env)
    err_flag = False
    log_list = ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
    for line in iter(install_process.stdout.readline, b''):
        line = line.decode('utf-8')
        stdout_line = str(line).strip()
        if stdout_line.find("[ERROR]") != -1 or stdout_line.find("not support"):
            err_flag = True
        if stdout_line != "":
            for str_list in log_list:
                if stdout_line.find(str_list) != -1:
                    print(stdout_line)
                    break
        sys.stdout.flush()
    if err_flag:
        hwlog.error("Seems like something went wrong, please check the logs")
        sys.exit(1)
    else:
        hwlog.info("Ascend deploy install success")


def get_install_cmd(mef_option, run_hccn_set, scene_num):
    if run_hccn_set:
        install_cmd = BASH + ANSIBLE_PATH + AND + BASH + NPU_PATH + AND + BASH + HCCN_PATH + AND + BASH \
                      + INSTALL_PATH + AND + BASH + REPORT_PATH
    else:
        install_cmd = BASH + ANSIBLE_PATH + AND + BASH + NPU_PATH + AND + BASH + INSTALL_PATH + AND + BASH + REPORT_PATH
    if scene_num == '4':
        if mef_option == 1:
            install_cmd = BASH + ANSIBLE_PATH + AND + BASH + KUBEEDGE_PATH + AND + BASH + REPORT_PATH
        if mef_option == 2:
            install_cmd = BASH + ANSIBLE_PATH + AND + BASH + INSTALL_PATH + AND + BASH + KUBEEDGE_PATH \
                          + AND + BASH + REPORT_PATH
    return install_cmd


def main(inv_file):
    hwlog.info("starting parse csv file")
    with open(inv_file) as f:
        reader = csv.reader(f)
        dto = InventoryDTO()
        for row in reader:
            if row[0] == "SCENE_NUM":
                dto.parse_row1_info(row)
            elif row[0] == "*group":
                pass
            else:
                dto.parse_other_row_info(row)
        hwlog.info("starting gen inventory file")
        dto.append_inventory()
    run_install(MEF_OPTIONS[dto.row1_param['mef_option']], dto.run_hccn_set, dto.row1_param['scene_num'])


if __name__ == '__main__':
    hwlog = common_log.Get_logger_deploy("ascend_deploy")
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
