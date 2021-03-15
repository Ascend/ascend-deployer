# Overview
## Functions
The offline installation tool provides automatic download and one-click installation of the OS components and Python third-party dependencies. It also supports the installation of the driver, firmware, and CANN software packages. The tools directory contains an additional Device IP configuration script that can be used if needed.
## Environment Requirements
The offline installation tool supports the download and installation of the OSs listed in the following table:
|    OS    | Version | CPU Architecture |            Installation Type             |
| :------: | :-----: | :--------------: | :--------------------------------------: |
|  CentOS  |   7.6   |     AArch64      | A minimal image is installed by default. |
|  CentOS  |   7.6   |      x86_64      | A minimal image is installed by default. |
|  CentOS  |   8.2   |     AArch64      | A minimal image is installed by default. |
|  CentOS  |   8.2   |      x86_64      | A minimal image is installed by default. |
|  Ubuntu  |  18.04  |     AArch64      | A server image is installed by default. A standard system is installed by SmartKit by default. |
|  Ubuntu  |  18.04  |      x86_64      | A server image is installed by default. A standard system is installed by SmartKit by default. |
|  Debian  |   9.9   |     AArch64      | A server image is installed by default. A standard system is installed by SmartKit by default. |
|  Debian  |   9.9   |      x86_64      | A server image is installed by default. A standard system is installed by SmartKit by default. |
| BigCloud |   7.6   |     AArch64      | A minimal image is installed by default. |
| BigCloud |   7.6   |      x86_64      | A minimal image is installed by default. |
| BigCloud |   7.7   |     AArch64      | A minimal image is installed by default. |
|   SLES   |  12.4   |      x86_64      | A minimal image is installed by default. |
|  Kylin   |V10Tercel|     AArch64      | A minimal image is installed by default. |
| EulerOS  | 2.0SP8  |     AArch64      | A minimal image is installed by default. |
| EulerOS  | 2.0SP9  |     AArch64      | A minimal image is installed by default. |
| EulerOS  | 2.0SP9  |      x86_64      | A minimal image is installed by default. |
## Precautions
- Basic commands such as **tar**, **cd**, **ls**, **find**, **grep**, **chown**, **chmod** must be installed in the OS. The OpenSSH server is used by Ansible for connections over SSH. When installing the Ubuntu OS, you need to install it.
- The offline installation tool supports only the default environment after the OS image is successfully installed. Do not install or uninstall software after the OS is installed. If some system software has been uninstalled, causing inconsistency with the default system package, you need to manually configure the network and use tools such as apt, yum, and dnf to install and configure the missing software.
- The offline installation tool can install only basic libraries to ensure that TensorFlow and PyTorch can run properly. If you need to run complex inference services or model training, the model code may contain libraries related to specific services. You need to install the libraries by yourself.
- For EulerOS, ensure that the source has the **kernel-headers** and **kernel-devel** software packages that match the kernel version (you can run the `uname -r` command to view the version). If the software packages do not exist, you need to prepare them.
- When installing CentOS 8.2, select **Standard** in **Additional Software for Selected Environment**. Otherwise, basic commands such as **tar** may be missing after the OS is installed.
- By default, the **root** user is not allowed to remotely log in to OSs such as EulerOS. Therefore, you need to set **PermitRootLogin** to **yes** in the **sshd_config** file before remote installation and set it to **no** after the installation.
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
      Run **start_download_ui.bat** (recommended because it allows you to select the OS components to be downloaded on the displayed UI) or **start_download.bat**.
- Linux
    Run the `./start_download.sh --os-list=<OS1>,<OS2>` command to start download.
## Installation
### Notice
- When the offline installation tool installs the driver and CANN software packages, the **HwHiAiUser** user is created by default as the running user. If you need to specify the running user and user group, modify the **inventory_file** file. The file content is as follows:
    ```
    [ascend:vars]
    user=HwHiAiUser
    group=HwHiAiUser
    ```

- A large amount of open source software needs to be installed. The open source software downloaded using the offline installation tool comes from the OS source. You need to fix the vulnerabilities of the open source software as required. You are advised to use the official source to update the software regularly.

### Obtaining Software Packages

Prepare the software packages to be installed as required. (The driver, firmware, and CANN software packages can be installed.)
    - Driver and firmware: [Link](https://www.huaweicloud.com/intl/en-us/ascend/resource/Software)
    - CANN software package: [Link](https://www.huaweicloud.com/intl/en-us/ascend/cann)
Save the software packages to be installed in the **resources** directory. The following is an example.
ZIP packages and run packages are available in both formats. If the same package in these two formats exists in the resources directory, install the ZIP package first.
Support Atlas 500 and Atlas 500Pro batch installation of IEF Agent, refer to UserManual-IEF documentation to prepare IEF product certificate, registration tools, installation tools, placed in the resources directory;
    - IEF relevant certificates and tools: [Link](https://support.huaweicloud.com/usermanual-ief/ief_01_0031.html)
    - The Atlas 500 comes pre-loaded with registration tools and installation tools, so you just need to prepare the product certificate and place it in the Resources directory.The Atlas 500Pro requires all three certificates and tools
    - Atlas 500 only supports the Euleros2.8 Aarch64 clipped operating system, and does not support other systems. Therefore, it does not support the offline deployment tool to run locally, but only supports remote installation.Atlas 500Pro supports both local and remote installations
    - Depends that the IEF server is working properly and that the network between the edge device and the IEF is working properly. Refer to the usermanual-IEF documentation for other restrictions
The files of docker image require the user to log in to ascendhub, pull the image, and then transfer it to resources/docker_images directory before docker-images' installation.
The file name of docker image is like to ubuntu_18.04_{x86_ 64 | aarch64}.tar, the system architecture is in the brackets, and only the two architectures in the brackets are supported.

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
   |- BigCloud_7.6_aarch64
   |- BigCloud_7.6_x86_64
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
    localhost ansible_connection='local' ansible_become_pass='password' # not root user
    ```
    Note: supporting both root and non-root users;The root user does not need to configure ansible_become_pass parameter, and the non-root user must configure ansible_become_pass parameter, which is the same as the ansible_ssh_pass parameter, and the non-root user must have the sudoer privilege.The offline deployment tool encrypts the Inventory files with passwords using Ansidia-Vault mechanism. ./install.sh --check or install, test and other commands can be executed to complete the encryption of the file after the configuration is completed, otherwise the account password may be leaked;Non-root users using the offline deployment tool need to have access to the ASCEND -Deployer directory.
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
    - Scenario-specific installation
      `./install.sh --install-scene=<scene_name>`
      The offline installation tool provides several basic installation scenarios. For details, see <a href="#scene">Installation Scenarios</a>. Example command:
       `./install.sh --install-scene=auto     // Automatic installation of all software packages that can be found`
3. After the installation, run the following command to check whether the specified component works properly:
  `./install.sh --test=<target>`
  You can run the `./install.sh --help` command to view the options of <target>. Example command:
  `./install.sh --test=driver // Test whether the driver is normal.`
### Batch Installation

1. Configure the IP addresses, user names, and passwords of other devices where the packages to be installed.
    Edit the **inventory_file** file. The format is shown as follows:
    ```
    [ascend]
    ip_address_1 ansible_ssh_user='root' ansible_ssh_pass='password1' # root user
    ip_address_2 ansible_ssh_user='username2' ansible_ssh_pass='password2' ansible_become_pass='password2' # not root user
    ip_address_3 ansible_ssh_user='username3' ansible_ssh_pass='password3' ansible_become_pass='password3' # not root user
    ```
    Note: The Inventory file configures the user name and password of the remote device, supporting both root and non-root users;The root user does not need to configure ansible_become_pass parameter, and the non-root user must configure ansible_become_pass parameter, which is the same as the ansible_ssh_pass parameter, and the non-root user must have the sudoer privilege.The offline deployment tool encrypts the Inventory files with passwords using Ansidia-Vault mechanism. `./install.sh --check` or install, test and other commands can be executed to complete the encryption of the file after the configuration is completed, otherwise the account password may be leaked;Non-root users using the offline deployment tool need to have access to the ASCEND -Deployer directory.
2. Run the **ansible ping** command to test the connectivity of the devices where the packages to be installed.
    ```
    # Configure environment variables.
    export PATH=/usr/local/python3.7.5/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH
    # Test the connectivity of the devices.
    ansible all -i ./inventory_file -m ping # Inventory_file is not encrypted
    ansible all -i ./inventory_file -m ping --ask-vault-pass # Inventory_file is encrypted
    ```
    If Ansible is not installed in the current environment, run the `./install.sh --check` command.
    If inventory_file is encrypted, you need to add the `--ask-vault-pass` parameter to test the connectivity of the device to be installed
    Ensure that all devices can be properly connected. If a device fails to be connected, check whether the network connection of the device is normal and whether sshd is enabled.
3. Run the installation script and select an installation mode (software-specific installation or scenario-specific installation) as required.
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
4. After the installation, run the following command to check whether the specified component works properly:
  `./install.sh --test=<target>`
  You can run the `./install.sh --help` command to view the options of <target>. Example command:
  `./install.sh --test=driver // Test whether the driver is normal.`

# Environment Variable Configuration
During the installation, Python 3.7.5 is automatically installed on the device. To ensure that the built-in Python (Python 2.x or Python 3.x) is not affected, you need to configure the following environment variables before using Python 3.7.5:
```
export PATH=/usr/local/python3.7.5/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH
```
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
## <a name="parameter">Parameter Description</a>
Select corresponding parameters to install, upgrade, or uninstall the software. The command format is as follows:
`./install.sh [options]`
The following table describes the parameters. You can run the `./install.sh --help` command to view the options of the following parameters.

| Parameter                    | Description                              |
| :--------------------------- | ---------------------------------------- |
| --help  -h                   | Queries help information.                |
| --check                      | Check the environment to ensure that the control machine has installed Python 3.7.5, Ansible and other components, and check the connectivity with the device to be installed.                  |
| --clean                      | Clean the Resources directory under the user's home directory for the device to be installed.          |
| --nocopy                     | Forbids resources copying during batch installation. |
| --debug                      | Performs debugging.                      |
| --output-file                | Set the output format of the command execution. The available parameters can be viewed with the command "ansible -doc-t callback-l".                    |
| --stdout_callback=<callback_name>| Performs debugging.                      |
| --install=<package_name>     | Specifies the software to be installed. If **--install=npu** is specified, the driver and firmware are installed. |
| --install-scene=<scene_name> | Specifies the scenario for installation. For details about the installation scenarios, see <a href="#scene">Installation Scenarios</a>. |
| --uninstall=<package_name>   | Uninstalls the specified software. If **--uninstall=npu** is specified, the driver and firmware will be uninstalled. |
| --upgrade=<package_name>     | Upgrades the specified software. If **--upgrade=npu** is specified, the driver and firmware will be upgraded. |
| --test=<target>              | Checks whether the specified component works properly. |

## <a name="scene">Installation Scenarios</a>

The offline installation tool provides several basic installation scenarios.

| Installation Scenario | Installed Components                     | Description                              |
| --------------------- | ---------------------------------------- | ---------------------------------------- |
| auto                  | all                                      | All software packages that can be found are installed. |
| infer_dev             | Driver, firmware, nnrt, toolbox, the Toolkit, torch, TFPlugin, and TensorFlow | Inference development scenario.          |
| infer_run             | Driver, firmware, nnrt, and toolbox      | Inference running scenario               |
| train_dev             | Driver, firmware, nnae、toolbox, the Toolkit, torch, TFPlugin, and TensorFlow | Training development scenario            |
| train_run             | Driver, firmware, nnae, toolbox, torch, TFPlugin, and TensorFlow | Training running scenario                |
| vmhost                | Driver, firmware, and toolbox            | VM host scenario                         |
| edge                  | Driver, firmware, atlasedge, ha          | Install MindX middleware, HA                        |

The configuration files for the preceding installation scenarios are stored in the **scene** directory. For example, the following shows the configuration file **scene/scene_infer_run.yml** of the inference development scenario:

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

To customize an installation scenario, refer to the preceding configuration file.
## <a name="config">Configuration Description</a>
### Proxy Configuration
If you want to use an HTTP proxy, either configure the proxy in an environment variable (recommended) or configure the proxy in the downloader/config.ini file.
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
os_list=CentOS_7.6_aarch64, CentOS_7.6_x86_64, CentOS_8.2_aarch64, CentOS_8.2_x86_64, Ubuntu_18.04_aarch64, Ubuntu_18.04_x86_64, BigCloud_7.6_aarch64, BigCloud_7.6_x86_64, ...          # OS information of the environment to be deployed.
```
###  <a name="sourceconfig">Source Configuration</a>
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

[epel]
baseurl=https://mirrors.huaweicloud.com/epel/7/aarch64
```
Indicates that both Base and EPEL sources are enabled from which system components will be queried and downloaded.Huawei source is used by default and can be modified as needed.If you modify, select a safe and reliable source and test whether the download and installation behavior is normal, otherwise it may cause incomplete download of the component or abnormal installation.Deleting the source may result in an incomplete download of the component.
