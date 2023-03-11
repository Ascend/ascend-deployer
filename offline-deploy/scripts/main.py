import csv
import os
import sys

CHARACTER_LINE = 0
IP_LINE = 1
USER_LINE = 2
PWD_LINE = 3
HOSTNAME_LINE = 4
K8S_API_LINE = 5
INTERFACE_LINE = 6
SCENE_LIST = ['1', '2', '3', '4']
TOOLS_LIST = ['npu-exporter', 'noded', 'hccl-controller']
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
        self.hostName = ""
        self.api = ""
        self.interface = ""
        self.master = ""
        self.worker = ""
        self.mef = ""


def append_mef(obj):
    if obj.ip == "" or obj.user == "":
        pass
    str_user = "ansible_ssh_user=" + obj.user
    str_pwd = "ansible_ssh_pass=" + obj.pwd
    str_host = "set_hostname=" + obj.hostName
    new_line = " ".join(
        [obj.ip, str_user, str_pwd, str_host,
         "\n"])
    obj.worker += new_line


def append_worker(obj):
    if obj.ip == '':
        pass
    str_user = "ansible_ssh_user=" + obj.user
    str_pwd = "ansible_ssh_pass=" + obj.pwd
    str_host = "set_hostname=" + obj.hostName
    new_line = " ".join(
        [obj.ip, str_user, str_pwd, str_host,
         "\n"])
    obj.worker += new_line


def append_master(obj):
    if obj.ip == "" or obj.user == "":
        pass
    str_user = "ansible_ssh_user=" + obj.user
    str_pwd = "ansible_ssh_pass=" + obj.pwd
    str_host = "set_hostname=" + obj.hostName
    str_api = "k8s_api_server_ip=" + obj.api
    str_interface = " kube_interface=" + obj.interface
    new_line = " ".join(
        [obj.ip, str_user, str_pwd, str_host, str_api, str_interface,
         "\n"])
    obj.master += new_line


def solve_device(obj):
    if obj.character == "worker":
        append_worker(obj)
    elif obj.character == "master":
        append_master(obj)
    elif obj.character == "mef":
        append_mef(obj)


def verify_parameter(num, tools, obj):
    if num not in SCENE_LIST:
        return 'scene_num invalid !'
    toollist = tools.split(',')
    for tool in toollist:
        tool = tool.lower()
        if tool not in TOOLS_LIST:
            return 'tool name incorrect !'
    master = obj.master
    mlist = master.split('\n')
    if len(mlist) % 2 == 0:
        return 'master num not illegal !'
    return ''


def append_inventory(num, tools, obj):
    result = verify_parameter(num, tools, obj)
    if result != '':
        print(result)
        sys.exit(1)
    do_append_inventory(num, tools, obj)


def do_append_inventory(num, tools, obj):
    raw_file = RAW_FILE.format(master=obj.master, worker=obj.worker, mef=obj.mef, sn=num, extra=tools)
    inventory = open("inventory_file", mode="w", encoding="UTF-8")
    for line in raw_file:
        print(line)
        inventory.write(line)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        filename = 'Inventory_Template.CSV'
    else:
        filename = sys.argv[1]
    try:
        f = open(filename, mode="r", encoding="GBK")
    except Exception:
        print("CANNOT READ THE FILE!")

    reader = csv.reader(f)
    top = next(reader)
    scene_num = top[1]
    extra = top[3]

    title = next(reader)
    dto = InventoryDTO()
    for row in reader:
        dto.character = row[CHARACTER_LINE]
        dto.ip = row[IP_LINE]
        dto.user = row[USER_LINE]
        dto.pwd = row[PWD_LINE]
        dto.hostName = row[HOSTNAME_LINE]
        dto.api = row[K8S_API_LINE]
        dto.interface = row[INTERFACE_LINE]
        solve_device(dto)
    append_inventory(scene_num, extra, dto)

    command = './run_install.sh'
    ret = os.popen(command)
