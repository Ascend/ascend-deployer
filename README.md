# 离线安装工具说明

离线安装工具提供系统依赖、python依赖自动下载工具和一键式安装所有依赖的脚本

目前离线安装工具支持如下操作系统

|操作系统|版本 |cpu架构   |安装类型         |
|-------|-----|---------|----------------|
|CentOS |7.6  |aarch64  |镜像默认Minimal模式         |
|CentOS |7.6  |x86_64   |镜像默认Minimal模式         |
|CentOS |8.2  |aarch64  |镜像默认Minimal模式         |
|CentOS |8.2  |x86_64   |镜像默认Minimal模式         |
|ubuntu |18.04|aarch64  |SmartKit默认Standard模式、镜像默认Server模式|
|ubuntu |18.04|x86_64   |SmartKit默认Standard模式、镜像默认Server模式|
|BigCloud|7.6 |aarch64  |镜像默认Minimal模式         |
|BigCloud|7.6 |x86_64   |镜像默认Minimal模式         |
|SLES   |12.4 |x86_64   |镜像默认Minimal模式         |
|EulerOS|2.0SP8 |aarch64|镜像默认Minimal模式         |
|EulerOS|2.0SP9 |aarch64|镜像默认Minimal模式         |
|EulerOS|2.0SP9 |x86_64 |镜像默认Minimal模式         |

OS必装软件：tar, cd, ls, find, grep, chown, chmod等基本命令。OpenSSH Server用于ansible通过SSH连接登录，Ubuntu系统安装时需要选择安装

环境限制：OS安装后没有额外安装或卸载过软件，是镜像安装成功后的默认环境；若卸载安装某些系统软件，导致与安装默认系统包不一致，离线安装部署不支持该场景，需要手动配置网络，通过apt、yum、dnf等工具安装配置缺失软件

依赖限制：离线部署工具只能安装最基本的库，保证torch和tensorflow能够运行起来。如果需要运行比较复杂的推理或者训练模型，模型代码中可能包含具体业务相关的库，这些库需要自行安装。

EulerOS：需要确保源存在和内核版本相同的kenrel-headers和kernel-devel版本。如果源中没有，需要自行准备对应的kernel-headers和kernel-devel软件包。

CentOS：CentOS 8.2安装时，需要勾选Additioanl Software for Selected Environment中的Standard等选项，如未勾选，系统安装完成后可能缺少tar等基本命令。

远程安装：EulerOS等操作系统默认禁止root用户远程连接。因此，在这类操作系统中远程安装时需要提前配置sshd_config中PermitRootLogin为yes。安装完成后再配置为no。

系统的内核版本可通过 uname -r 命令查看

toolkit: 安装toolkit时可能需要配置sudoer用户。详细配置步骤请参考昇腾社区中异构计算框架CANN相关文档《软件安装指南（开发&运行场景，通过命令行方式）》配置安装用户权限章节


# 离线安装工具操作指导

## 单机安装

- **步骤 1**

启动start_download.bat或者start_download.sh下载依赖软件

- **步骤 2**

将CANN软件包放到resources目录下

```
ascend-deployer
|- install.sh
|- ansible.cfg
|- playbooks
|- scenes
`- resources/
   |- CentOS_7.6_aarch64
   |- CentOS_7.6_x86_64
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

使用filezilla等工具，将整个目上传到待安装设备上

- **步骤 4**
执行install.sh --help仔细阅读参数说明
```bash
./install.sh --help
Usage: ./install.sh [options]
 Options:
--help  -h                     Print this message
--check                        check environment
--clean                        clean resources on remote servers
--nocopy                       do not copy resources to remote servers when install for remote
--debug                        enable debug
--install=<package_name>       Install specific package:
                               cmake
                               driver
                               firmware
                               gcc
                               nnae
                               nnrt
                               npu
                               python375
                               sys_pkg
                               tensorflow
                               tfplugin
                               toolbox
                               toolkit
                               torch
The "npu" will install driver and firmware together
--install-scene=<scene_name>   Install specific scene:
                               auto
                               infer_dev
                               infer_run
                               train_dev
                               train_run
                               vmhost
The "npu" will upgrade driver and firmware together
--test=<target>                test the functions:
                               all
                               driver
                               firmware
                               tensorflow
                               toolbox
                               torch
```

- **步骤 5**

运行install.sh安装组件或按场景安装,例如：

```bash
./install.sh --install=driver       // 安装driver
./install.sh --install=npu          // 安装driver和firmware
./install.sh --install=nnrt,toolbox // 安装nnrt和toolbox
./install.sh --install-scene=auto   // 自动安装所有能找到的软件包
```
_注意:_ 如果安装或者升级了driver或firmware，请在安装完成后重启设备使驱动和固件生效

_注意:_ 执行指定组件安装时请确保安装顺序正确。例如nnrt或nnae需要在driver和firmware安装之后，
firmware必须在driver已经安装后才能安装，等等。

_注意:_ 部分组件存在运行时依赖，例如torch需要toolkit提供相应的运行时依赖。tensorflow + npubridge需要tfplguin提供运行时依赖。


- **步骤 6**

运行检查，简单检查各个组件是否能够正常工作
```bash
./install.sh --test=driver         // 测试driver是否正常
./install.sh --test=firmware       // 测试firmware是否正常
./install.sh --test=torch          // 测试pytorch是否正常
./install.sh --test=all            // 测试所有已安装组件
```


## 批量安装

在单机安装执行安装之前配置inventory_file文件指定待安装设备。下载和上传到服务器的过程与单机相同。

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

- **步骤 6**

运行检查，与单机安装相同


## 按场景安装

离线部署工具提供几个基本安装场景

|场景|安装的组件 |说明|
|-------|-------------------------|-----|
|infer_run |driver, firmware, nnrt, toolbox| 推理运行|
|infer_dev |driver, firmware, nnrt, toolbox, toolkit, torch, tfplugin, tensorflow|推理开发|
|train_run |driver, firmware, nnae, toolbox, torch, tfplugin, tensorflow|训练运行|
|train_dev |driver, firmware, nnae, toolbox, toolkit, torch, tfplugin, tensorflow|训练开发|
|vmhost |driver, firmware, toolbox|虚拟机host|
|auto |all| 安装所有|


- **场景定制**

场景的配置文件位于scene目录，文件内容非常简单，例如文件scene/scene_infer_run.yml:
```bash
- hosts: '{{ hosts_name }}'

- name: install system dependencies
  import_playbook: ../playbooks/install_sys_pkg.yml

- name: install driver and firmware
  import_playbook: ../playbooks/install_npu.yml

- name: install nnrt
  import_playbook: ../playbooks/install_nnrt.yml

- name: install toolbox
  import_playbook: ../playbooks/install_toolbox.yml
```
如果有特殊需求需要定制场景，参考scene_infer_run.yml。对不同组件进行灵活组合即可。


# 离线安装工具详细说明
### 下载工具使用

windows下需安装python3，推荐使用python3.7版本以上

windows版本下载路径[python3.7.5](https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe)

工具目录结构如下
```
|-- downloader
|-- playbooks
|-- start_download.bat
|-- start_download_ui.bat
|-- start_download.sh
|-- install.sh
|-- resources
|-- ansble.cfg
|-- ...
```
在windows下运行start_download.bat启动下载，在linux下运行start_download.sh启动下载

在windows下运行start_download_ui.bat可启动建议UI。可在简易UI中选择需要下载的OS组件。

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

CentOS源在对应版本的配置目录中
```
downloader/config/CentOS_{version}_{arch}/source.repo
```
例如CentOS 7.6 aarch64第一的源配置在如下文件中 
```
downloader/config/CentOS_7.6_aarch64/source.repo
```
CentOS 7.6的源配置文件内容如下:
```
[base]
baseurl=http://mirrors.huaweicloud.com/centos-altarch/7/os/aarch64

[epel]
baseurl=http://mirrors.huaweicloud.com/epel/7/aarch64
```
表示同时启用了base源和epel源，下载CentOS的依赖是会从这两个源中查询和下载。默认使用华为源，根据需要修改。
修改源通常只需要修改其中host部分，即mirrors.huaweicloud.com部分。如需修改后面部分，请确保理解CentOS的源配置

_注意:_ CentOS的依赖软件需要在base和epel一起才能包含完整。如果需删除源，可能造成依赖下载不完整。

CentOS 8.2的源结构与7.6差异较大,例如CentOS 8.2 aarch64下源配置为：
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
包含4个子源。 修改规则与CentOS 7.6相同


- **Ubuntu源配置**

以Ubuntu 18.04 aarch64为例，源配置文件为：
```buildoutcfg
downloader/config/Ubuntu_18.04_aarch64/source.list
```
内容如下：
```buildoutcfg
deb http://mirrors.huaweicoud.com/ubuntu-ports/ bionic main multiverse restricted universe
deb http://mirrors.huaweicloud.com/ubuntu-ports/ bionic-updates main multiverse restricted universe
deb http://mirrors.huaweicloud.com/ubuntu-ports/ bionic-security main multiverse restricted universe
```
配置文件格式和ubuntu的/etc/apt/source.list基本相同。默认使用华为源，可根据实际情况修改。

_注意_: 修改源时通常只建议修改url。 增加或删除源可能找出依赖下载失败或依赖版本不匹配。

### downloader介绍
1.downloader下载保存的目录结构：  
```
resources/
|-- CentOS_7.6_aarch64
|-- CentOS_7.6_x86_64
|-- CentOS_8.2_aarch64
|-- CentOS_8.2_x86_64
|-- Ubuntu_18.04_aarch64
|-- Ubuntu_18.04_x86_64
|-- aarch64
`-- x86_64
```

2.代理配置

在文件downloader/config.ini文件中配置代理
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

在文件downloader/config.ini文件中配置下载项
```
[download]
os_list=CentOS_7.6_aarch64, CentOS_7.6_x86_64, CentOS_8.2_aarch64, CentOS_8.2_x86_64, Ubuntu_18.04_aarch64, Ubuntu_18.04_x86_64, BigCloud_7.6_aarch64, BigCloud_7.6_x86_64, SLES_12.4_x86_64  # 待安装部署的环境OS信息
```

### Driver,Frimware和CANN层软件安装

Driver,Firmware,CANN层软件需要使用run包。 将相关软件包放置在resources目录下即可，例如：
```
ascend-deployer
|- install.sh
|- ansible.cfg
|- playbooks
|- scenes
`- resources/
   |- CentOS_7.6_aarch64
   |- CentOS_7.6_x86_64
   |- ...
   |- aarch64
   |- x86_64
   |- A300-3000-npu-driver_xxx.run
   |- A300-3000-npu-firmware_xxx.run
   |- Ascend-cann-nnrt-xxx.run
   |- ...
   `- Ascend-cann-toolkit-xxx.run
```

### 环境变量配置

1.python3.7.5

如果待安装环境未安装python3.7.5，安装过程中会自动安装，为了不影响系统自带python(python2.x or python3.x)，
要使用python3.7.5之前，需要配置以下环境变量:
```bash
export PATH=/usr/local/python3.7.5/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH
```

### 更新离线部署工具

离线部署工具中的upgrade_self.sh和upgrade_self.bat用于更新离线部署工具自身

# 升级注意事项

1.涉及1-2包(driver、firmware)的升级操作，需要手动reboot重启服务器，才能生效，即执行test接口验证前需要重启

# 安全注意事项

1. 由于需要使用dpkg， rpm等包管理器，只能使用root账号运行

2. 由于需要安装大量开源软件，本工具下载的开源软件均来自操作系统源，开源软件的漏洞和修复需要用户自己根据情况修复，强烈建议使用官方源定期更新

3. inventory_file文件中会配置远程机器的root用户名和密码，建议使用ansible的vault机制进行加密，使用完成之后建议立即删除

   参考文档[http://www.ansible.com.cn/docs/playbooks_vault.html](http://www.ansible.com.cn/docs/playbooks_vault.html)
