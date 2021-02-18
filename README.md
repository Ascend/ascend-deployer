# 简介
## 功能描述
离线安装工具提供系统组件、python第三方依赖自动下载以及一键式安装的功能，并支持驱动、固件以及CANN软件包的安装。
## 环境要求
离线安装工具现支持如下操作系统的组件下载及安装。
|操作系统|版本|CPU架构|安装类型|
|:----:|:----:|:----:|:----:|
|CentOS|7.6|aarch64|镜像默认Minimal模式|
|CentOS|7.6|x86_64|镜像默认Minimal模式|
|CentOS|8.2|aarch64|镜像默认Minimal模式|
|CentOS|8.2|x86_64|镜像默认Minimal模式|
|ubuntu|18.04|aarch64|镜像默认Server模式、SmartKit默认Standard模式|
|ubuntu|18.04|x86_64|镜像默认Server模式、SmartKit默认Standard模式|
|BigCloud|7.6|aarch64|镜像默认Minimal模式|
|BigCloud|7.6|x86_64|镜像默认Minimal模式|
|SLES|12.4|x86_64|镜像默认Minimal模式|
|EulerOS|2.0SP8|aarch64|镜像默认Minimal模式|
|EulerOS|2.0SP9|aarch64|镜像默认Minimal模式|
|EulerOS|2.0SP9|x86_64|镜像默认Minimal模式|
## 注意事项
- 操作系统必须安装tar, cd, ls, find, grep, chown, chmod等基本命令。OpenSSH Server用于ansible通过SSH连接登录，Ubuntu系统安装时需要选择安装。
- 离线安装工具仅支持OS镜像安装成功后的默认环境，请不要在安装OS后额外安装或卸载软件。若已卸载某些系统软件，导致与安装默认系统包不一致，需手动配置网络，通过apt、yum、dnf等工具安装配置缺失软件。
- 离线安装工具只能安装最基本的库，确保TensorFlow和PyTorch能够运行。若需运行较为复杂的推理业务或模型训练，模型代码中可能包含具体业务相关的库，这些库需用户自行安装。
- EulerOS系统需要确保源存在与系统内核版本（可通过 `uname -r` 命令查看）一致的kernel-headers和kernel-devel软件包。若不存在，需自行准备相应的kernel-headers和kernel-devel软件包。
- CentOS 8.2安装时，需要勾选“Additioanl Software for Selected Environment”中的Standard，若未勾选，系统安装完成后可能缺少tar等基本命令。
- EulerOS等操作系统默认禁止root用户远程连接。因此，对于这类操作系统，远程安装时需提前配置sshd_config中PermitRootLogin为yes，安装完成后再配置为no。
# 操作指导
## 下载系统组件及python第三方依赖
支持windows或linux系统使用下载功能。
### 须知
- 如需配置代理、通过修改配置文件的方式调整为下载所需OS的组件等，可编辑“downloader/config.ini”文件，具体可参考<a href="#config">配置说明</a>。
- 离线安装工具已提供源配置文件，默认使用华为源，用户可根据需要进行替换。具体可参考<a href="#sourceconfig">源配置</a>。
- 下载好的软件会自动存放于resources目录下。
- 安装完成后，建议卸载系统中可能存在安全风险的gcc、g++等第三方组件。
### 下载操作
- windows
    1. windows环境需安装python3，推荐使用python3.7版本以上。
下载链接：[python3.7.5](https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe)
请根据界面提示完成安装。注意安装时在“Advanced Options"界面勾选” Add Python to environment variables"，否则需手动添加环境变量。
    2. 启动下载。
运行start_download.bat或start_download_ui.bat（推荐使用，可在弹出的简易UI界面上勾选需要下载的OS组件）。
- linux
    执行`./start_download.sh`启动下载。
## 安装操作
### 安装须知
- 由于安装过程需使用dpkg， rpm等包管理器，因此仅支持root用户运行。

- 离线安装工具在安装驱动、CANN软件包过程中，会默认创建HwHiAiUser用户作为软件包运行用户，若用户需自行指定运行用户和用户组，可自行修改inventory_file文件。文件内容如下：
    ```
    [ascend:vars]
    user=HwHiAiUser
    group=HwHiAiUser
    ```
    
- 由于需要安装大量开源软件，离线安装工具下载的开源软件均来自操作系统源，开源软件的漏洞和修复需要用户自行根据情况修复，强烈建议使用官方源定期更新。

### 准备软件包

根据实际需要准备待安装软件包（支持驱动、固件、CANN软件包的安装）。
    - 驱动和固件：[获取链接](https://ascend.huawei.com/#/hardware/firmware-drivers)
    - CANN软件包：[获取链接](https://ascend.huawei.com/#/software/cann)
将待安装软件包放置于resources目录下。参考如下：

```
ascend-deployer
|- ...
|- install.sh
|- inventory_file
|- ...
|- playbooks
|- README.md
|- resources
   |- A300-3010-npu-driver_xxx.run
   |- A300-3010-npu-firmware_xxx.run
   |- Ascend-cann-nnrt-xxx.run
   |- ...
   |- Ascend-cann-toolkit-xxx.run
   |- ...
   |- BigCloud_7.6_aarch64
   |- BigCloud_7.6_x86_64
   |- ...
```
### 单机安装
1. 将ascend-deployer整个目录上传到待安装设备上。
2. 执行安装脚本，可根据需要选择安装方式（指定软件安装或指定场景安装）。
    - 指定软件安装
`./install.sh --install=<package_name>`
<package_name>可选范围可通过执行`./install.sh --help`查看。命令示例如下：
    `./install.sh --install=npu     //安装driver和firmware`
    注意事项：
        - 请按照“driver>firmware>CANN软件包（toolkit、nnrt等）”或“npu>CANN软件包（toolkit、nnrt等）”的顺序进行安装。
        - 安装driver或firmware后，需执行`reboot`重启设备使驱动和固件生效。
       - 部分组件存在运行时依赖，如pytorch需要toolkit提供运行时依赖，tensorflow + npubridge需要tfplugin提供运行时依赖。
    - 指定场景安装
`./install.sh --install-scene=<scene_name>`
离线部署工具提供几个基本安装场景，具体可参考<a href="#scene">安装场景介绍</a>。命令示例如下：
 `./install.sh --install-scene=auto     //自动安装所有能找到的软件包`
3. 安装后检查，可通过以下命令检查指定组件能否正常工作。
`./install.sh --test=<target>`
<target>可选范围可通过执行`./install.sh --help`查看。命令示例如下：
`./install.sh --test=driver     //测试driver是否正常`
### 批量安装

1. 配置待安装的其他设备的ip地址、用户名和密码。
    编辑inventory_file文件，格式如下：
    ```
    [ascend]
    ip_address_1 ansible_ssh_user='root' ansible_ssh_pass='password1'
    ip_address_2 ansible_ssh_user='root' ansible_ssh_pass='password2'
    ip_address_3 ansible_ssh_user='root' ansible_ssh_pass='password3'
    ```
    注意：inventory文件中会配置远程设备的root用户名和密码，建议使用ansible的vault机制进行加密，使用完成之后建议立即删除。
2. 执行ansible ping测试待安装设备连通性。
    ```
    #配置环境变量
    export PATH=/usr/local/python3.7.5/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH
    #测试待安装设备连通性
    ansible all -i ./inventory_file -m ping
    ```
    若当前环境未安装ansible，可执行`./install.sh --check`
    确保所有设备都能正常连接，若存在设备连接失败情况，请检查该设备的网络连接和sshd服务是否开启。
3. 执行安装脚本，可根据需要选择安装方式（指定软件安装或指定场景安装）。
    - 指定软件安装
`./install.sh --install=<package_name>`
<package_name>可选范围可通过执行`./install.sh --help`查看。命令示例如下：
    `./install.sh --install=npu     //安装driver和firmware`
    注意事项：
        - 请按照“driver>firmware>CANN软件包（toolkit、nnrt等）”或“npu>CANN软件包（toolkit、nnrt等）”的顺序进行安装。
        - 安装driver或firmware后，需执行`reboot`重启设备使驱动和固件生效。
        - 部分组件存在运行时依赖，如pytorch需要toolkit提供运行依赖，tensorflow + npubridge需要tfplugin提供运行依赖。
    - 指定场景安装
`./install.sh --install-scene=<scene_name>`
离线部署工具提供几个基本安装场景，具体可参考<a href="#scene">安装场景介绍</a>。命令示例如下：
 `./install.sh --install-scene=auto     //自动安装所有能找到的软件包`
4. 安装后检查，可通过以下命令检查指定组件能否正常工作。
`./install.sh --test=<target>`
<target>可选范围可通过执行`./install.sh --help`查看。命令示例如下：
`./install.sh --test=driver     //测试driver是否正常`

# 配置环境变量
安装过程会自动给待安装设备安装python3.7.5，为不影响系统自带python(python2.x or python3.x)， 在使用python3.7.5之前，需配置如下环境变量:
```
export PATH=/usr/local/python3.7.5/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH
```
# 后续任务
- 推理场景
开发者可以参见《[CANN 应用软件开发指南 (C&C++)](https://www.huaweicloud.com/ascend/cann)》或《[CANN 应用软件开发指南 (Python)](https://www.huaweicloud.com/ascend/cann)》在开发环境上开发应用程序。
- 训练场景
若需进行网络模型移植和训练，请参考《[TensorFlow网络模型移植&训练指南](https://www.huaweicloud.com/ascend/pytorch-tensorflow)》或《[PyTorch网络模型移植&训练指南](https://www.huaweicloud.com/ascend/pytorch-tensorflow)》。
# 升级
可执行以下命令，升级指定软件：
`./install.sh --upgrade=<package_name>`
<package_name>可选范围可通过执行`./install.sh --help`查看。命令示例如下：
`./install.sh --upgrade=npu     //升级driver和firmware`
注意事项：

- 请按照“firmware>driver>CANN软件包（toolkit、nnrt等）“或“npu>CANN软件包（toolkit、nnrt等）”的顺序进行升级。
- 升级driver或firmware后，需执行`reboot`重启设备使驱动和固件生效。
# 卸载
可执行以下命令，卸载指定软件：
`./install.sh --uninstall=<package_name>`
<package_name>可选范围可通过执行`./install.sh --help`查看。命令示例如下：
`./install.sh --uninstall=npu     //卸载driver和firmware`
注意事项：
请按照“CANN软件包（toolkit、nnrt等）>driver和firmware（driver和firmware无卸载顺序要求）“的顺序进行卸载。

# 更新离线部署工具
能够通过以下操作实现离线安装工具自我更新。
- windows
运行upgrade_self.bat启动更新。
- linux
执行命令`./upgrade_self.sh`启动更新。
# 参考信息
## <a name="parameter">参数说明</a>
用户根据实际需要选择对应参数完成安装、升级或卸载，命令格式如下：
`./install.sh [options]`
参数说明请参见下表。表中各参数的可选参数范围可通过执行`./install.sh --help`查看。

| 参数                         | 说明                                                         |
| :--------------------------- | ------------------------------------------------------------ |
| --help  -h                   | 查询帮助信息。                                               |
| --check                      | 检查环境。                                                   |
| --clean                      | 清理resources目录。                                          |
| --nocopy                     | 在批量安装时不进行资源拷贝。                                 |
| --debug                      | 开发调测使用。                                               |
| --install=<package_name>     | 指定软件安装。若指定“--install=npu”，将会安装driver和firmware。 |
| --install-scene=<scene_name> | 指定场景安装。安装场景请参见<a href="#scene">安装场景介绍</a>。 |
| --uninstall=<package_name>   | 卸载指定软件。若指定“--uninstall=npu”，将会卸载driver和firmware。 |
| --upgrade=<package_name>     | 升级指定软件。若指定“--upgrade=npu”，将会升级driver和firmware。 |
| --test=<target>              | 检查指定组件能否正常工作。                                   |

## <a name="scene">安装场景介绍</a>

离线部署工具提供几个基本安装场景。

| 安装场景  | 安装的组件                                                   | 说明                   |
| --------- | ------------------------------------------------------------ | ---------------------- |
| auto      | all                                                          | 安装所有能找到的软件包 |
| infer_dev | driver、firmware、 nnrt、toolbox、toolkit、 torch、tfplugin、tensorflow | 推理开发场景           |
| infer_run | driver、 firmware、nnrt、toolbox                             | 推理运行场景           |
| train_dev | driver、firmware、nnae、toolbox、toolkit、torch、tfplugin、tensorflow | 训练开发场景           |
| train_run | driver、firmware、nnae、toolbox、torch、tfplugin、tensorflow | 训练运行场景           |
| vmhost    | driver、firmware、toolbox                                    | 虚拟机host场景         |

上述安装场景的配置文件位于scene目录下，如推理开发场景的配置文件scene/scene_infer_run.yml:

```
- hosts: '{{ hosts_name }}'

- name: install system dependencies
  import_playbook: ../playbooks/install/install_sys_pkg.yml

- name: install python3.7.5
  import_playbook: ../playbooks/install/install_python375.yml

- name: install driver and firmware
  import_playbook: ../playbooks/install/install_npu.yml

- name: install nnrt
  import_playbook: ../playbooks/install/install_nnrt.yml

- name: install toolbox
  import_playbook: ../playbooks/install/install_toolbox.yml

- name: install toolkit
  import_playbook: ../playbooks/install/install_toolkit.yml

- name: install torch
  import_playbook: ../playbooks/install/install_torch.yml

- name: install tfplugin
  import_playbook: ../playbooks/install/install_tfplugin.yml

- name: install tensorflow
  import_playbook: ../playbooks/install/install_tensorflow.yml

- name: install protobuf
  import_playbook: ../playbooks/install/install_protobuf.yml
```

如需自定义安装场景，可参考上述配置文件进行定制。
##  <a name="config">配置说明</a>
### 代理配置
在downloader/config.ini文件中配置代理，内容如下：
```
[proxy]
enable=false         # 是否开启代理配置参数
verify=true         # 是否校验https证书
protocol=http
hostname=openproxy.huawei.com
port=8080
username=none       # 代理账号
userpassword=none   # 代理密码
```
### 下载行为配置
在downloader/config.ini文件中可进行下载行为配置，将其调整为下载所需OS的组件。
```
[download]
os_list=CentOS_7.6_aarch64, CentOS_7.6_x86_64, CentOS_8.2_aarch64, CentOS_8.2_x86_64, Ubuntu_18.04_aarch64, Ubuntu_18.04_x86_64, BigCloud_7.6_aarch64, BigCloud_7.6_x86_64, ...          # 待安装部署的环境OS信息
```
###  <a name="sourceconfig">源配置</a>
离线安装工具已提供源配置文件，用户可根据实际进行替换。
-  Python源配置
在downloader/config.ini文件中配置python源，默认使用华为源。
    ```
[pypi]
index_url=http://mirrors.huaweicloud.com/pypi/simple
    ```
- 系统源配置
系统源配置文件downloader/config/*{os}\__{version}\__{arch}*/source.*xxx*
以CentOS 7.6 aarch64为例，源配置文件downloader/config/CentOS_7.6_aarch64/source.repo内容如下：
```
[base]
baseurl=http://mirrors.huaweicloud.com/centos-altarch/7/os/aarch64

[epel]
baseurl=http://mirrors.huaweicloud.com/epel/7/aarch64
```
表明同时启用base源和epel源，下载系统组件时会从这两个源中查询和下载。默认使用华为源，可根据需要修改。若删除源，可能造成组件下载不完整。