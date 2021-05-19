# Overview

## Functions

The offline installation tool provides automatic download and one-click installation of the OS components and Python third-party dependencies. It also supports the installation of the driver, firmware, and CANN software packages. The tools directory additionally places the Device IP configuration script, the use method can refer to <a href="#Device_IP">Device IP configuration specification</a>.

## Environment Requirements

### Description of the supported operating system
|    OS    | Version | CPU Architecture |            Installation Type             |
| :------: | :-----: | :--------------: | :--------------------------------------: |
|  CentOS  |   7.6   |     AArch64      | A minimal image is installed by default. |
|  CentOS  |   7.6   |      x86_64      | A minimal image is installed by default. |
|  CentOS  |   8.2   |     AArch64      | A minimal image is installed by default. |
|  CentOS  |   8.2   |      x86_64      | A minimal image is installed by default. |
| EulerOS  | 2.0SP8  |     AArch64      | A minimal image is installed by default. |
| EulerOS  | 2.0SP9  |     AArch64      | A minimal image is installed by default. |
| EulerOS  | 2.0SP9  |      x86_64      | A minimal image is installed by default. |
|  Ubuntu  |  18.04  |     AArch64      | A server image is installed by default. A standard system is installed by SmartKit by default. |
|  Ubuntu  |  18.04  |      x86_64      | A server image is installed by default. A standard system is installed by SmartKit by default. |
|  Debian  |   9.9   |     AArch64      | A server image is installed by default. A standard system is installed by SmartKit by default. |
|  Debian  |   9.9   |      x86_64      | A server image is installed by default. A standard system is installed by SmartKit by default. |
|  Debian  |   10.0   |      x86_64      | A server image is installed by default. A standard system is installed by SmartKit by default. |
| BCLinux |   7.6   |     AArch64      | A minimal image is installed by default. |
| BCLinux |   7.6   |      x86_64      | A minimal image is installed by default. |
| BCLinux |   7.7   |     AArch64      | A minimal image is installed by default. |
|   SLES   |  12.4   |      x86_64      | A minimal image is installed by default. |
|   SLES   |  12.5   |      x86_64      | A minimal image is installed by default. |
|   Linx   |   6     |     AArch64      | A minimal image is installed by default. |
|  Kylin   |V10Tercel|     AArch64      | A minimal image is installed by default. |
|  Kylin   |V10Tercel|      x86_64      | A minimal image is installed by default. |
|   UOS    |   20    |     AArch64      | A minimal image is installed by default. |
|   UOS    |   20    |      x86_64      | A minimal image is installed by default. |
|  Tlinux  |  2.4    |     AArch64      | A server image is installed by default.  |
|  Tlinux  |  2.4    |     x86_64       | A server image is installed by default.  |

### Description of supported hardware configuration
|  Central Inference Hardware  |  Central Training Hardware  |  Intelligent Edge Hardware  |
|:-------------:|:-------------:|:-------------:|
|  A300-3000    |  A300T-9000   |  A500 Pro-3000|
|  A300-3010    |  A800-9000    |               |
|  A300I Pro    |  A800-9010    |               |
|  A800-3000    |               |               |
|  A800-3010    |               |               |

## Precautions

- Basic commands such as **tar**, **cd**, **ls**, **find**, **grep**, **chown**, **chmod**, **unzip** must be installed in the OS. The OpenSSH server is used by Ansible for connections over SSH. When installing the Ubuntu OS, you need to install it.
- The offline installation tool supports only the default environment after the OS image is successfully installed. Do not install or uninstall software after the OS is installed. If some system software has been uninstalled, causing inconsistency with the default system package, you need to manually configure the network and use tools such as apt, yum, and dnf to install and configure the missing software.
- The offline installation tool can install only basic libraries to ensure that TensorFlow and PyTorch can run properly. If you need to run complex inference services or model training, the model code may contain libraries related to specific services. You need to install the libraries by yourself.
- Euleros, SLES, Debian and other systems need to ensure that there are kernel-headers and kernel-devel packages that are consistent with the kernel version of the system (which can be viewed through 'uname -r' command). If not, you need to prepare your own kernel headers.
- When installing the SLES driver, the offline installer will set "allow_unsupported_modules" in /etc/modprob. d/10-unsupported-modules.conf to "1", which means that non-native drivers are allowed to be loaded during system boot.
- By default, the **root** user is not allowed to remotely log in to OSs such as EulerOS. Therefore, you need to set **PermitRootLogin** to **yes** in the **sshd_config** file before remote installation and set it to **no** after the installation.
- Support for Ubuntu 18.04 x86_64 installation of cross-compiled related components and the Aarch64 architecture toolkit package.
- CentOS 7.6 x86_64 with lower version kernel (below 4.5) of ATLAS 300T training card requires CentOS to be upgraded to 8.0 or above or a kernel patch is added. Failure to do so may result in firmware installation failure.Add a kernel patch method please refer to the reference [link] (https://support.huawei.com/enterprise/zh/doc/EDOC1100162133/b56ad5be).
- After the kylin V10 system's dependencies are installed, you need to wait for the system configuration to complete before you can use docker and other commands.
- You need to modify /etc/pam.d/su, delete # before 'auth efficient pam_ rootok.so', so that the root user switch to other users without entering a password when the system is Linx.
- After the default installation of tlinux system, the total space of the root directory is about 20G, and the packages that exceed the available disk space can not be placed in the resources directory to avoid decompression or installation failure.

# Operation Instructions

## Downloading OS Components and Python Third-party Dependencies

The download function can be used in the Windows or Linux OSs.

### Notice

- To configure a proxy or modify the configuration file to download required OS components, edit the **downloader/config.ini** file. For details, see <a href="#config">Configuration Description</a>.
- The offline installation tool provides the source configuration file. The Huawei source is used by default. Replace it as required. For details, see <a href="#sourceconfig">Source Configuration</a>.
- The downloaded software is automatically stored in the **resources** directory.
- After the installation, it is recommended to uninstall the third-party components such as GCC and G + + that may have security risks in the system.

### Download

- Windows
  1. Python 3 is required in Windows. Python 3.7 or later is recommended.
     Download link: [python3.7.5](https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe)
     Complete the installation as prompted. During the installation, select **Add Python to environment variables** on the **Advanced Options** page. Otherwise, you need to manually add environment variables.
  2. Start download.
     Run **start_download_ui.bat** (recommended because it allows you to select the Related components of OS or PKG to be downloaded on the displayed UI) or **start_download.bat**.
- Linux
  1. Run the `./start_download.sh --os-list=<OS1>,<OS2> --download=<PK1>,<PK2>==<Version>` command to start download. The following call ` * * sh ` script using `. / * * sh ` way, also can use ` bash * * sh ` calls, please according to actual use.
  2. Support root and non-root users to perform download operations, Non-root users do not need sudo permissions, but do need to have executable permissions for the tool directory; The presence of Python 3 on the environment is checked when the download is performed. If python3 does not exist, it can be divided into two types: if the current user is root, the tool will automatically download python3 through APT, YUM and other tools;If the current user is not root, the tool prompts the user to install Python3.In both cases, the user is required to ensure that the environment network and source are available;

## Installation

### install options

- install options are in the inventory_file. default options is below:

```bash
[ascend]
localhost ansible_connection='local'

[ascend:vars]
user=HwHiAiUser
group=HwHiAiUser
install_path=/usr/local/Ascend
```

| parameter    | remark                                                |
|:------------ |:----------------------------------------------------- |
| user         | user，will be pass to --install-username options       |
| group        | usergroup，will be pass to --install-usergroup options |
| install_path | install path，will be pass to --install-path options   |

### Notice

- The driver and CANN software packages will user HwHiAiUser and group as default user. The **HwHiAiUser** user must be created first. The commands to create user and group is below:

```bash
#add HwHiAiUser group
groupadd HwHiAiUser

#add HwHiAiUser user add it to HwHiAiUser group
#set /home/HwHiAiUser as HwHiAiUser's HOME directory and create
#set /bin/bash HwHiAiUser's default shell
useradd -g HwHiAiUser -d /home/HwHiAiUser -m HwHiAiUser -s /bin/bash
```

- If you need to specify the running user and user group, modify the **inventory_file** file. The file content is as follows:

```
[ascend:vars]
user=HwHiAiUser
group=HwHiAiUser
```

- A large amount of open source software needs to be installed. The open source software downloaded using the offline installation tool comes from the OS source. You need to fix the vulnerabilities of the open source software as required. You are advised to use the official source to update the software regularly.

### Obtaining Software Packages

1. Prepare the software packages to be installed as required (The driver, firmware, and CANN software packages can be installed). Save the software packages to be installed in the **resources** directory. The following is an example.
   - Driver and firmware: [Link](https://www.huaweicloud.com/intl/en-us/ascend/resource/Software)
   - CANN software package: [Link](https://www.huaweicloud.com/intl/en-us/ascend/cann)
2. ZIP packages and run packages are available in both formats. If the same package in these two formats exists in the resources directory, install the ZIP package first. Only one version of the package should exist in the resources directory at installation time, otherwise there may be version mismatch.
3. Support Atlas 500 and Atlas 500Pro batch installation of IEF Agent, refer to UserManual-IEF documentation to prepare IEF product certificate, registration tools, installation tools, placed in the resources directory;
   - IEF relevant certificates and tools: [Link](https://support.huaweicloud.com/usermanual-ief/ief_01_0031.html)
   - The Atlas 500 comes pre-loaded with registration tools and installation tools, so you just need to prepare the product certificate and place it in the Resources directory.The Atlas 500Pro requires all three certificates and tools
   - Atlas 500 only supports the Euleros 2.8 Aarch64 tailoring operating system, not other systems, so it does not support the offline deployment tool to run locally, only supports remote installation, and also does not support non-root installation. Atlas 500Pro supports both local and remote installations
   - Depending on the edge node AtlasEdge middleware working properly, Atlas 500 comes with AtlasEdge middleware， Atlas 500Pro needs to install AtlasEdge middleware first
   - Depends that the IEF server is working properly and that the network between the edge device and the IEF is working properly. Whether the edge node is successfully managed needs to be observed at the IEF Web front end. Refer to the usermanual-IEF documentation for other restrictions
4. The files of docker image require the user to log in to ascendhub, pull the image, and then transfer it to resources/docker_images directory before docker-images' installation.The file name of docker image is like to ubuntu_18.04_{x86_ 64 | aarch64}.tar, the system architecture is in the brackets, and only the two architectures in the brackets are supported.

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

### Single-Device Installation

1. Configure a stand-alone inventory_file file.
    Edit the **inventory_file** file. The format is shown as follows:

   ```
   [ascend]
   localhost ansible_connection='local' # root user
   ```

    Note: only support root user due to safety reason.

2. Run the installation script and select an installation mode (software-specific installation or scenario-specific installation) as required.

   - Software-specific installation
     `./install.sh --install=<package_name>`
     You can run the `./install.sh --help` command to view the options of <package_name>. Example command:
     `./install.sh --install=npu //Install the driver and firmware.`
     Notes:
     - Installation sequence: driver > firmware > CANN software package (such as the Toolkit and nnrt), or npu > CANN software package.
     - After the driver or firmware is installed, run the `reboot` command to restart the device for the driver and firmware to take effect.
     - Some components require runtime dependencies. For example, PyTorch requires the Toolkit to provide runtime dependencies, TensorFlow and npubridge require TFPlugin to provide runtime dependencies, and mindspore_ascend require driver and toolkit to provide runtime dependencies.
     - All the installation of Python libraries must first install Python 3.7.5, such as python, tensorflow, Mindstore, etc.
     - Mindspore-ascend needs to install the driver and toolkit of its version for normal use. Please refer to the official website of [mindspore](https://mindspore.cn/install) for software supporting instructions。
   - Scenario-specific installation
     `./install.sh --install-scene=<scene_name>`
     The offline installation tool provides several basic installation scenarios. For details, see <a href="#scene">Installation Scenarios</a>. Example command:
      `./install.sh --install-scene=auto     // Automatic installation of all software packages that can be found`

3. After the installation, run the following command to check whether the specified component works properly:
   `./install.sh --test=<target>`
   You can run the `./install.sh --help` command to view the options of <target>. Example command:
   `./install.sh --test=driver // Test whether the driver is normal.`

   ### Batch Installation

4. Configure the IP addresses, user names, and passwords of other devices where the packages to be installed.
    Edit the **inventory_file** file. The format is shown as follows:

   ```
   [ascend]
   ip_address_1 ansible_ssh_user='root' ansible_ssh_pass='password1'
   ip_address_2 ansible_ssh_user='root' ansible_ssh_pass='password2'
   ip_address_3 ansible_ssh_user='root' ansible_ssh_pass='password3'
   ```

    Note:

   - The Inventory file configures the user name and password for the remote device, supporting only root user;  After the configuration is completed, it is necessary to execute commands such as./install.sh --check or install, test to complete the encryption of the file, otherwise the account password may be leaked.

   - For safety, strongly suggest to use ansible-vaule encrypt the inventory_file and then edit it with ansible-edit. for example

     ```bash
     ansible-vault encrypt inventory_file
     ansible_vault edit inventory_file
     ```

   - Set the environment variable ANSIBLE_VAULT_PASSWORD_FILE to specify the Ansibled-Valut password file.For example, if the user sets ANSIBLE_VAULT_PASSWORD_FILE=~/.vault_pass.txt, Ansible will automatically search for passwords in the file to avoid the user interactively entering the Ansible_Valut password;This functionality is provided by ansible and details, please refer to [ansible official document] (https://docs.ansible.com/ansible/latest/user_guide/vault.html).


5. Run the `./install.sh --check` command to test the connectivity of the devices where the packages to be installed.
    Ensure that all devices can be properly connected. If a device fails to be connected, check whether the network connection of the device is normal and whether sshd is enabled.

6. Run the installation script and select an installation mode (software-specific installation or scenario-specific installation) as required.

   - Software-specific installation
     `./install.sh --install=<package_name>`
     You can run the `./install.sh --help` command to view the options of <package_name>. Example command:
     `./install.sh --install=npu //Install the driver and firmware.`
     Notes:
     - Installation sequence: driver > firmware > CANN software package (such as the Toolkit and nnrt), or npu > CANN software package.
     - After the driver or firmware is installed, run the `reboot` command to restart the device for the driver and firmware to take effect.
     - Some components require runtime dependencies. For example, PyTorch requires the Toolkit to provide runtime dependencies, and TensorFlow and npubridge require TFPlugin to provide runtime dependencies.
   - Scenario-specific installation
     `./install.sh --install-scene=<scene_name>`
     The offline installation tool provides several basic installation scenarios. For details, see <a href="#scene">Installation Scenarios</a>. Example command:
      `./install.sh --install-scene=auto     // Automatic installation of all software packages that can be found`

7. After the installation, run the following command to check whether the specified component works properly:
   `./install.sh --test=<target>`
   You can run the `./install.sh --help` command to view the options of <target>. Example command:
   `./install.sh --test=driver // Test whether the driver is normal.`

# Environment Variable Configuration

The offline deployment tool can install Python 3.7.5, To ensure that the built-in Python (Python 2.x or Python 3.x) is not affected, you need to configure the following environment variables before using Python 3.7.5:

```
export PATH=/usr/local/python3.7.5/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH
```
This tool will automatically install the Python 3.7.5 environment variable in /usr/local/ascendrc file. You can easily set the Python 3.7.5 environment variable by following the following command
```
source /usr/local/ascendrc
```

Similarly, other software packages or tools installed by offline deployment tools can be used normally only after users refer to the corresponding official information and configure environment variables or make other Settings.

# Follow-up

- Inference scenario
  You can develop applications in the development environment by referring to the [CANN Application Software Development Guide (C and C++)](https://www.huaweicloud.com/intl/en-us/ascend/cann) or [CANN Application Software Development Guide (Python)](https://www.huaweicloud.com/intl/en-us/ascend/cann).
- Training scenario
  For details about network model porting and training, see the [TensorFlow Network Model Porting and Training Guide](https://www.huaweicloud.com/intl/en-us/ascend/pytorch-tensorflow) or [PyTorch Network Model Porting and Training Guide](https://www.huaweicloud.com/intl/en-us/ascend/pytorch-tensorflow).
- Delete this tool
  This tool is only used for deployment. When installation completed, it should be deleted for free the disk space.

# Upgrade

Run the following command to upgrade the specified software:
`./install.sh --upgrade=<package_name>`
You can run the `./install.sh --help` command to view the options of <package_name>. Example command:
`./install.sh --upgrade=npu // Upgrade the driver and firmware.`
Notes:

- Upgrade sequence: firmware > driver > CANN software package (such as the Toolkit and nnrt), or npu > CANN software package.
- After the driver or firmware is upgraded, run the `reboot` command to restart the device for the driver and firmware to take effect.

# Uninstallation

Run the following command to uninstall the specified software:
`./install.sh --uninstall=<package_name>`
You can run the `./install.sh --help` command to view the options of <package_name>. Example command:
`./install.sh --uninstall=npu     // Uninstall the driver and firmware`
Note:
Uninstallation sequence: CANN software package (such as the Toolkit and nnrt) > driver and firmware (no requirement on the uninstallation sequence of the driver and firmware).

# Offline Installation Tool Upgrade

You can perform the following operation to upgrade the offline installation tool:

- Windows
  Run **upgrade_self.bat** to start the upgrade.
- Linux
  Run the `./upgrade_self.sh` command to start the upgrade.

# Reference Information

## <a name="parameter">Install Parameter Description</a>

Select corresponding parameters to install, upgrade, or uninstall the software. The command format is as follows:
`./install.sh [options]`
The following table describes the parameters. You can run the `./install.sh --help` command to view the options of the following parameters.

| Parameter                         | Description                                                                                                                                                                    |
|:--------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| --help  -h                        | Queries help information.                                                                                                                                                      |
| --check                           | Check the environment to ensure that the control machine has installed Python 3.7.5, Ansible and other components, and check the connectivity with the device to be installed. |
| --clean                           | Clean the Resources directory under the user's home directory for the device to be installed.                                                                                  |
| --nocopy                          | Forbids resources copying during batch installation.                                                                                                                           |
| --debug                           | Performs debugging.                                                                                                                                                            |
| --output-file=<output_file>       | Set the output format of the command execution. The available parameters can be viewed with the command "ansible -doc-t callback-l".                                           |
| --stdout_callback=<callback_name> | Performs debugging.                                                                                                                                                            |
| --install=<package_name>          | Specifies the software to be installed. If **--install=npu** is specified, the driver and firmware are installed.                                                              |
| --install-scene=<scene_name>      | Specifies the scenario for installation. For details about the installation scenarios, see <a href="#scene">Installation Scenarios</a>.                                        |
| --uninstall=<package_name>        | Uninstalls the specified software. If **--uninstall=npu** is specified, the driver and firmware will be uninstalled.                                                           |
| --upgrade=<package_name>          | Upgrades the specified software. If **--upgrade=npu** is specified, the driver and firmware will be upgraded.                                                                  |
| --test=<target>                   | Checks whether the specified component works properly.                                                                                                                         |
| --display=<target>                | Displays installed packages                                                                 |

## <a name="parameter">Download Parameter Description</a>

| Parameter           | Description                                    |
|:------------------- | ---------------------------------------------- |
| `--os-list=<OS1>,<OS2>`| set specific os softwares to download          |
| `--download=<PK1>,<PK2>==<Version>`| download specific software. such as 如MindStudio、CANN |

Currently MindStudio supports 2.0.0 and 3.0.1 versions, and Cann supports 20.2.rc1 and 5.0.1 versions. Only one version of the MindStudio or Cann package should exist in the resources directory at the time of installation, otherwise there may be versions that do not match. `./start_download.sh --download=<PK1>,<PK2>==<Version>`, when `<Version>` is missing, `<PK>` is the latest. MindStudio installation please refer to the [install MindStudio](https://gitee.com/ascend/ascend-deployer/blob/master/docs/Install_MindStudio.md).

## <a name="scene">Installation Scenarios</a>

The offline installation tool provides several basic installation scenarios.

| Installation Scenario | Installed Components                                                          | Description                                            |
| --------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------ |
| auto                  | all                                                                           | All software packages that can be found are installed. |
| infer_dev             | Driver, firmware, nnrt, toolbox, the Toolkit, torch, TFPlugin, and TensorFlow | Inference development scenario.                        |
| infer_run             | Driver, firmware, nnrt, and toolbox                                           | Inference running scenario                             |
| train_dev             | Driver, firmware, nnae、toolbox, the Toolkit, torch, TFPlugin, and TensorFlow  | Training development scenario                          |
| train_run             | Driver, firmware, nnae, toolbox, torch, TFPlugin, and TensorFlow              | Training running scenario                              |
| vmhost                | Driver, firmware, and toolbox                                                 | VM host scenario                                       |
| edge                  | Driver, firmware, atlasedge, ha                                               | Install MindX middleware, HA                           |

The configuration files for the preceding installation scenarios are stored in the **scene** directory. For example, the following shows the configuration file **scene/scene_infer_run.yml** of the inference development scenario:

```
- hosts: '{{ hosts_name }}'

- name: install system dependencies
  import_playbook: ../install/install_sys_pkg.yml

- name: install python3.7.5
  import_playbook: ../install/install_python375.yml

- name: install driver and firmware
  import_playbook: ../install/install_npu.yml

- name: install nnrt
  import_playbook: ../install/install_nnrt.yml

- name: install toolbox
  import_playbook: ../install/install_toolbox.yml

- name: install toolkit
  import_playbook: ../install/install_toolkit.yml

- name: install torch
  import_playbook: ../install/install_torch.yml

- name: install tfplugin
  import_playbook: ../install/install_tfplugin.yml

- name: install tensorflow
  import_playbook: ../install/install_tensorflow.yml
```

To customize an installation scenario, refer to the preceding configuration file.

## <a name="config">Configuration Description</a>

### Proxy Configuration

If you want to use an HTTP proxy, either configure the proxy in an environment variable (recommended) or configure the proxy in the downloader/config.ini file. If a certificate error occurs during the download process, it may be that the proxy server has a security mechanism for certificate replacement, so you need to install the proxy server certificate first.

1. Configure the agent in the environment variable as follows

   ```
   # Configure environment variables.
   export http_proxy="http://user:password@proxyserverip:port"
   export https_proxy="http://user:password@proxyserverip:port"
   ```

   Where "user" is the user's internal network name, "password" is the user's password (special characters need to be escaped), "proxyserverip" is the IP address of the proxyserver, and "port" is the port.

2. Configure the agent in the downloader/config.ini file as follows:

   ```
   [proxy]
   enable=false        # Whether to enable or disable the proxy.
   verify=true         # Whether to verify the HTTPS certificate.
   protocol=https      # The HTTP protocol
   hostname=           # proxy server
   port=               # proxy port
   username=none       # Proxy account
   userpassword=none   # Proxy password
   ```

   You need to change the enable parameter to true, and configure the available hostname, port, username, userpassword.
   For security purposes, if the proxy account and password have been configured in the downloader/config.ini file, you should clear the config.ini after downloading

### Download Configuration

You can configure and modify the download parameters in the **downloader/config.ini** file to download the required OS components.

```
[download]
os_list=CentOS_7.6_aarch64, CentOS_7.6_x86_64, CentOS_8.2_aarch64, CentOS_8.2_x86_64, Ubuntu_18.04_aarch64, Ubuntu_18.04_x86_64 ...          # OS information of the environment to be deployed.
```

### <a name="sourceconfig">Source Configuration</a>

The offline installation tool provides the source configuration file. Replace it as required.

- Python source configuration
  Configure the Python source in the **downloader/config.ini** file.The Huawei source is used by default.

  ```
  [pypi]
  index_url=https://repo.huaweicloud.com/repository/pypi/simple
  ```
- OS source configuration
  OS source configuration file: **downloader/config/*{os}\__{version}\__{arch}*/source.*xxx***
  Using CentOS 7.6 AArch64 as an example, the content of the source configuration file **downloader/config/CentOS_7.6_aarch64/source.repo** is as follows:

  ```
  [base]
  baseurl=https://mirrors.huaweicloud.com/centos-altarch/7/os/aarch64
  ```

[epel]
baseurl=https://mirrors.huaweicloud.com/epel/7/aarch64

```
Indicates that both Base and EPEL sources are enabled from which system components will be queried and downloaded.Huawei source is used by default and can be modified as needed.If you modify, select a safe and reliable source and test whether the download and installation behavior is normal, otherwise it may cause incomplete download of the component or abnormal installation.Deleting the source may result in an incomplete download of the component.

# Other Install Guide

## <a name="Device_IP">Device IP configuration specification</a>
The function of this script is to modify the IP address of NPU board card and realize batch configuration by using the batch deployment capability of Ansible tools. The following contents are only for the reference of users with use scenarios of batch configuration.

### Data preparation
- Server's operating system IP (OS IP) address file.
- The server's operating system user name and password.
- The Device IP address file to be configured.
- Device IP configuration script (deviceip-conf.sh).

### instructions
- Device IP refers to the IP address of the NPU board to be modified.
- Please refer to <a href="#IP format">OS IP address and Device IP address format</a> for the server's operating system IP (OS IP) address file and the Device IP address format to be configured.
- Batch operation does not support mixed device types, that is, the selected device type, the number of NPU standard cards and the configured IP address number, the working mode must be consistent.
- Each server has 2 NPU boards and each NPU board has 4 NPU chips.In SMP mode, four NPU chips on each NPU board need to be configured with IP addresses of four different network segments.

### steps
1. Upload the OS IP address file, the Device IP address file, and the Device IP configuration script to the specified directory of the target host (e.g., /root/ uploadDeviceIP, /root/ uploadDeviceIP, /root/ uploadDeviceIP).
2. Execute the command at the target host specified directory (for example, /root/ uploadDeviceIP)
```

bash deviceip-conf. sh [Device type] [Number of NPU standard cards] [NPU standard card IP configuration] [Working mode] [OS IP address file] [DeviceIP address file]

```
Take 8 non-standard NPU board cards using SMP mode A800-9000 as an example, the command is
```

bash DeviceIP-conf.sh 1 0 0 SMP /root/uploadosip/OS_IP /root/uploaddeviceip/Device_IP

```
|parameter|instructions|selection|    note    |
|:------:|:--:|:-----:|:--------------:|
|Device type|A800-9000 with 8 NPU|1|npu-smi info query number of NPU = 8, enter 1; query number of NPU = 4, enter 2|
|Number of NPU standard cards|Not NPU standard card|0|With the number of NPU standard cards, A800-9000 is set to 0|
|NPU standard card IP configuration|Not NPU standard card|0|With the same IP number of NPU standard card, A800-9000 is set to 0|
|Working mode|SMP|0|According to the actual configuration, SMP(symmetric multiprocessor mode), AMP (asymmetric multiprocessor mode)|

### <a name="IP format">OS IP address and Device IP address format</a>
You need to convert these two files to UNIX format.
1. OS IP address file
- Format 1 (Recommended)
The IP address segment, like this IPx-IPy, ends with a carriage return, for example:
```

10.80.100.101~10.80.100.104

```
- Format 2
List of IP addresses, one by one, with OS IP addresses, ending with Enter, for example:
```

10.80.100.101
10.80.100.102
10.80.100.103
10.80.100.104

```
2. Device IP address file
- Format 1 (Recommended)
IP address segment, similar to the format of IPX-IPY /Netmask/Gateway. In SMP mode, the 4 NPU chips on each NPU board need to be configured with the Device IP addresses of 4 different network segments, ending with Enter, for example:
```

172.168.1.100~172.168.1.107/255.255.255.0/172.168.1.1
172.168.2.100~172.168.2.107/255.255.255.0/172.168.2.1
172.168.3.100~172.168.3.107/255.255.255.0/172.168.3.1
172.168.4.100~172.168.4.107/255.255.255.0/172.168.4.1

```
- Format 2
A list of IP addresses, in a format similar to this IP/Netmask/Gateway, gives the OS IP addresses one by one, ending with a press return, for example:
```

172.168.1.100/255.255.255.0/172.168.1.1
172.168.2.100/255.255.255.0/172.168.2.1
172.168.3.100/255.255.255.0/172.168.3.1
172.168.4.100/255.255.255.0/172.168.4.1

```

```
