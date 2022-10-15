# 简介

## 功能描述

离线安装工具提供系统组件、python第三方依赖自动下载以及一键式安装的功能，并支持驱动、固件以及CANN软件包的安装。tools目录额外放置了Device IP配置脚本，使用方法可参考[Device IP配置](https://gitee.com/ascend/ascend-deployer/blob/master/docs/Device_IP_Configuration.md)。

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
| Kylin   | V10GFB    | aarch_64| 镜像默认Minimal模式                     |
| Kylin   | v10juniper| aarch64 | 镜像默认Minimal模式                     |
| Linx    | 6         | aarch64 | 镜像默认Minimal模式                     |
|OpenEuler|  20.03LTS  | aarch64| 镜像默认Minimal模式                     |
|OpenEuler|  20.03LTS  | x86_64 | 镜像默认Minimal模式                     |
| SLES    | 12.4      | x86_64  | 镜像默认Minimal模式                     |
| SLES    | 12.5      | x86_64  | 镜像默认Minimal模式                     |
| Tlinux  | 2.4       | aarch64 | 镜像默认Server模式                      |
| Tlinux  | 2.4       | x86_64  | 镜像默认Server模式                      |
| UOS     | 20SP1     | aarch64 | 镜像默认Minimal模式                     |
| UOS     | 20SP1     | x86_64  | 镜像默认Minimal模式                     |
| UOS     | 20-1020e  | aarch64 | 镜像默认Minimal模式                     |
| UOS     | 20-1021e  | aarch64 | 镜像默认Minimal模式                     |
| UOS     | 20        | aarch64 | 镜像默认Minimal模式                     |
| UOS     | 20        | x86_64  | 镜像默认Minimal模式                     |
| Ubuntu  | 18.04.1/5 | aarch64 | 镜像默认Minimal模式                     |
| Ubuntu  | 18.04.1/5 | x86_64  | 镜像默认Minimal模式                     |
| Ubuntu  | 20.04.1   | aarch64 | 镜像默认Minimal模式                     |
| Ubuntu  | 20.04.1   | x86_64  | 镜像默认Minimal模式                     |

### 支持的硬件形态说明

|  中心推理硬件  |  中心训练硬件    |  智能边缘硬件  |
|:-------------:|:---------------:|:-------------:|
|  A300-3000    |  A300T-9000     |  A500 Pro-3000|
|  A300-3010    |  A800-9000      |  Atlas200(EP) |
|  A300I Pro    |  A800-9010      |               |
|  A300V Pro    |  Atlas 300T Pro |               |
|  A300I DUO    |                 |               |
|  A800-3000    |                 |               |
|  A800-3010    |                 |               |
|  A300V        |                 |               |


## 注意事项

- 如果系统的gcc版本低于7.3.0，离线安装工具会自动安装，该过程耗时较长；用户也可通过手动提前升级并配置环境变量的方式来规避该自动升级。
- 离线安装工具默认下载和安装Python-3.7.5作为CANN软件包的配套Python版本，以下全文相关处均以Python-3.7.5进行解释说明。用户可以通过设置ASCEND_PYTHON_VERSION环境变量，或downloader/config.ini文件中的ascend_python_version配置项（同时设置时环境变量优先），自行选择Python版本，可选的Python版本为`3.7.0~3.7.11`和`3.8.0~3.8.11和3.9.0~3.9.9`。本工具仅在Python-3.7.5版本上经过全面适配和测试，强烈建议不要更改默认配置。
- Kylin V10 GFB系统下载系统依赖时下载Kylin_V10Tercel_aarch64即可。
- 如果SLES系统依赖下载失败，请用户自行修改opensuse的源。例如SLES12.4系统请修改downloader\config\SLES_12.4_x86_64\source.repo。
- 操作系统必须安装tar、cd、ls、find、grep、chown、chmod、unzip、bzip2、ssh等基本命令。建议在Ubuntu/Debian系统的安装过程中，到【Software selection】这一步时勾选上【OpenSSH server】/【SSH server】这一选项，避免缺失ssh命令。
- 离线安装工具仅支持OS镜像安装成功后的默认环境，请不要在安装OS后额外安装或卸载软件。若已卸载某些系统软件，导致与安装默认系统包不一致，需手动配置网络，通过apt、yum、dnf等工具安装配置缺失软件。
- 离线安装工具只能安装最基本的库，确保TensorFlow和PyTorch能够运行。若需运行较为复杂的推理业务或模型训练，模型代码中可能包含具体业务相关的库，这些库需用户自行安装。
- 离线安装工具除了install.sh、start_download.sh、start_download_ui.bat和start_download.bat外，其余文件并非设计给用户使用的接口或者命令，请勿直接使用。
- 禁止将密码放到inventory_file文件里。
- A300T训练卡低版本内核（低于4.5）的CentOS 7.6 x86_64需要将CentOS升级至8.0及以上或添加内核补丁，否则可能导致固件安装失败。添加内核补丁的方法请参考[参考链接](https://support.huawei.com/enterprise/zh/doc/EDOC1100162133/b56ad5be)。
- A300I Pro、A300V Pro、A300V、A300T-9000和Atlas 300T pro卡安装驱动或固件时必须在inventory_file中提前配置cus_npu_info变量, 其中, A300I pro须配置为300i-pro, A300V Pro须配置为300v-pro，A300V须配置为300v，A300T-9000须配置为300t，Atlas 300T Pro须配置为300t-pro。1U SOC形态安装驱动或固件和toolbox时必须在inventory_file中提前配置chip_name变量，值为310P。编辑inventory_file文件，格式如下：

   ```
   [ascend]
   localhost ansible_connection='local' cus_npu_info='300i-pro'  # A300I Pro
   ip_address_1 ansible_ssh_user='root' cus_npu_info='300v-pro'  # A300V Pro
   ip_address_2 ansible_ssh_user='root' cus_npu_info='300v'      # A300V
   ip_address_3 ansible_ssh_user='root' cus_npu_info='300t'      # A300T-9000
   ip_address_4 ansible_ssh_user='root' cus_npu_info='300t-pro'  # Atlas 300T Pro
   ip_address_5 ansible_ssh_user='root' chip_name='310P'         # 1U SOC
   ```
- 由于无法区分Atlas200 EP和A300推理卡（A300-3000、A300-3010、A800-3000、A800-3010）的硬件形态，Atlas200 EP场景使用本工具时需满足如下条件。不支持Atlas200 EP和A300推理卡环境批量部署；部署的机器包含Atlas200 EP时，resources目录下不要放置A300的NPU包，部署的机器包含A300推理卡时，resources目录下不要放置Atlas200 EP的NPU包；由于以上2条的限制，`--download=CANN`下载功能也不会包含Atlas200 EP的NPU包，请自行准备。
- SLES安装驱动时，离线安装工具会设置/etc/modprobe.d/10-unsupported-modules.conf里的“allow_unsupported_modules ”的值为“1”，表示允许系统启动过程中加载非系统自带驱动。
- EulerOS等很多操作系统默认禁止root用户远程连接，所以需提前配置/etc/ssh/sshd_config中PermitRootLogin为yes（个别OS配置方法或许不同，请参考OS官方说明）；用完本工具后，及时关闭root用户远程连接
- 支持Ubuntu 18.04.1/5安装交叉编译的相关组件和aarch64架构的toolkit软件包。
- Kylin v10系统安装系统依赖后，需等待系统配置完成，方可正常使用docker等命令。
- 由于CenOS下安装的docker/containerd等可以多版本并存，所以建议CentOS 7.6和CentOS 8.2系统安装系统依赖前请确认系统上是否已安装docker，如果已安装请使用`yum -y remove docker-ce`、`yum -y remove docker-ce-cli`、`yum -y remove containerd.io`命令卸载后再进行系统依赖的安装。
- 建议用户修改 downloader/config 和 downloader/requirements.txt 中的包版本，确保符合所在组织的安全要求。
- Tlinux系统默认安装完后，/根目录总空间约为20G，resources目录下不可放置超过其磁盘可用空间的包，避免解压或安装失败。
- BCLinux 7.6系统默认无python3，在执行下载操作时会先执行`yum install python3`命令。由于BCLinux 7.6系统源无python3组件，请用户参考BCLinux官方修改源配置文件，或直接将"/etc/yum.repos.d/BCLinux-Base.repo"里的"el7.6"字样改为"el7.7"(执行`sed -i 's/el7.6/el7.7/g' /etc/yum.repos.d/BCLinux-Base.repo`命令)，安装完成后请恢复原来的配置。
- 本工具不下载tensorflow-1.15.0 aarch64、tensorflow-2.6.5 aarch64、torch-1.5.0/apex-0.1 aarch64/x86_64和torch-1.8.1/apex-0.1/torch_npu-1.8.1 aarch64/x86_64的Python组件包，需用户自行准备后放置在resources/pylibs目录下，否则会跳过安装。
- tensorflow aarch64编译时请严格遵守官方的编译规范。
- tensorflow 1.15.0 仅适配python3.7，tensorflow 2.6.5 适配python3.7、python3.8、python3.9。由于依赖冲突，已安装一个版本后，安装另一个版本需先卸载已安装版本。
- 基于安全考虑，建议将ascend-deployer的下载和解压目录（ascend-deployer目录）进行加固，将其权限设置为仅允许本人使用。
- 如果准备在Linux下使用自动下载功能，请提前配置好GUI界面并直接运行下载指令。
- EulerOS、SLES、Debian等系统安装驱动时可能会触发驱动源码编译，需要用户自行安装跟系统内核版本（可通过 `uname -r` 命令查看）一致的内核头软件包，具体如下。

- 内核头软件包说明

| 操作系统     | 跟系统内核版本一致的内核头软件包                                    | 获取来源            |
| ---------   | ---------------------------------------------------------------- | --------------------|
| EulerOS     | kernel-headers-`<version>`、kernel-devel-`<version>`                 | 联系OS厂商，或在对应版本OS附带的"devel_tools.tar.gz"工具组件内查找 |
| SLES        | kernel-default-`<version>`、kernel-default-devel-`<version>`         | 联系OS厂商，或在对应版本OS的镜像内查找 |
| Debian      | linux-headers-`<version>`、linux-headers-`<version>`-common、linux-kbuild-`<version>`| 联系OS厂商，或在对应版本OS的镜像内查找 |

## 工具获取与安装

### pip安装

```bash
pip3 install ascend-deployer
```
- 版本要求：python >= 3.6
- 建议以root用户身份，使用系统自带python3及pip3工具安装，若无pip3请自行安装
- 非root用户请勿使用该方式进行安装。
- 使用方法参考<a href="#pip_manual">操作指导:pip方式</a>

### git安装

```bash
git clone https://gitee.com/ascend/ascend-deployer.git
```

基于安全考虑，用户在git clone前应将环境umask设置为077，并只在用户HOME目录下clone、使用工具，并仅供本用户自己使用。

### 下载zip安装

点击右上角“克隆/下载”按钮，然后点击下方“下载zip”，下载后解压使用（为了防止软件包在传递过程或存储期间被恶意篡改，建议用户下载软件包后使用sha256sum对软件进行完整性校验，当前最新正式版本的sha256sum请参考master分支的readme）。本工具支持root和非root用户使用。为避免解压后权限过大风险，建议解压zip包前将环境umask设置为077，并只在用户HOME目录下解压、使用工具，并仅供本用户自己使用。以上2种安装方式请同样注意工具目录的权限风险。

确认目录和文件的属主及权限是否符合用户所在的组织的安全要求等。另外，请注意，除用户本人以及管理用户外的其他用户，不应拥有安装目录的上级目录的写权限，find {安装目录} -ls
# 操作指导:源码方式

## 下载功能

支持windows或linux系统使用下载功能。运行前请确认使用的离线安装目录属于用户自己所有，且目录的权限和属组需要符合所在组织的安全要求。

### 下载须知

- 如需配置代理、通过修改配置文件的方式调整为下载所需OS的组件（windows场景）等，可编辑“downloader/config.ini”文件，具体可参考<a href="#config">配置说明</a>。
- 由于需要安装大量开源软件，离线安装工具下载的开源软件均来自操作系统源，开源软件的漏洞和修复需要用户自行根据情况修复，强烈建议使用官方源并定期更新。具体可参考<a href="#sourceconfig">源配置</a>。
- 下载好的软件会自动存放于resources目录下。
- 安装过程中会创建docker用户组并启动docker服务。安装完成后，建议卸载系统中可能存在安全风险的gcc、g++、cpp、jdk等第三方组件。

### 下载操作

- windows

  1. windows环境需安装python3，推荐使用python3.7版本以上。
     下载链接：[python3.7.5](https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe)，请根据界面提示完成安装。
     注意安装时在“Advanced Options"界面勾选” Add Python to environment variables"，否则需手动添加环境变量。

  2. 启动下载。
     设置“downloader/config.ini”的os_list或software配置项，运行start_download.bat；或直接运行start_download_ui.bat（推荐使用，可在弹出的简易UI界面上勾选需要下载的OS或PKG相关组件）。

- linux

  1. 执行`./start_download.sh --os-list=<OS1>,<OS2> --download=<PK1>,<PK2>==<Version>`启动下载，具体可参考<a href="#download_parameter">下载参数说明</a>。以下调用`**.sh`脚本采用`./**.sh`的方式，也可使用`bash **.sh`调用，请根据实际使用，建议下载前将环境umask设置为077。
  2. 执行下载时会先检查环境上是否存在python3，如果python3不存在时，分2种：如果当前用户是root用户，本工具会通过apt、yum等工具自动下载python3；如果当前用户是非root用户，本工具会提示用户自行安装python3。
## 安装功能

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

- install_path参数指定CANN软件包的安装路径，root用户安装时该参数有效（且环境上未安装CANN软件包，即没有`/etc/Ascend/ascend_cann_install.info`文件，否则会安装到该文件内容指定的路径），非root用户安装时该参数无效（只能安装到默认路径~/Ascend）；install_path参数不指定驱动包和边缘组件(atlasedge和ha)的安装路径，驱动包只能安装到默认路径/usr/local/Ascend，边缘组件(atlasedge和ha)只能安装到默认路径/usr/local。
- install_path参数指定Toolbox软件包的安装路径，root用户安装时该参数有效（且环境上未安装Toolbox软件包，即没有`/etc/Ascend/ascend_cann_install.info`和`/etc/Ascend/ascend_toolbox_install.info`文件，否则会安装到该文件内容指定的路径），非root用户安装时该参数无效（只能安装到默认路径~/Ascend）。
- 离线工具为zip包时，用户需确认离线工具的解压目录为新解压，并且目录权限为700，没有软链接。
- 安装完成后需修改配置，建议取消root用户的登录。
- 驱动包会使用HwHiAiUser用户和用户组作为软件包默认运行用户，用户需自行创建，并保证该创建用户的密码、密码有效期以及后续使用中的安全问题。创建用户组和用户的命令如下：

```bash
#添加HwHiAiUser用户组
groupadd HwHiAiUser

#添加HwHiAiUser用户,并加入HwHiAiUser用户组
#设置HwHiAiUser的HOME目录为/home/HwHiAiUser
#并设置用户的shell为/bin/bash
useradd -g HwHiAiUser -d /home/HwHiAiUser -m HwHiAiUser -s /bin/bash
```

- 安装2.0.2版本的边缘组件(atlasedge和ha)时，可能需限制HwHiAiUser用户为不可登录状态。但安装驱动包时，需将HwHiAiUser用户设置为可登录状态。请根据具体场景设置。
```bash
usermod -s /sbin/nologin HwHiAiUser   # 安装2.0.2版本的边缘组件(atlasedge和ha)时
usermod -s /bin/bash HwHiAiUser   # 安装驱动时
```

- 安装2.0.3及以后版本的边缘组件(atlasedge)时，该组件会默认创建一个MindXEdge用户。

- 安装2.0.4版本的边缘组件时，需提前安装haveged，例如Ubuntu系统使用`apt install haveged`命令进行安装，安装后需执行`systemctl enable haveged`和`systemctl start haveged`启动haveged服务。

- 若用户需自行指定运行用户和用户组，可在创建用户和用户组后自行修改inventory_file文件。文件内容如下：

```
[ascend:vars]
user=HwHiAiUser
group=HwHiAiUser
```

- 非root用户支持安装的软件列表

| 软件名                 | 说明                                  |
|:---------------------- |:------------------------------------- |
| python、gcc         | python3.7.5和gcc7.3.0，安装在$HOME/.local/目录下  |
| python框架             | tensorflow、pytorch、mindspore           |
| CANN                   | toolbox、nnae、nnrt、tfplugin、toolkit、kernels，默认安装在$HOME目录下，不支持指定路径安装 |
| MindStudio             | 安装在$HOME/目录下  |

注意：
  1. 非root用户需要root用户安装系统组件和driver后才可以安装以上组件。
  2. gcc7.3.0安装后需要建立软链接才能使用,例如root安装的gcc7.3.0执行命令`ln -sf /usr/local/gcc7.3.0/bin/gcc /usr/bin/gcc`。
  3. kernels的安装需要先安装nnae或toolkit，安装kernels需指定--kernels_type参数。
  4. 非root用户需要加入driver安装的属组，才可以正常安装和使用nnrt和toolkit组件，driver默认安装的属组为HwHiAiUser。修改用户组命令如下：

```bash
usermod -a -G HwHiAiUser 非root用户名
```

### 准备软件包

1. 根据实际需要准备待安装软件包（支持驱动、固件、CANN软件包的安装），将待安装软件包放置于resources目录下，参考如下：
   - 驱动和固件：[获取链接](https://ascend.huawei.com/#/hardware/firmware-drivers)
   - CANN软件包：[获取链接](https://ascend.huawei.com/#/software/cann)
2. 软件包仅支持zip包格式，安装时resources目录下只应存在一个版本的软件包，否则可能会有版本不配套的情况。如果resources目录下没有软件包，工具会跳过安装。
3. 支持Atlas 500和Atlas 500Pro批量安装IEF Agent，参考usermanual-ief文档准备IEF产品证书、注册工具、安装工具，放置于resources目录下；
   - IEF相关证书和工具：[参考链接](https://support.huaweicloud.com/usermanual-ief/ief_01_0100.html)
   - Atlas 500已预置了注册工具和安装工具，所以只需准备产品证书放置于resources目录下；而Atlas 500Pro对这3个证书和工具都需要
   - Atlas 500只支持自带的EulerOS2.8 aarch64裁剪版操作系统，不支持其他系统，因此也不支持离线部署工具本地运行，只支持远程安装，也不支持非root安装；Atlas 500Pro支持本地和远程安装
   - 依赖边缘节点atlasedge中间件正常工作，Atlas 500自带atlasedge中间件，Atlas 500Pro需要先安装atlasedge中间件
   - 依赖IEF服务器正常工作，且边缘设备与IEF之间网络正常，边缘节点是否成功纳管需到IEF的web前端观察，其他限制请参考usermanual-ief文档
4. docker镜像文件需用户登录ascendhub，拉取镜像后将镜像转存至resources/docker_images目录下（需自行创建该目录），方可进行docker镜像的安装；docker镜像文件命名格式参考ubuntu_18.04_{x86_64 | aarch64}.tar，大括号内为系统架构，仅支持括号内的两种架构。docker镜像的安装会先安装系统包，所以安装docker镜像前先下载对应的系统包；用户需要确保要安装的docker镜像的安全性。

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

   编辑inventory_file文件，默认如下：

   ```
   [ascend]
   localhost ansible_connection='local'
   ```

2. 执行安装脚本，可根据需要选择安装方式（指定组件安装或指定场景安装）。注意，如果需要其他用户能够使用root用户随后安装的python等，请提前设置umask为022，设置前确认该umask权限符合所在组织的安全要求。

    - 2.1. 指定组件安装

    执行命令`./install.sh --install=<package_name_1>,<package_name_2>`，示例如下。

    ```
    ./install.sh --help     # 查看帮助信息
    ./install.sh --install=sys_pkg,python,npu     # 安装系统依赖、python3.7.5、driver和firmware
    ```

    注意事项：

       - 请按照“sys_pkg>python3.7.5>npu(driver、firmware)>CANN软件包(toolkit、nnrt等)>AI框架(pytorch、tensorflow、mindspore)”顺序进行安装。安装时resources目录下的CANN包版本需和npu配套。
       - 安装driver或firmware后，可能需执行“reboot”重启设备使驱动和固件生效。
       - 部分组件存在运行时依赖，如pytorch需要toolkit或nnae提供运行时依赖，tensorflow 调用npu资源需要tfplugin + toolkit或nnae提供运行时依赖，mindspore需要driver和toolkit提供运行时的依赖。
       - 所有python库的安装都必须先安装python3.7.5，如pytorch、tensorflow、mindspore等。
       - 安装时运行环境时间需要通过date -s命令校准到正确的UTC时间。

    - 2.2 指定场景安装（建议非专业用户使用这种方式）

    执行命令`./install.sh --install-scene=<scene_name>`，示例如下。
    ```
    ./install.sh --install-scene=auto     # 自动安装所有能找到的软件包
    ```
    本工具提供几个基本安装场景，具体可参考<a href="#scene">安装场景介绍</a>。

3. 安装后检查

    执行命令`./install.sh --test=<target>`，示例如下。
    ```
    ./install.sh --test=driver     # 测试driver是否正常`
    ```

### 批量安装

1. 基于密钥认证的ssh连接，安装前请确认系统中未安装paramiko（ansible在某些情况下会使用paramiko，其配置不当容易引起安全问题）。

   配置待安装的其他设备的ip地址，编辑inventory_file文件，格式如下：

   ```
   [ascend]
   ip_address_1 ansible_ssh_user='root'      # root用户
   ip_address_2 ansible_ssh_user='root'
   ip_address_3 ansible_ssh_user='username'  # 非root用户
   ```

   设置密钥认证的参考操作如下，请注意ssh密钥和密钥密码在使用和保管过程中的风险，特别是密钥未加密时的风险，用户应按照所在组织的安全策略进行相关配置，包括并不局限于软件版本、口令复杂度要求、安全配置（协议、加密套件、密钥长度等，特别是/etc/ssh下和~/.ssh下的配置）：
   ```bash
   ssh-keygen -t rsa -b 3072   # 登录管理节点并生成SSH Key。安全起见，建议用户到"Enter passphrase"步骤时输入密钥密码，且符合密码复杂度要求。建议执行这条命令前先将umask设置为0077，执行完后再恢复原来umask值。
   ssh-copy-id -i ~/.ssh/id_rsa.pub <user>@<ip>   # 将管理节点的公钥拷贝到所有节点的机器上，<user>@<ip>替换成要拷贝到的对应节点的账户和ip。
   ssh <user>@<ip>   # 验证是否可以登录远程节点，<user>@<ip>替换成要登录的对应节点的账户和ip。验证登录OK后执行`exit`命令退出该ssh连接。
   ```

   注意事项: 请用户注意ssh密钥和密钥密码在使用和保管过程中的风险。

2. 设置ssh代理管理ssh密钥，避免工具批量安装操作过程中输入密钥密码。设置ssh代理的参考操作如下：
   ```bash
   ssh-agent bash   # 开启ssh-agent的bash进程
   ssh-add ~/.ssh/id_rsa         # 向ssh-agent添加私钥
   ```

3. 执行`./install.sh --check`测试待安装设备连通性。确保所有设备都能正常连接，若存在设备连接失败情况，请检查该设备的网络连接和sshd服务是否开启。
4. 后续操作同上述的单机安装第2、3步骤。
5. 工具的批量安装操作完成后，及时退出ssh代理进程，避免安全风险。
   ```bash
   exit   # 退出ssh-agent的bash进程
   ```

# <a name="pip_manual">操作指导:pip方式</a>

当本工具使用pip安装时，将提供2个入口方便操作

- ascend-download     下载器
- ascend-deployer     部署器

2个入口对root和非root用户均可用

## 下载

```bash
ascend-download --os-list=<OS1>,<OS2> --download=<PK1>,<PK2>==<Version>
```

Win 10和Linux均可执行

- 所有资源下载至ascend-deployer/resources

- windows下在执行命令的当前目录生成ascend-deployer目录。下载完成后将
  整个目录拷贝至待部署linux服务器即可使用。

- linux下将在用户HOME目录下生成ascend-deployer目录，可通过设置环境变量ASCEND_DEPLOYER_HOME替换用户HOME目录，非root用户须保证该目录存在且能正常读写。

## 安装

```bash
ascend-deployer --install=<pkg1,pkg2>
```

ascend-deployer本质上是install.sh的一个wrapper，使用方法与直接执行ascend-deployer目录中的install.sh完全相同。ascend-deployer命令将自动寻找用户HOME目录下的ascend-deployer/install.sh文件执行，可通过设置环境变量ASCEND_DEPLOYER_HOME替换用户HOME目录，非root用户须保证该目录存在且能正常读写。

# <a name="set_env_var">配置环境变量</a>

离线部署工具可以安装python3.7.5，为不影响系统自带python(python2.x or python3.x)， 在使用python3.7.5之前，需配置如下环境变量。

```
export PATH=/usr/local/python3.7.5/bin:$PATH                         # root
export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH   # root

export PATH=~/.local/python3.7.5/bin:$PATH                           # non-root
export LD_LIBRARY_PATH=~/.local/python3.7.5/lib:$LD_LIBRARY_PATH     # non-root
```
本工具执行安装操作时会自动在本机安装python3.7.5，并把以上环境变量内容写进/usr/local/ascendrc文件内，执行如下命令便可轻松设置python3.7.5的环境变量。
```
source /usr/local/ascendrc     # root
source ~/.local/ascendrc       # non-root
```

同样，离线部署工具安装的其他软件包或工具，需用户参考相应的官方资料后配置环境变量或进行其他设置后，方可正常使用。

# 后续任务

- 推理场景

  开发者如果需要开发应用程序，请参考相应的官方资料，如《CANN 应用软件开发指南 (C&C++)》或《CANN 应用软件开发指南 (Python)》。

- 训练场景

  若需进行网络模型移植和训练，请参考相应的官方资料，如《TensorFlow网络模型移植&训练指南》或《PyTorch网络模型移植&训练指南》。

- 删除工具

  本工具属于安装部署类工具，系统安装完成后应立即删除以释放磁盘空间。

| 应删除的                       | 说明                                 |
|:-------------------------------|:-------------------------------------|
| ascend-deployer                | 控制机上的离线部署工具的目录            |
|`pip3 uninstall ascend-deployer`| 控制机上pip安装的工具，可用命令卸载     |
| ~/ansible                      | 控制机和远程机器，自定义信息收集配置文件 |
| `~/resources和~/resources.tar` | 控制机和远程机器，resource资源目录      |
| ~/build                        | 控制机和远程机器，源码包的解压目录      |

# 参考信息

## <a name="parameter">安装参数说明</a>

用户根据实际需要选择对应参数完成安装，命令为`./install.sh [options]`。
参数说明请参见下表，表中各参数的可选参数范围可通过执行`./install.sh --help`查看。

| 参数                                | 说明                                                   |
|:--------------------------------- | ---------------------------------------------------- |
| --help  -h                        | 查询帮助信息。                                              |
| --check                           | 检查环境，确保控制机安装好python3.7.5、ansible等组件，并检查与待安装设备的连通性。   |
| --clean                           | 清理待安装设备用户家目录下的resources目录。                           |
| --nocopy                          | 在批量安装时不进行资源拷贝。                                       |
| --force_upgrade_npu               | 当不是所有卡异常时，可以强制升级NPU                                |
| --tensorflow_version              | 指定安装tensorflow的版本，可以为1.15.0或2.6.5，默认为1.15.0  |
| --kernels_type                    | 指定算子包类型，只能是nnae或toolkit，默认为nnae
| --verbose                         | 打印详细信息                                                    |
| --output-file=<output_file>       | 重定向命令执行的输出结果到指定文件。                                   |
| --stdout_callback=<callback_name> | 设置命令执行的输出格式，可用的参数通过"ansible-doc -t callback -l"命令查看。 |
| --install=<package_name>          | 指定软件安装。若指定“--install=npu”，将会安装driver和firmware。       |
| --install-scene=<scene_name>      | 指定场景安装。安装场景请参见<a href="#scene">安装场景介绍</a>。        |
| --patch=<package_name>            | 指定软件打补丁                                                       |
| --patch-rollback=<package_name>   | 指定软件的补丁回退                                                   |
| --test=<target>                   | 检查指定组件能否正常工作。                                            |

## <a name="download_parameter">下载参数说明</a>

| 参数                  | 说明                      |
|:------------------- | ----------------------- |
| `--os-list=<OS1>,<OS2>` | 指定下载的特定操作系统的相关依赖软件      |
| `--download=<PK1>,<PK2>==<Version>`| 指定下载可选的组件。例如MindSpore、MindStudio、CANN |

本工具默认下载python组件包。当--os-list指定的系统中只有aarch64架构时，只下载aarch64架构系统所需的python组件包；当--os-list指定的系统中只有x86_64架构时，只下载x86_64架构系统所需的python组件包；当--os-list为空或指定的系统中aarch64架构和x86_64架构都有时，2种架构系统所需的python组件包都会下载。下载aarch64或x86_64架构的CANN包逻辑同上。

| 可选的组件      | 配套版本1  | 配套版本2  | 配套版本3 | 配套版本4 | 配套版本5 | 配套版本6 |
|:-------------- | --------  | --------  | --------  | -------- | --------- | -------- |
| MindStudio     |  2.0.0    |  3.0.2    |  3.0.3   |   3.0.4   |  5.0.RC1 | 5.0.RC2   |
| MindSpore      |  1.1.1    |  1.3.0    |  1.5.0   |   1.6.2   |  1.7.0   | 1.8.0     |
| CANN           |  20.3.0   |  5.0.2.1  |  5.0.3.1 | 5.0.4   |  5.1.RC1.1 | 5.1.RC2   | 

安装时resources目录下只应存在一个版本且跟CANN包版本配套的MindSpore或MindStudio，配套关系如上；`./start_download.sh --download=<PK1>,<PK2>==<Version>`，当`<Version>`为空时，会下载最新版本的`<PK>`；`--download=MindSpore`时，--os-list需指定对应的OS，OS及相关配套说明详见[Mindspore官网](https://mindspore.cn/versions)；MindStudio的下载安装请参考[下载安装MindStudio](https://gitee.com/ascend/ascend-deployer/blob/master/docs/Install_MindStudio.md)；CANN的下载请参考[下载CANN](https://gitee.com/ascend/ascend-deployer/blob/master/docs/Download_CANN.md)

## <a name="scene">安装场景介绍</a>

离线部署工具提供几个基本安装场景。如果系统的gcc版本低于7.3.0，安装框架前需要安装gcc以确保各场景安装后可正常使用。gcc7.3.0安装后需要建立软链接才能使用(/usr/bin/gcc指向安装的gcc7.3.0的可执行文件),例如root安装的gcc7.3.0执行命令`ln -sf /usr/local/gcc7.3.0/bin/gcc /usr/bin/gcc`。

| 安装场景     | 安装的组件                                                        | 说明            |
| ---------   | ---------------------------------------------------------------- | ----------------|
| auto        | all                                                              | 安装所有能找到的软件包 |
| vmhost      | sys_pkg、npu、toolbox                                            | 虚拟机场景             |
| edge        | sys_pkg、atlasedge、ha                                           | 安装MindX中间件、HA    |
| offline_dev | sys_pkg、python、npu、toolkit                                  | 离线开发场景          |
| offline_run | sys_pkg、python、npu、nnrt                                     | 离线运行场景          |
| mindspore   | sys_pkg、python、npu、toolkit、mindspore                       | mindspore场景         |
| tensorflow_dev | sys_pkg、python、npu、toolkit、tfplugin、tensorflow         | tensorflow开发场景    |
| tensorflow_run | sys_pkg、python、npu、nnae、tfplugin、tensorflow            | tensorflow运行场景    |
| pytorch_dev | sys_pkg、python、npu、toolkit、pytorch                         | pytorch开发场景       |
| pytorch_run | sys_pkg、python、npu、nnae、pytorch                            | pytorch运行场景       |

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

## <a name="patch">安装、回退CANN补丁包</a>
ascend-deployer工具支持CANN冷补丁的安装和回退。
1. CANN补丁包不支持使用ascend-deployer工具在线下载，用户需自行获取到所需CANN补丁包后，放置于ascend-deployer/resources/patch(如不存在patch目录用户请自行创建)目录下，注意在安装前删除ascend-deployer/resources目录下补丁包对应的CANN软件包。
2. 安装、回退CANN冷补丁的执行命令参考如下：
   - 安装CANN冷补丁（以nnae、tfplugin包为例）：`./install.sh --patch=nnae,tfplugin`
   - 回退CANN冷补丁（以nnae、tfplugin包为例）：`./install.sh --patch-rollback=nnae,tfplugin`
3. 关于CANN冷补丁的相关约束如下：
   - 补丁仅能支持对应的基线版本或相关的补丁版本进行升级。
   - 基于同一基线版本的补丁，需保证后续安装的补丁版本大于之前安装的补丁版本。
   - 仅支持回退一次补丁版本。回退时需将安装补丁时的补丁包放置于ascend-deployer/resources/patch(如不存在patch目录用户请自行创建)目录下，注意在回退前删除ascend-deployer/resources目录下补丁包对应的CANN软件包。
## <a name="config">配置说明</a>

### <a name="proxy_configuration">代理配置</a>

如需使用代理，需在环境变量中配置代理，用户需要注意代理的安全性。本工具默认校验https证书，如果下载过程中出现证书错误，可能是代理服务器有证书替换的安全机制，则需要先安装代理服务器证书。

1. Linux环境变量中配置代理，参考如下
   
   ```
   # 配置环境变量
   export http_proxy="http://user:password@proxyserverip:port"
   export https_proxy="http://user:password@proxyserverip:port"
   ```
   
   其中user为用户在内部网络中的用户名，password为用户密码（特殊字符需转义），proxyserverip为代理服务器的ip地址，port为端口。windows环境变量中配置代理的原理同Linux，具体操作请参考官方说明。

2. 在downloader/config.ini文件中配置是否进行证书校验，内容如下：
   
   ```
   [proxy]
   verify=true         # 是否校验https证书。如果关闭，请用户注意安全风险。
   ```

### windows下载参数说明

在downloader/config.ini文件中可进行windows下载行为配置，将其调整为下载所需组件（不建议直接修改配置文件，建议运行start_download_ui.bat使用UI界面勾选所需组件）。

```
[download]
os_list=CentOS_7.6_aarch64, CentOS_7.6_x86_64, CentOS_8.2_aarch64, CentOS_8.2_x86_64, Ubuntu_18.04_aarch64, Ubuntu_18.04_x86_64, ...          # 待安装部署的环境OS信息
[software]
pkg_list=CANN_5.0.3.1,MindStudio_3.0.3  # 待部署的CANN或MindStudio
```

### <a name="sourceconfig">源配置</a>

离线安装工具已提供源配置文件，用户可根据实际进行替换。

1. Python源配置。在downloader/config.ini文件中配置python源，默认使用华为源。

```
[pypi]
index_url=https://repo.huaweicloud.com/repository/pypi/simple
```

2. 系统源配置。系统源配置文件downloader/config/*{os}\__{version}\__{arch}*/source.*xxx*。以CentOS 7.6 aarch64为例，源配置文件downloader/config/CentOS_7.6_aarch64/source.repo内容如下。这表明同时启用base源和epel源，下载系统组件时会从这两个源中查询和下载。默认使用华为源，可根据业务需求和安装需求修改，以保证其源符合所在组织的安全/漏洞修补要求。若修改，请选择安全可靠的源，并测试下载和安装行为是否正常，否则可能造成组件下载不完整或安装异常。若删除源，可能造成组件下载不完整。

```
[base]
baseurl=https://mirrors.huaweicloud.com/centos-altarch/7/os/aarch64

[epel]
baseurl=https://mirrors.huaweicloud.com/epel/7/aarch64
```

3. 下载类Centos的系统组件时需解析系统源内的xml文件，建议在系统python3中安装defusedxml安全组件，以提升应对潜在的XML漏洞攻击的安全能力。


## <a name="url">公网URL</a>
```
https://cmake.org
https://github.com
https://gcc.gnu.org
http://mirrors.bclinux.org
https://archive.kylinos.cn
https://support.huawei.com
https://mirrors.tencent.com
https://mirrors.bfsu.edu.cn
https://repo.huaweicloud.com
https://uniportal.huawei.com
https://mirrors.huaweicloud.com
https://cache-redirector.jetbrains.com
https://obs-9be7.obs.myhuaweicloud.com
https://obs-9be7.obs.cn-east-2.myhuaweicloud.com
https://ms-release.obs.cn-north-4.myhuaweicloud.com
```
## <a name='sha256sum'>sha256sum校验</a>
| sha256sum                                                        | 离线安装版本                    |
| ---------------------------------------------------------------- | ------------------------------ |
| 22f7e10677658e7c3d223b32f73786c765e85cf6f66440bf620c3e4275f11e7f | ascend-deployer-2.0.4.B093.zip | 

## <a name="faq">FAQ</a>

1. Q: 首次执行`./install.sh --check`或其他安装命令时，会自动安装系统依赖和python3.7.5，如果人为异常中断安装过程，再次执行命令时则可能出现rpm、dpkg工具被锁或python3.7.5功能缺失的情况。

- A: 释放rpm、dpkg工具锁，删除python3.7.5安装目录（python3.7.5安装目录可参考<a href="#set_env_var">配置环境变量</a>），重新使用工具安装。

2. Q: 非root用户安装5.0.1版本以前的toolkit时提示输入sudo密码。

- A: 安全原因，本工具不要求非root用户拥有sudo权限，所以不支持非root用户安装5.0.1版本以前的toolkit。

3. Q: 工具crl文件更新和签名校验的机制是什么样的？是否具备独立的crl文件更新的能力？

- A: crl文件更新和签名校验有两种方式，优先使用toolbox/latest/Ascend-DMI/bin/ascend-cert工具，如果环境上不存在该工具，则使用openssl开源工具。为兼容新旧软件包的签名格式，本工具会使用2套证书。本工具会比较安装包内的crl文件和系统本地的crl文件的生效时间，并使用最新的crl文件校验证书是否被吊销。对root用户，系统本地的crl文件为`/etc/hwsipcrl/ascendsip.crl(或ascendsip_g2.crl)`，对非root用户，该文件为`~/.local/hwsipcrl/ascendsip.crl(或ascendsip_g2.crl)`。如果系统本地的crl文件不存在或生效时间早于安装包内的crl文件，则系统本地的crl文件会被安装包内的crl文件替换。tools/update_crl.sh文件具备独立的crl文件更新的能力，执行`bash update_crl.sh <crl_file>`命令即可，`<crl_file>`为用户上传的crl文件路径。

4. Q: 下载部分组件时出现"certificate verify failed"等字样是什么原因？

- A: 下载时本工具默认校验https证书，上述报错可能是代理服务器证书异常，请联系系统管理员处理。该校验功能在downloader/config.ini文件中可配置，具体可参考<a href="#proxy_configuration">代理配置</a>。

5. Q: euler系统作为worker节点时安装tensoflow2.6.5出现“Failed to connect to the host via ssh: Shared connection to XX closed"等字样。
- A: 主机中设置了ssh连接会话超时时间，部署任务的时间超过了设置的ssh连接会话超时时间会导致该错误。修改“/etc/ssh/sshd_config”文件中的“ClientAliveInterval”关键字的值为“1800”（超时时间为30分钟），然后执行`systemctl restart sshd`重启sshd服务。

1. Q: 如果系统安装torch-1.8.1后导入torch出现“ImportError: libblas.so.3: cannot open shared object file: No such file or directory”等字样是什么原因？
- A：系统未安装openblas依赖，导致没有这个库，执行`yum install openblas`安装系统依赖，然后创建软链接。创建方式参考如下（请以具体的库版本为准）：
  - 执行`find / -name libopenblas*so`查找libopenblas-r0.3.9.so文件（具体显示的版本以实际为准）。
  - 执行`ln -s /usr/lib64/libopenblas-r0.3.9.so /usr/lib64/libblas.so.3`和`ln -s /usr/lib64/libopenblas-r0.3.9.so /usr/lib64/liblapack.so.3`创建软链接。
