# 离线安装工具说明

离线安装工具提供系统依赖、python依赖自动下载工具的和一键式安装所有依赖的脚本

目前离线安装工具支持如下操作系统

|操作系统 |版本|cpu架构    |
|-------|-----|---------|
|centos |7.6  |aarch64  |
|centos |7.6  |x86_64   |
|centos |8.2  |aarch64  |
|centos |8.2  |x86_64   |
|ubuntu |18.04|aarch64  |
|ubuntu |18.04|x86_64   |

# 离线安装工具操作指导

## 单机安装

- **步骤 1**

启动start_download.bat或者start_download.sh下载依赖软件

- **步骤 2**

将CANN软件包软件包放到resources目录下

```
atlas-deployer
|- install.sh
|- ansible.cfg
|- playbooks
|- scenes
`- resources/
   |- centos_7.6_aarch64
   |- centos_7.6_x86_64
   |- ...
   |- aarch64
   |- x86_64
   |- A300-3000-npu-driver_xxx.run
   |- A300-3000-npu-firmware_xxx.run
   |- Ascend-cann-nnrt-xxx.run
   |- ...
   `- Ascend-cann-toolkit-xxx.run
```

- **步骤 3**

使用filezilla等工具，将整个目录上从到待安装设备上

- **步骤 4**
执行install.sh --help仔细阅读参数说明
```bash
./install.sh --help
```

- **步骤 5**

运行install.sh安装组件或按场景安装,例如：

```bash
./install.sh --install=driver      // 安装driver
./install.sh --install=npu         // 安装driver和firmware
./install.sh --install-scene=auto  // 自动安装所有能找到的软件包
```

## 批量安装

在单机安装执行安装之前配置inventor_file文件指定待安装设备。下载和上传之服务器的过程与单机相同。

- **步骤 1**

在文件inventory_file配置待安装的其他设备的ip地址、用户名和密码,可配多个。

例如：
```buildoutcfg
[ascend]
ip_address_1 ansible_ssh_user='root' ansible_ssh_pass='password1'
ip_address_2 ansible_ssh_user='root' ansible_ssh_pass='password2'
ip_address_3 ansible_ssh_user='root' ansible_ssh_pass='password3'

```

- **步骤 2**

执行ansible ping测试其他设备连通性
```bash
export PATH=/usr/local/python3.7.5/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH
ansible all -i ./inventory_file -m ping
ip_address_1 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```
如果之前没有安装过ansible可以执行./install.sh --check
```bash
./install.sh --check
```
如果所有设备都success，表示所有设备都能正常连接。如有设备失败，请检查该设备的网络连接和sshd服务是否开启

- **步骤 4**
执行install.sh --help仔细阅读参数说明
```bash
./install.sh --help
```

- **步骤 5**

执行install.sh启动批量安装。过程与单机安装基本相同，例如：
```bash
./install.sh --install=driver      // 安装driver
./install.sh --install=npu         // 安装driver和firmware
./install.sh --install-scene=auto  // 自动安装所有能找到的软件包
```

# 离线安装工具详细说明
### 下载工具使用

windows下需安装python3，推荐使用python3.7版本以上

windows版本下载路径[python3.7.5](https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe)

工具目录结构如下
```
|-- downloader
|-- playbooks
|-- start_download.bat
|-- start_download.sh
|-- install.sh
|-- resources
|-- ansble.cfg
```
在windows下运行start_download.bat启动下载，在linux下运行start_download.sh启动下载

### 下载工具配置

下载工具涉及到的配置文件如下
```
downloader/config.ini
downloader/config/{os}_{version}_{arch}/source.list
downloader/config/{os}_{version}_{arch}/source.repo
```

- **Python源配置**

python源配置在downloader/config.ini中，默认使用华为源，可根据需要替换
```buildoutcfg
[pypi]
index_url=http://mirrors.huaweicloud.com/pypi/simple
```

- **Centos源配置**

centos源在对于版本的配置目录中
```
downloader/config/centos_{version}_{arch}/source.repo
```
例如centos 7.6  aarch64第一的源配置在如下文件中 
```
downloader/config/centos_7.6_aarch64/source.repo
```
centos 7.6的源配置文件内容如下:
```
[base]
baseurl=http://mirrors.huaweicloud.com/centos-altarch/7/os/aarch64

[epel]
baseurl=http://mirrors.huaweicloud.com/epel/7/aarch64
```
表示同时启用了base源和epel源，下载centos的依赖是会从这两个源中查询和下载。默认使用华为源，根据需要修改。
修改源通常只需要修改其中host部分，即mirrors.huaweicloud.com部分。如需修改后面部分，请确保理解centos的源配置

_注意:_ centos的依赖软件需要在base和epel一起才能包含完整。如果需删除源，可能造成依赖下载不完整。

centos 8.2的源结构与7.2差异较大,例如CentOS 8.2 aarch64下源配置为：
```buildoutcfg
[base]
baseurl=http://mirrors.huaweicloud.com/centos/8/BaseOS/aarch64/os

[powertool]
baseurl=http://mirrors.huaweicloud.com/centos/8/PowerTools/aarch64/os

[AppStream]
baseurl=http://mirrors.huaweicloud.com/centos/8/AppStream/aarch64/os/

[Everything]
baseurl=http://mirrors.huaweicloud.com/epel/8/Everything/aarch64
```
包含4个子源。 修改规则与centos7.6相同


- **Ubuntu源配置**

已ubuntu 18.04 aarch64为例子，源配置文件为：
```buildoutcfg
config/ubuntu_18.04_aarch64/source.list
```
内容如下：
```buildoutcfg
deb http://mirrors.huaweicoud.com/ubuntu-ports/ bionic main multiverse restricted universe
deb http://mirrors.huaweicloud.com/ubuntu-ports/ bionic-updates main multiverse restricted universe
deb http://mirrors.huaweicloud.com/ubuntu-ports/ bionic-security main multiverse restricted universe
```
配置文件格式和ubuntu的/etc/apt.d/source.list基本相同。默认使用华为源，可根据实际情况修改。

_注意_: 修改源时通常只建议修改url。 增加或删除源可能找出依赖下载失败或依赖版本不匹配。

### downloader介绍
1.downloader下载保存的目录结构：  
```
resources/
|-- centos_7.6_aarch64
|-- centos_7.6_x86_64
|-- centos_8.2_aarch64
|-- centos_8.2_x86_64
|-- ubuntu_18.04_aarch64
|-- ubuntu_18.04_x86_64
|-- aarch64
`-- x86_64
```

2.代理配置  
```editorconfig
[proxy]
enable=true         # 是否开启代理配置参数
verify=true         # 是否校验https证书
protocol=http
hostname=openproxy.huawei.com
port=8080
username=none       # 代理账号
userpassword=none   # 代理密码
```

3.下载行为配置
```
[download]
os_list=CentOS_7.6, CentOS_8.2, Ubuntu_18.04, BigCloud_7.6   # 待安装部署的环境OS信息
arch_list=aarch64, x86_64                                    # 待安装部署的环境Arch信息
delete_exists=true                                           # 当重新下载时是否删除已下载的软件包
```

### Driver,Frimware和CANN层软件安装

Driver,Firmware,CANN层软件需要使用run包。 将相关软件包放置在resources目录下即可，例如：
```
atlas-deployer
|- install.sh
|- ansible.cfg
|- playbooks
|- scenes
`- resources/
   |- centos_7.6_aarch64
   |- centos_7.6_x86_64
   |- ...
   |- aarch64
   |- x86_64
   |- A300-3000-npu-driver_xxx.run
   |- A300-3000-npu-firmware_xxx.run
   |- Ascend-cann-nnrt-xxx.run
   |- ...
   `- Ascend-cann-toolkit-xxx.run
```

# 安全注意事项

1. 由于需要使用dpkg， rpm等包管理器，只能使用root账号运行

2. inventory文件中会配置远程机器的root用户名和密码，建议使用ansible的vault机制进行加密，使用完成之后建议立即删除
   
   参考文档[http://www.ansible.com.cn/docs/playbooks_vault.html](http://www.ansible.com.cn/docs/playbooks_vault.html)
