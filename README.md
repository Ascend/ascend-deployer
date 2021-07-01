# 简介

## 功能描述

离线安装工具提供系统组件、python第三方依赖自动下载以及一键式安装的功能，并支持驱动、固件以及CANN软件包的安装。tools目录额外放置了Device IP配置脚本，使用方法可参考<a href="#Device_IP">Device IP配置说明</a>。

## 环境要求

### 支持的操作系统说明

| 操作系统 | 版本      | CPU架构 | 安装类型                                |
|:-------:|:---------:|:-------:|:--------------------------------------:|
| BCLinux | 7.6       | aarch64 | 镜像默认Minimal模式                     |
| BCLinux | 7.6       | x86_64  | 镜像默认Minimal模式                     |
| BCLinux | 7.7       | aarch64 | 镜像默认Minimal模式                     |
| CentOS  | 7.6       | aarch64 | 镜像默认Minimal模式                     |
| CentOS  | 7.6       | x86_64  | 镜像默认Minimal模式                     |
| CentOS  | 8.2       | aarch64 | 镜像默认Minimal模式                     |
| CentOS  | 8.2       | x86_64  | 镜像默认Minimal模式                     |
| Debian  | 9.9       | aarch64 | 镜像默认Minimal模式                     |
| Debian  | 9.9       | x86_64  | 镜像默认Minimal模式                     |
| Debian  | 10.0      | x86_64  | 镜像默认Minimal模式                     |
| EulerOS | 2.8       | aarch64 | 镜像默认Minimal模式                     |
| EulerOS | 2.9       | aarch64 | 镜像默认Minimal模式                     |
| EulerOS | 2.9       | x86_64  | 镜像默认Minimal模式                     |
| Kylin   | V10Tercel | aarch64 | 镜像默认Minimal模式                     |
| Kylin   | V10Tercel | x86_64  | 镜像默认Minimal模式                     |
| Kylin   | v10juniper| aarch64 | 镜像默认Minimal模式                     |
| Linx    | 6         | aarch64 | 镜像默认Minimal模式                     |
|OpenEuler|20.03LTS-SP1| aarch64| 镜像默认Minimal模式                     |
|OpenEuler|20.03LTS-SP1| x86_64 | 镜像默认Minimal模式                     |
|OpenEuler|  20.03LTS  | aarch64| 镜像默认Minimal模式                     |
|OpenEuler|  20.03LTS  | x86_64 | 镜像默认Minimal模式                     |
| SLES    | 12.4      | x86_64  | 镜像默认Minimal模式                     |
| SLES    | 12.5      | x86_64  | 镜像默认Minimal模式                     |
| Tlinux  | 2.4       | aarch64 | 镜像默认Server模式                      |
| Tlinux  | 2.4       | x86_64  | 镜像默认Server模式                      |
| UOS     | 20SP1     | aarch64 | 镜像默认Minimal模式                     |
| UOS     | 20SP1     | x86_64  | 镜像默认Minimal模式                     |
| UOS     | 20        | aarch64 | 镜像默认Minimal模式                     |
| UOS     | 20        | x86_64  | 镜像默认Minimal模式                     |
| Ubuntu  | 18.04.1/5 | aarch64 | 镜像默认Minimal模式                     |
| Ubuntu  | 18.04.1/5 | x86_64  | 镜像默认Minimal模式                     |
| Ubuntu  | 20.04     | aarch64 | 镜像默认Minimal模式                     |
| Ubuntu  | 20.04     | x86_64  | 镜像默认Minimal模式                     |

### 支持的硬件形态说明

|  中心推理硬件  |  中心训练硬件  |  智能边缘硬件  |
|:-------------:|:-------------:|:-------------:|
|  A300-3000    |  A300T-9000   |  A500 Pro-3000|
|  A300-3010    |  A800-9000    |               |
|  A300I Pro    |  A800-9010    |               |
|  A800-3000    |               |               |
|  A800-3010    |               |               |


## 注意事项

- 操作系统必须安装tar、cd、ls、find、grep、chown、chmod、unzip、ssh等基本命令。建议在Ubuntu/Debian系统的安装过程中，到【Software selection】这一步时勾选上【OpenSSH server】/【SSH server】这一选项，避免缺失ssh命令。
- 离线安装工具仅支持OS镜像安装成功后的默认环境，请不要在安装OS后额外安装或卸载软件。若已卸载某些系统软件，导致与安装默认系统包不一致，需手动配置网络，通过apt、yum、dnf等工具安装配置缺失软件。
- 离线安装工具只能安装最基本的库，确保TensorFlow和PyTorch能够运行。若需运行较为复杂的推理业务或模型训练，模型代码中可能包含具体业务相关的库，这些库需用户自行安装。
- SLES安装驱动时，离线安装工具会设置/etc/modprobe.d/10-unsupported-modules.conf里的“allow_unsupported_modules ”的值为“1”，表示允许系统启动过程中加载非系统自带驱动。
- EulerOS等很多操作系统默认禁止root用户远程连接，所以需提前配置/etc/ssh/sshd_config中PermitRootLogin为yes（个别OS配置方法或许不同，请参考OS官方说明）；用完本工具后，及时关闭root用户远程连接
- 支持Ubuntu 18.04.1/5、Ubuntu 20.04 x86_64安装交叉编译的相关组件和aarch64架构的toolkit软件包。
- Atlas 300T 训练卡低版本内核（低于4.5）的CentOS 7.6 x86_64需要将CentOS升级至8.0及以上或添加内核补丁，否则可能导致固件安装失败。添加内核补丁的方法请参考[参考链接](https://support.huawei.com/enterprise/zh/doc/EDOC1100162133/b56ad5be)
- Kylin v10系统安装系统依赖后，需等待系统配置完成，方可正常使用docker等命令。
- Linx 系统，需修改/etc/pam.d/su文件，取消auth sufficient pam_rootok.so前的注释，使root用户su切换其他用户不用输入密码。
- Tlinux系统默认安装完后，/根目录总空间约为20G，resources目录下不可放置超过其磁盘可用空间的包，避免解压或安装失败。
- EulerOS、SLES、Debian等系统安装驱动时可能会触发驱动源码编译，需要用户自行安装跟系统内核版本（可通过 `uname -r` 命令查看）一致的内核头软件包，具体如下。

### 内核头软件包说明
| 操作系统     | 跟系统内核版本一致的内核头软件包                                    | 获取来源            |
| ---------   | ---------------------------------------------------------------- | --------------------|
| EulerOS     | kernel-headers-`<version>`、kernel-devel-`<version>`                 | 联系OS厂商，或在对应版本OS附带的"devel_tools.tar.gz"工具组件内查找 |
| SLES        | kernel-default-`<version>`、kernel-default-devel-`<version>`         | 联系OS厂商，或在对应版本OS的镜像内查找 |
| Debian      | linux-headers-`<version>`、linux-headers-`<version>`-common、linux-kbuild-`<version>`| 联系OS厂商，或在对应版本OS的镜像内查找 |

## 安装

### pip安装

```bash
pip3 install ascend-deployer -i https://pypi.mirrors.ustc.edu.cn/simple/
```
版本要求：python >= 3.6

### git安装

```bash
git clone https://gitee.com/ascend/ascend-deployer.git
```

### 下载zip安装

点击右上角“克隆/下载”按钮，然后点击下方“下载zip”,下载后解压使用。

# 操作指导:源码方式

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
     运行start_download.bat或start_download_ui.bat（推荐使用，可在弹出的简易UI界面上勾选需要下载的OS或PKG相关组件）。

- linux

  1. 执行`./start_download.sh --os-list=<OS1>,<OS2> --download=<PK1>,<PK2>==<Version>`启动下载；以下调用`**.sh`脚本采用`./**.sh`的方式，也可使用`bash **.sh`调用，请根据实际使用。
  2. 支持root和非root用户执行下载操作，非root用户不必拥有sudo权限，但需拥有本工具目录的可执行权限；执行下载时会先检查环境上是否存在python3，如果python3不存在时，分2种：如果当前用户是root用户，本工具会通过apt、yum等工具自动下载python3；如果当前用户是非root用户，本工具会提示用户自行安装python3；2种情况下均请用户保证环境网络和源可用.
## 安装操作

### 安装参数

- 安装过程基本参数可通过inventory_file文件配置

默认配置如下：

```bash
[ascend]
localhost ansible_connection='local'

[ascend:vars]
user=HwHiAiUser
group=HwHiAiUser
install_path=/usr/local/Ascend
```

| 配置项          | 说明                                    |
|:------------ |:------------------------------------- |
| user         | 用户，该参数将传递给run包的--install-username选项   |
| group        | 用户组，该参数将传递给run包的--install-usergroup选项 |
| install_path | CANN软件包的安装路径，该参数将传递给run包的--install-path选项     |

### 安装须知

- install_path参数只能指定CANN软件包的安装路径，root用户安装时该参数有效，非root用户安装时该参数无效（只能安装到默认路径~/Ascend）；install_path参数不指定驱动包的安装路径和边缘组件(atlasedge和ha)，驱动包和边缘组件(atlasedge和ha)只能安装到默认路径/usr/local/Ascend
- 驱动、CANN软件包，会使用HwHiAiUser用户和用户组作为软件包默认运行用户，用户需自行创建。 创建用户组和用户的命令如下：

```bash
#添加HwHiAiUser用户组
groupadd HwHiAiUser

#添加HwHiAiUser用户,并加入HwHiAiUser用户组
#设置HwHiAiUser的HOME目录为/home/HwHiAiUser
#并设置用户的shell为/bin/bash
useradd -g HwHiAiUser -d /home/HwHiAiUser -m HwHiAiUser -s /bin/bash
```

- 若用户需自行指定运行用户和用户组，可在创建用户和用户组后自行修改inventory_file文件。文件内容如下：

```
[ascend:vars]
user=HwHiAiUser
group=HwHiAiUser
```

- 由于需要安装大量开源软件，离线安装工具下载的开源软件均来自操作系统源，开源软件的漏洞和修复需要用户自行根据情况修复，强烈建议使用官方源并定期更新。
- 非root用户支持安装的软件列表

| 软件名                 | 说明                                  |
|:---------------------- |:------------------------------------- |
| python375、gcc         | python3.7.5和gcc7.3.0，安装在$HOME/.local/目录下  |
| python框架             | tensorflow、pytorch、mindspore           |
| CANN                   | toolbox、nnae、nnrt、tfplugin、toolkit，默认安装在$HOME目录下，不支持指定路径安装 |
| MindStudio             | 安装在$HOME/目录下  |

注意：
  1. 非root用户需要root用户安装系统组件和driver后才可以安装以上组件。
  2. 非root用户需要加入driver安装的属组，才可以正常安装和使用nnrt和toolkit组件，driver默认安装的属组为HwHiAiUser。修改用户组命令如下：

```bash
usermod -a -G HwHiAiUser 非root用户名
```

### 准备软件包

1. 根据实际需要准备待安装软件包（支持驱动、固件、CANN软件包的安装），将待安装软件包放置于resources目录下，参考如下：
   - 驱动和固件：[获取链接](https://ascend.huawei.com/#/hardware/firmware-drivers)
   - CANN软件包：[获取链接](https://ascend.huawei.com/#/software/cann)
2. 软件包支持zip包和run包2种格式，如果resources目录下存在这2种格式的同一软件包，优先安装zip格式的软件包；安装时resources目录下只应存在一个版本的软件包，否则可能会有版本不配套的情况。
3. 支持Atlas 500和Atlas 500Pro批量安装IEF Agent，参考usermanual-ief文档准备IEF产品证书、注册工具、安装工具，放置于resources目录下；
   - IEF相关证书和工具：[参考链接](https://support.huaweicloud.com/usermanual-ief/ief_01_0031.html)
   - Atlas 500已预置了注册工具和安装工具，所以只需准备产品证书放置于resources目录下；而Atlas 500Pro对这3个证书和工具都需要
   - Atlas 500只支持自带的EulerOS2.8 aarch64裁剪版操作系统，不支持其他系统，因此也不支持离线部署工具本地运行，只支持远程安装，也不支持非root安装；Atlas 500Pro支持本地和远程安装
   - 依赖边缘节点atlasedge中间件正常工作，Atlas 500自带atlasedge中间件，Atlas 500Pro需要先安装atlasedge中间件
   - 依赖IEF服务器正常工作，且边缘设备与IEF之间网络正常，边缘节点是否成功纳管需到IEF的web前端观察，其他限制请参考usermanual-ief文档
4. docker镜像文件需用户登录ascendhub，拉取镜像后将镜像转存至resources/docker_images目录下，方可进行docker镜像的安装；docker镜像文件命名格式参考ubuntu_18.04_{x86_64 | aarch64}.tar，大括号内为系统架构，仅支持括号内的两种架构。

```
ascend-deployer
|- ...
|- install.sh
|- inventory_file
|- ...
|- playbooks
|- README.md
|- resources
   |- A300-3010-npu_xxx.zip
   |- A300-3010-npu-driver_xxx.run
   |- A300-3010-npu-firmware_xxx.run
   |- Ascend-cann-nnrt-xxx.zip
   |- Ascend-cann-nnrt-xxx.run
   |- ...
   |- Ascend-cann-toolkit-xxx.run
   |- ...
   |- BCLinux_7.6_aarch64
   |- BCLinux_7.6_x86_64
   |- cert_ief_xxx.tar.gz
   |- edge-installer_xxx_arm64.tar.gz
   |- edge-register_xxx_arm64.tar.gz
   |- docker_images
   |- ...
```

### 单机安装

1. 配置单机的inventory_file文件。
    编辑inventory_file文件，格式如下：

   ```
   [ascend]
   localhost ansible_connection='local' # root用户
   ```

2. 执行安装脚本，可根据需要选择安装方式（指定软件安装或指定场景安装）。

   - 指定软件安装
     `./install.sh --install=<package_name>`
     <package_name>可选范围可通过执行`./install.sh --help`查看。命令示例如下：
     `./install.sh --install=npu     //安装driver和firmware`
     注意事项：
     - 请按照“driver>firmware>CANN软件包（toolkit、nnrt等）”或“npu>CANN软件包（toolkit、nnrt等）”的顺序进行安装。
     - 安装driver或firmware后，需执行`reboot`重启设备使驱动和固件生效。
     - 部分组件存在运行时依赖，如pytorch需要toolkit提供运行时依赖，tensorflow + npubridge需要tfplugin提供运行时依赖，mindspore_ascend需要driver和toolkit提供运行时的依赖。
     - 所有python库的安装都必须先安装python3.7.5，如pytorch、tensorflow、mindspore等。
     - mindspore_ascend需要安装其版本配套的driver和toolkit才能正常使用，软件配套说明详见[Mindspore官网](https://mindspore.cn/install)。
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
   ip_address_1 ansible_ssh_user='root' ansible_ssh_pass='password1'      # root用户
   ip_address_2 ansible_ssh_user='root' ansible_ssh_pass='password2'
   ip_address_3 ansible_ssh_user='username' ansible_ssh_pass='password3'  # 非root用户
   ```

   #### 注意事项：

- inventory_file_文件中会配置远程设备的用户名和密码。本工具会使用ansible-vault对配置有密码的inventory_file_文件进行加密，配置完成后须执行./install.sh --check或者install、test等命令才能完成对该文件的加密，否则可能导致账户密码的泄露。
- 需要在inventory_file中配置密码时，建议先使用ansible-valut加密文件，再使用ansible-vault edit编辑文件。

```bash
ansible-vault encrypt inventory_file        // 加密文件
ansible-vault edit inventory_file           // 编辑加密后的文件
```
- 设置环境变量ANSIBLE_VAULT_PASSWORD_FILE可以指定ansible-valut密码的文件；例如，如果用户设置ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass.txt，Ansible将自动在该文件中搜索密码，避免用户交互式输入ansible-valut密码；该功能由ansible提供，详情请参见[ansible官方文档](https://docs.ansible.com/ansible/latest/user_guide/vault.html)。

2. 执行`./install.sh --check`测试待安装设备连通性。
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

# 操作指导:pip方式

当本工具使用pip安装时，将提供2个入口方便操作

- ascend-download     下载器
- ascend-deployer     部署器

非root用户安装后如果找不到这两个命令，需要配置PATH环境变量，配置命令如下：

```bash
export PATH=~/.local/bin:$PATH
```

## 下载

```bash
ascend-download --os-list=<OS1>,<OS2> --download=<PK1>,<PK2>==<Version>
```

Win 10和Linux均可执行

- 所有资源下载至ascend-deployer/resources

- windows下在执行命令的当前目录生成ascend-deployer目录。下载完成后将
  整个目录拷贝至待部署linux服务器即可使用。

- linux下将在HOME目录下生成ascend-deployer目录。可通过设置环境变量ASCEND_DEPLOYER_HOME修改该目录。

## 安装

```bash
ascend-deployer --install=<pkg1,pkg2>
```

ascend-deployer本质上是install.sh的一个wrapper。
使用方法与直接执行ascend-deployer目录中的install.sh完全相同。
ascend-deployer命令将自动寻找${ASCEND_DEPLOYER_HOME}/ascend-deployer/install.sh文件执行。
ASCEND_DEPLOYER_HOME目录默认值与用户HOME相同，非root用户须保证该目录存在且能正常读写。
非root用户不需要sudo权限也可执行安装。

# 配置环境变量

离线部署工具可以安装python3.7.5，为不影响系统自带python(python2.x or python3.x)， 在使用python3.7.5之前，需配置如下环境变量:

```
export PATH=/usr/local/python3.7.5/bin:$PATH                         # root
export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH   # root

export PATH=~/.local/python3.7.5/bin:$PATH                           # non-root
export LD_LIBRARY_PATH=~/.local/python3.7.5/lib:$LD_LIBRARY_PATH     # non-root
```
本工具执行安装操作时会自动在本机安装python3.7.5，并把以上环境变量内容写进/usr/local/ascendrc文件内，执行如下命令便可轻松设置python3.7.5的环境变量
```
source /usr/local/ascendrc     # root
source ~/.local/ascendrc       # non-root
```

同样，离线部署工具安装的其他软件包或工具，需用户参考相应的官方资料后配置环境变量或进行其他设置后，方可正常使用。

# 后续任务

- 推理场景

开发者可以参见《[CANN 应用软件开发指南 (C&C++)](https://www.huaweicloud.com/ascend/cann)》或《[CANN 应用软件开发指南 (Python)](https://www.huaweicloud.com/ascend/cann)》在开发环境上开发应用程序。

- 训练场景
  若需进行网络模型移植和训练，请参考《[TensorFlow网络模型移植&训练指南](https://www.huaweicloud.com/ascend/pytorch-tensorflow)》或《[PyTorch网络模型移植&训练指南](https://www.huaweicloud.com/ascend/pytorch-tensorflow)》。
- 删除工具
  本工具属于安装部署类工具，系统安装完成后应立即删除以释放磁盘空间。

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
- 请按照“CANN软件包（toolkit、nnrt等）>driver和firmware（driver和firmware无卸载顺序要求）“的顺序进行卸载。
- root用户卸载默认路径/usr/local/Ascend的npu包(driver和firmware)和边缘组件(atlasedge和ha)，root用户卸载inventory_file内install_path参数指定路径的CANN软件包，非root用户卸载默认路径~/Ascend的CANN软件包。
- 不支持非root用户卸载npu(driver和firmware)和边缘组件(atlasedge和ha)，不支持卸载npu(driver和firmware)和边缘组件(atlasedge和ha)时带有--uninstall-version参数。

# 更新离线部署工具

能够通过以下操作实现离线安装工具自我更新。

- windows
  运行upgrade_self.bat启动更新。
- linux
  执行命令`./upgrade_self.sh`启动更新。

# 参考信息

## <a name="parameter">安装参数说明</a>

用户根据实际需要选择对应参数完成安装、升级或卸载，命令格式如下：
`./install.sh [options]`
参数说明请参见下表。表中各参数的可选参数范围可通过执行`./install.sh --help`查看。

| 参数                                | 说明                                                   |
|:--------------------------------- | ---------------------------------------------------- |
| --help  -h                        | 查询帮助信息。                                              |
| --check                           | 检查环境，确保控制机安装好python3.7.5、ansible等组件，并检查与待安装设备的连通性。   |
| --clean                           | 清理待安装设备用户家目录下的resources目录。                           |
| --nocopy                          | 在批量安装时不进行资源拷贝。                                       |
| --debug                           | 开发调测使用。                                                    |
| --output-file=<output_file>       | 重定向命令执行的输出结果到指定文件。                                   |
| --stdout_callback=<callback_name> | 设置命令执行的输出格式，可用的参数通过"ansible-doc -t callback -l"命令查看。 |
| --install=<package_name>          | 指定软件安装。若指定“--install=npu”，将会安装driver和firmware。       |
| --install-scene=<scene_name>      | 指定场景安装。安装场景请参见<a href="#scene">安装场景介绍</a>。        |
| --uninstall=<package_name>        | 卸载指定软件。若指定“--uninstall=npu”，将会卸载driver和firmware。     |
| --uninstall-version=<version>     | 卸载指定版本的软件，与--uninstall参数一起使用。                       |
| --upgrade=<package_name>          | 升级指定软件。若指定“--upgrade=npu”，将会升级driver和firmware。       |
| --test=<target>                   | 检查指定组件能否正常工作。                                            |
| --display=<target>                | 显示已安装软件包。                                                   |

## <a name="parameter">下载参数说明</a>

| 参数                  | 说明                      |
|:------------------- | ----------------------- |
| `--os-list=<OS1>,<OS2>` | 指定下载的特定操作系统的相关依赖软件      |
| `--download=<PK1>,<PK2>==<Version>`| 指定下载可选的软件包。例如MindStudio、CANN |

当前MindStudio支持下载2.0.0、3.0.1版本，CANN支持下载20.2.RC1、5.0.1版本，安装时resources目录下只应存在一个版本的MindStudio或CANN包，否则可能会有版本不配套的情况；`./start_download.sh --download=<PK1>,<PK2>==<Version>`，当`<Version>`为空时，会下载最新版本的`<PK>`；MindStudio的安装请参考[安装MindStudio](https://gitee.com/ascend/ascend-deployer/blob/master/docs/Install_MindStudio.md)

## <a name="scene">安装场景介绍</a>

离线部署工具提供几个基本安装场景。

| 安装场景     | 安装的组件                                                        | 说明            |
| ---------   | ---------------------------------------------------------------- | ----------------|
| auto        | all                                                              | 安装所有能找到的软件包 |
| vmhost      | sys_pkg、npu、toolbox                                            | 虚拟机场景             |
| edge        | sys_pkg、atlasedge、ha                                           | 安装MindX中间件、HA    |
| offline_dev | sys_pkg、python375、npu、toolkit                                  | 离线开发场景          |
| offline_run | sys_pkg、python375、npu、nnrt                                     | 离线运行场景          |
| mindspore   | sys_pkg、python375、npu、toolkit、mindspore                       | mindspore场景         |
| tensorflow_dev | sys_pkg、python375、npu、toolkit、tfplugin、tensorflow         | tensorflow开发场景    |
| tensorflow_run | sys_pkg、python375、npu、nnae、tfplugin、tensorflow            | tensorflow运行场景    |
| pytorch_dev | sys_pkg、python375、npu、toolkit、pytorch                         | pytorch开发场景       |
| pytorch_run | sys_pkg、python375、npu、nnae、pytorch                            | pytorch运行场景       |

上述安装场景的配置文件位于scene目录下，如auto场景的配置文件scene/scene_auto.yml:

```
- hosts: '{{ hosts_name }}'

- name: install system dependencies
  import_playbook: ../install/install_sys_pkg.yml

- name: install python3.7.5
  import_playbook: ../install/install_python375.yml

- name: install driver and firmware
  import_playbook: ../install/install_npu.yml

- name: install toolkit
  import_playbook: ../install/install_toolkit.yml

- name: install nnrt
  import_playbook: ../install/install_nnrt.yml

- name: install nnae
  import_playbook: ../install/install_nnae.yml

- name: install tfplugin
  import_playbook: ../install/install_tfplugin.yml

- name: install toolbox
  import_playbook: ../install/install_toolbox.yml

- name: install pytorch
  import_playbook: ../install/install_pytorch.yml

- name: install tensorflow
  import_playbook: ../install/install_tensorflow.yml

- name: install mindspore
  import_playbook: ../install/install_mindspore.yml
```

如需自定义安装场景，可参考上述配置文件进行定制。

## <a name="config">配置说明</a>

### 代理配置

如需使用http代理，其一是在环境变量中配置代理（推荐），其二是在downloader/config.ini文件中配置代理。
如果下载过程中出现证书错误，可能是代理服务器有证书替换的安全机制，则需要先安装代理服务器证书。

1. 环境变量中配置代理，参考如下
   
   ```
   # 配置环境变量
   export http_proxy="http://user:password@proxyserverip:port"
   export https_proxy="http://user:password@proxyserverip:port"
   ```
   
   其中user为用户在内部网络中的用户名，password为用户密码（特殊字符需转义），proxyserverip为代理服务器的ip地址，port为端口。

2. 在downloader/config.ini文件中配置代理，内容如下：
   
   ```
   [proxy]
   enable=false        # 是否开启代理配置参数
   verify=true         # 是否校验https证书
   protocol=https      # HTTP协议
   hostname=           # 代理服务器
   port=               # 端口
   username=none       # 代理账号
   userpassword=none   # 代理密码
   ```
   
   需将enable参数改为true，并配置可用的hostname、port、username、userpassword。
   安全起见，如果在downloader/config.ini文件中配置过代理账号及密码,下载完成后应清理掉config.ini

### 下载行为配置

在downloader/config.ini文件中可进行下载行为配置，将其调整为下载所需OS的组件。

```
[download]
os_list=CentOS_7.6_aarch64, CentOS_7.6_x86_64, CentOS_8.2_aarch64, CentOS_8.2_x86_64, Ubuntu_18.04_aarch64, Ubuntu_18.04_x86_64, ...          # 待安装部署的环境OS信息
```

### <a name="sourceconfig">源配置</a>

离线安装工具已提供源配置文件，用户可根据实际进行替换。

- Python源配置
  在downloader/config.ini文件中配置python源，默认使用华为源。

```
[pypi]
index_url=https://repo.huaweicloud.com/repository/pypi/simple
```

- 系统源配置
  系统源配置文件downloader/config/*{os}\__{version}\__{arch}*/source.*xxx*
  以CentOS 7.6 aarch64为例，源配置文件downloader/config/CentOS_7.6_aarch64/source.repo内容如下：

```
[base]
baseurl=https://mirrors.huaweicloud.com/centos-altarch/7/os/aarch64

[epel]
baseurl=https://mirrors.huaweicloud.com/epel/7/aarch64
```

表明同时启用base源和epel源，下载系统组件时会从这两个源中查询和下载。默认使用华为源，可根据需要修改。若修改，请选择安全可靠的源，并测试下载和安装行为是否正常，否则可能造成组件下载不完整或安装异常。若删除源，可能造成组件下载不完整。

# 其他安装指导

## <a name="Device_IP">Device IP配置说明</a>

此脚本的作用是修改NPU板卡IP地址，可利用ansible工具的批量部署能力实现批量配置，以下内容仅供有批量配置使用场景的用户参考使用。

### 数据准备

- 服务器的操作系统IP（OS IP）地址文件
- 服务器的操作系统用户名和密码
- 待配置的Device IP地址文件
- Device IP配置脚本（DeviceIP-conf.sh）

### 说明

- Device IP指的是待修改的NPU板卡IP地址。
- 服务器的操作系统IP（OS IP）地址文件和待配置的Device IP地址文件的格式请参考<a href="#IP格式说明">OS IP地址和Device IP地址格式说明</a>。
- 批量操作不支持混合设备类型，即所选设备的设备类型、NPU标卡数量及配置的IP地址个数、工作模式必须一致。
- 每台服务器有2块NPU板，每块NPU板有4个NPU芯片。SMP模式下每块NPU板上的4个NPU芯片需要配置4个不同网段的IP地址。

### 操作步骤

1. 将OS IP地址文件、Device IP地址文件、Device IP配置脚本上传到目标主机的指定目录（例如分别是/root/uploadosip、/root/uploaddeviceip、/root/uploaddeviceip）。

2. 在目标主机指定目录（例如/root/uploaddeviceip）执行命令
   
   ```
   bash DeviceIP-conf.sh [ 设备类型 ] [ NPU标卡数量 ] [ NPU标卡IP配置 ] [ 工作模式 ] [ OS IP地址文件 ] [ Device IP地址文件 ]
   ```
   
   以8个非标NPU板卡的采用SMP模式的A800-9000为例，命令为
   
   ```
   bash DeviceIP-conf.sh 1 0 0 SMP /root/uploadosip/OS_IP /root/uploaddeviceip/Device_IP
   ```

| 参数        | 参数说明            | 参数取值 | 备注                                        |
|:---------:|:---------------:|:----:|:-----------------------------------------:|
| 设备类型      | 8个NPU的A800-9000 | 1    | npu-smi info查询NPU数量为8，则输入1，查询NPU数量为4，则输入2 |
| NPU标卡数量   | 不是NPU标卡         | 0    | 同NPU标卡数量，A800-9000请设置为0                   |
| NPU标卡IP配置 | 不是NPU标卡         | 0    | 同NPU标卡IP数量，A800-9000请设置为0                 |
| 工作模式      | SMP             | 0    | 根据实际配置，SMP(对称多处理器模式）、AMP（非对称多处理器模式）       |

### <a name="IP格式说明">OS IP地址和Device IP地址格式说明</a>

需要将这2个文件转换为UNIX格式

1. OS IP地址文件
- 格式1（推荐）
  IP地址段，类似这个IPx-IPy，以回车结束，例如：
  
  ```
  10.80.100.101~10.80.100.104
  ```

- 格式2
  IP地址清单，逐一给出OS IP地址，以回车结束，例如：
  
  ```
  10.80.100.101
  10.80.100.102
  10.80.100.103
  10.80.100.104
  ```
2. Device IP地址文件
- 格式1（推荐）
  IP地址段，类似这个IPx-IPy/Netmask/Gateway的格式，SMP模式下每块NPU板上的4个NPU芯片需要配置4个不同网段的Device IP地址，以回车结束，例如：
  
  ```
  172.168.1.100~172.168.1.107/255.255.255.0/172.168.1.1
  172.168.2.100~172.168.2.107/255.255.255.0/172.168.2.1
  172.168.3.100~172.168.3.107/255.255.255.0/172.168.3.1
  172.168.4.100~172.168.4.107/255.255.255.0/172.168.4.1
  ```

- 格式2
  IP地址清单，类似这个IP/Netmask/Gateway的格式，逐一给出OS IP地址，以回车结束，例如：
  
  ```
  172.168.1.100/255.255.255.0/172.168.1.1
  172.168.2.100/255.255.255.0/172.168.2.1
  172.168.3.100/255.255.255.0/172.168.3.1
  172.168.4.100/255.255.255.0/172.168.4.1
  ```
