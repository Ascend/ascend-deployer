# Overview

## Functions

The offline installation tool provides automatic download and one-click installation of the OS components and Python third-party dependencies. It also supports the installation of the driver, firmware, and CANN software packages. The tools directory additionally places the Device IP configuration script, the use method can refer to <a href="#Device_IP">Device IP configuration specification</a>.

## Environment Requirements

### Description of the supported operating system
|    OS    | Version | CPU Architecture |            Installation Type             |
| :------: | :-----: | :--------------: | :--------------------------------------: |
|  BCLinux |   7.6   |     aarch64      | A minimal image is installed by default. |
|  BCLinux |   7.6   |      x86_64      | A minimal image is installed by default. |
|  BCLinux |   7.7   |     aarch64      | A minimal image is installed by default. |
|  CentOS  |   7.6   |     aarch64      | A minimal image is installed by default. |
|  CentOS  |   7.6   |      x86_64      | A minimal image is installed by default. |
|  CentOS  |   8.2   |     aarch64      | A minimal image is installed by default. |
|  CentOS  |   8.2   |      x86_64      | A minimal image is installed by default. |
|  Debian  |   9.9   |     aarch64      | A minimal image is installed by default. |
|  Debian  |   9.9   |      x86_64      | A minimal image is installed by default. |
|  Debian  |   10.0  |      x86_64      | A minimal image is installed by default. |
| EulerOS  |   2.8   |     aarch64      | A minimal image is installed by default. |
| EulerOS  |   2.9   |     aarch64      | A minimal image is installed by default. |
| EulerOS  |   2.9   |      x86_64      | A minimal image is installed by default. |
|  Kylin   |V10Tercel|     aarch64      | A minimal image is installed by default. |
|  Kylin   |V10Tercel|      x86_64      | A minimal image is installed by default. |
|  Kylin   |v10juniper|    aarch64      | A minimal image is installed by default. |
|   Linx   |   6     |     aarch64      | A minimal image is installed by default. |
|OpenEuler |20.03LTS |     aarch64      | A minimal image is installed by default. |
|OpenEuler |20.03LTS |      x86_64      | A minimal image is installed by default. |
|   SLES   |  12.4   |      x86_64      | A minimal image is installed by default. |
|   SLES   |  12.5   |      x86_64      | A minimal image is installed by default. |
|  Tlinux  |  2.4    |     aarch64      | A server image is installed by default.  |
|  Tlinux  |  2.4    |      x86_64      | A server image is installed by default.  |
|   UOS    | 20SP1   |     aarch64      | A minimal image is installed by default. |
|   UOS    | 20SP1   |      x86_64      | A minimal image is installed by default. |
|   UOS    |   20    |     aarch64      | A minimal image is installed by default. |
|   UOS    |   20    |      x86_64      | A minimal image is installed by default. |
|  Ubuntu  |18.04.1/5|     aarch64      | A minimal image is installed by default. |
|  Ubuntu  |18.04.1/5|      x86_64      | A minimal image is installed by default. |

### Description of supported hardware configuration
|  Central Inference Hardware  |  Central Training Hardware  |  Intelligent Edge Hardware  |
|:-------------:|:-------------:|:-------------:|
|  A300-3000    |  A300T-9000   |  A500 Pro-3000|
|  A300-3010    |  A800-9000    |               |
|  A300I Pro    |  A800-9010    |               |
|  A800-3000    |               |               |
|  A800-3010    |               |               |

## Precautions

- By default, the offline installation tool downloads and installs Python-3.7.5 as a Python version of the Cann package. This is explained in Python-3.7.5.Users can select the Python version by setting the ASCEND_PYTHON_VERSION environment variable, or the ASCEND_PYTHON_VERSION configuration item in the downloader/config.ini file (environment variable is preferred when setting at the same time).The optional Python versions are 3.7.0 to 3.7.11 and 3.8.0 to 3.8.11. This tool has only been fully adapted and tested on Python-3.7.5, and it is strongly recommended not to change the default configuration.
- Basic commands such as **tar**, **cd**, **ls**, **find**, **grep**, **chown**, **chmod**, **unzip**, **ssh** must be installed in the OS. It is recommended that during the installation process of Ubuntu/Debian system, select the option of [OpenSSH Server]/[SSH Server] when going to [Software Selection] to avoid missing SSH command.
- The offline installation tool supports only the default environment after the OS image is successfully installed. Do not install or uninstall software after the OS is installed. If some system software has been uninstalled, causing inconsistency with the default system package, you need to manually configure the network and use tools such as apt, yum, and dnf to install and configure the missing software.
- The offline installation tool can install only basic libraries to ensure that TensorFlow and PyTorch can run properly. If you need to run complex inference services or model training, the model code may contain libraries related to specific services. You need to install the libraries by yourself.
- When installing the SLES driver, the offline installer will set "allow_unsupported_modules" in /etc/modprob. d/10-unsupported-modules.conf to "1", which means that non-native drivers are allowed to be loaded during system boot.
- By default, the **root** user is not allowed to remotely log in to OSs such as EulerOS. Therefore, you need to set **PermitRootLogin** to **yes** in the **sshd_config** file before using this tool(Individual OS configuration methods may be different, please refer to the OS official description), and close the remote connection of root user after using this tool.
- Support for Ubuntu 18.04.1/5 installation of cross-compiled related components and the Aarch64 architecture toolkit package.
- CentOS 7.6 x86_64 with lower version kernel (below 4.5) of ATLAS 300T training card requires CentOS to be upgraded to 8.0 or above or a kernel patch is added. Failure to do so may result in firmware installation failure.Add a kernel patch method please refer to the reference [link] (https://support.huawei.com/enterprise/zh/doc/EDOC1100162133/b56ad5be).
- After the kylin V10 system's dependencies are installed, you need to wait for the system configuration to complete before you can use docker and other commands.
- You need to modify /etc/pam.d/su, delete # before 'auth efficient pam_ rootok.so', so that the root user switch to other users without entering a password when the system is Linx.
- After the default installation of tlinux system, the total space of the root directory is about 20G, and the packages that exceed the available disk space can not be placed in the resources directory to avoid decompression or installation failure.
- BCLinux 7.6 does not have python3 by default. The `yum install python3` command is run before the download operation. Because the BCLinux 7.6 system source does not contain python3, modify the source configuration file by referring to the BCLinux official configuration file, or change "el7.6" to "el7.7" in "/etc/yum.repos.d/BCLinux-Base.repo"(Run the `sed -i 's/el7.6/el7.7/g' /etc/yum.repos.d/BCLinux-Base.repo` command). After the installation, restore the original configuration.
- tensorflow-1.15.0 aarch64 and torch-1.5.0/apex-0.1 aarch64/x86_64 are not available for download. You need to place them in your resources/pylibs directory, otherwise the installation will be skipped.
- Euleros, SLES, Debian and other systems may trigger driver source compilation when installing the driver. Users are required to install the kernel header package consistent with the kernel version of the system (which can be viewed through 'uname -r' command). The details are as follows.

### Description of the kernel header package
| OS          | kernel header package that matches the kernel version of the system  | How to get            |
| ---------   | ---------------------------------------------------------------------| ----------------------|
| EulerOS     | kernel-headers-`<version>`、kernel-devel-`<version>`                 | Contact the OS vendor, or find it in the "devel_tools.tar.gz" tool component that comes with the corresponding OS |
| SLES        | kernel-default-`<version>`、kernel-default-devel-`<version>`         | Contact the OS vendor, or look it up in the image of the corresponding OS |
| Debian      | linux-headers-`<version>`、linux-headers-`<version>`-common、linux-kbuild-`<version>`| Contact the OS vendor, or look it up in the image of the corresponding OS |

## Tool installation

### pip install

```bash
pip3 install ascend-deployer
```
- Version requirement: python >= 3.6
- It is recommended that you install it as root and use the python3 and pip3 tools on your system. If pip3 is not available, please install it by yourself
- Refer to <a href="#pip_manual">Operation instruction: pip install</a>

### git install

```bash
git clone https://gitee.com/ascend/ascend-deployer.git
```

### download zip

Click the "clone / download" button in the upper right corner, and then click the "download zip" below to download and unzip to use. To avoid the risk of excessive permissions after unzipping, it is recommended to set the environment umask to 022 or higher before unzipping the zip package, and only unzip and use tools in the user's HOME directory, and only for the user's own use. The above two installation methods please pay attention to the tool directory permissions risk.

# Operation Instructions

## Downloading OS Components and Python Third-party Dependencies

The download function can be used in the Windows or Linux OSs.

### Notice

- Modify the configuration file to download required OS components(Windows), edit the **downloader/config.ini** file. For details, see <a href="#config">Configuration Description</a>.
- A large amount of open source software needs to be installed. The open source software downloaded using the offline installation tool comes from the OS source. You need to fix the vulnerabilities of the open source software as required. You are advised to use the official source to update the software regularly. For details, see <a href="#sourceconfig">Source Configuration</a>.
- The downloaded software is automatically stored in the **resources** directory.
- After the installation, it is recommended to uninstall the third-party components such as gcc and g++ and cpp and jdk that may have security risks in the system.

### Download

- Windows
  1. Python 3 is required in Windows. Python 3.7 or later is recommended.
     Download link: [python3.7.5](https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe)
     Complete the installation as prompted. During the installation, select **Add Python to environment variables** on the **Advanced Options** page. Otherwise, you need to manually add environment variables.
  2. Start download.
     Set the os_list or software configuration item of "downloader/config.ini" and run **start_download.bat**.Run **start_download_ui.bat** (recommended because it allows you to select the Related components of OS or PKG to be downloaded on the displayed UI).
- Linux
  1. Run the `./start_download.sh --os-list=<OS1>,<OS2> --download=<PK1>,<PK2>==<Version>` command to start download, refer to <a href="#download_parameter">Linux Download Parameter Description</a>. The following call ` * * sh ` script using `. / * * sh ` way, also can use ` bash * * sh ` calls, please according to actual use.
  2. Support root and non-root users to perform download operations, Non-root users do not need sudo permissions, but do need to have executable permissions for the tool directory; The presence of Python 3 on the environment is checked when the download is performed. If python3 does not exist, it can be divided into two types: if the current user is root, the tool will automatically download python3 through APT, YUM and other tools;If the current user is not root, the tool prompts the user to install Python3.

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
| install_path | The installation path of the CANN package，will be pass to --install-path options   |

### Notice

- The install_path parameter can only specify the CANN package's installation path. This parameter is valid for root (The CANN package is not installed on the environment, i.e., there is no `/etc/scend/cann_install.info` file, otherwise it will be installed to the path specified by the contents of the file) and not for non-root (only to the default ~/Ascend path).The install_path parameter does not specify the installation path for the driver package and edge components (AtlasEdge and HA). The driver package can only be installed to the default path /usr/local/Ascend and edge components (AtlasEdge and HA) can only be installed to the default path /usr/local.
- The driver software packages will user HwHiAiUser and group as default user. The **HwHiAiUser** user must be created first and guarantee the password of the created user, the expiration date of the password and the security issues in subsequent use. The commands to create user and group is below:

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

- List of software supported by non-root users

|Software name  | description|
|:------------- |:------------------------------------- |
|Python375, gcc | python3.7.5 and gcc7.3.0 is installed in the $HOME/.local/ directory|
|Python framework | tensorflow, pytorch, mindpore|
|CANN | toolbox, nnae, nnrt, tfplugin and toolkit are installed in the $HOME directory by default, and the specified path is not supported|
|MindStudio | installed in the $HOME/ directory|

Note:
  1. Non-root users need root users to install system components and driver before they can install the above components.
  2. Non-root users need to join the driver installation group to install and use nnrt and toolkit normally. The default driver installation group is HwHiAiUser, Modify the user group command as follows:

```bash
usermod -a -G HwHiAiUser non-root-user
```

### Obtaining Software Packages

1. Prepare the software packages to be installed as required (The driver, firmware, and CANN software packages can be installed). Save the software packages to be installed in the **resources** directory. The following is an example.
   - Driver and firmware: [Link](https://www.huaweicloud.com/intl/en-us/ascend/resource/Software)
   - CANN software package: [Link](https://www.huaweicloud.com/intl/en-us/ascend/cann)
2. The package only supports the ZIP format. Only one version of the package should exist in the resources directory at installation time, otherwise there may be version mismatch. If there are no packages in the resources directory, the tool skips the installation.
3. Support Atlas 500 and Atlas 500Pro batch installation of IEF Agent, refer to UserManual-IEF documentation to prepare IEF product certificate, registration tools, installation tools, placed in the resources directory.
   - IEF relevant certificates and tools: [Link](https://support.huaweicloud.com/usermanual-ief/ief_01_0031.html)
   - The Atlas 500 comes pre-loaded with registration tools and installation tools, so you just need to prepare the product certificate and place it in the Resources directory.The Atlas 500Pro requires all three certificates and tools
   - Atlas 500 only supports the Euleros 2.8 Aarch64 tailoring operating system, not other systems, so it does not support the offline deployment tool to run locally, only supports remote installation, and also does not support non-root installation. Atlas 500Pro supports both local and remote installations
   - Depending on the edge node AtlasEdge middleware working properly, Atlas 500 comes with AtlasEdge middleware， Atlas 500Pro needs to install AtlasEdge middleware first
   - Depends that the IEF server is working properly and that the network between the edge device and the IEF is working properly. Whether the edge node is successfully managed needs to be observed at the IEF Web front end. Refer to the usermanual-IEF documentation for other restrictions
4. The files of docker image require the user to log in to ascendhub, pull the image, and then transfer it to resources/docker_images directory before docker-images' installation. please create this directory by yourself.The file name of docker image is like to ubuntu_18.04_{x86_ 64 | aarch64}.tar, the system architecture is in the brackets, and only the two architectures in the brackets are supported.

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

2. Run the installation script and select an installation mode (software-specific installation or scenario-specific installation) as required.

   - Software-specific installation
     `./install.sh --install=<package_name>`
     You can run the `./install.sh --help` command to view the options of <package_name>. Example command:
     `./install.sh --install=sys_pkg,python375,npu //Install system packages and python3.7.5 and driver and firmware.`
     Notes:
     - Installation sequence: sys_pkg > python375 > npu(driver and firmware) > CANN software package(such as the Toolkit and nnrt) > AI framework(pytorch、tensorflow、mindspore).
     - After the driver or firmware is installed, maybe you need run the `reboot` command to restart the device for the driver and firmware to take effect.
     - Some components require runtime dependencies. For example, PyTorch requires the Toolkit to provide runtime dependencies, TensorFlow and npubridge require TFPlugin to provide runtime dependencies, and mindspore require driver and toolkit to provide runtime dependencies.
     - All the installation of Python libraries must first install Python 3.7.5, such as python, tensorflow, Mindstore, etc.
     - `--install=mindspore` will install version 1.2.1 of MindSpore and requires python3.7.5 and the accompanying version of the Cann package to work properly.  . Please refer to the official website of [mindspore](https://mindspore.cn/install) for software supporting instructions.
   - Scenario-specific installation
     `./install.sh --install-scene=<scene_name>`
     The offline installation tool provides several basic installation scenarios. For details, see <a href="#scene">Installation Scenarios</a>. Example command:
      `./install.sh --install-scene=auto     // Automatic installation of all software packages that can be found`

3. After the installation, run the following command to check whether the specified component works properly:
   `./install.sh --test=<target>`
   You can run the `./install.sh --help` command to view the options of <target>. Example command:
   `./install.sh --test=driver // Test whether the driver is normal.`

### Batch Installation

1. SSH connection based on key authentication.
   Configure the IP addresses of other devices where the packages to be installed. Edit the **inventory_file** file. The format is shown as follows:
   ```
   [ascend]
   ip_address_1 ansible_ssh_user='root'      # root user
   ip_address_2 ansible_ssh_user='root'
   ip_address_3 ansible_ssh_user='username'  # non-root user
   ```

Configure the reference operation for key authentication
   ```bash
   ssh-keygen -t rsa -b 2048   # Log in to the management node and generate the SSH Key. For security reasons, it is recommended that the user Enter the key password at the "Enter passphrase" step, and ensure that the password complexity is reasonable. It is recommended to set the umask to 0077 before executing this command and to restore the original umask after executing it.
   ssh-copy-id -i ~/.ssh/id_rsa.pub <user>@<ip>   # Copy the public key of the management node to the machines of all nodes, and replace <user>@<ip> with the account and ip of the corresponding node to be copied to.
   ssh <user>@<ip>   # Verify that it is possible to log on to the remote node, and replace <user>@<ip> with the account and IP of the corresponding node to be logged in.
   ```

Note:
- Please be aware of the risks involved in the use and storage of SSH keys.

2. Set up the SSH agent to manage the SSH key to avoid entering the key password during the bulk installation of the tool. The following are the guidelines for setting up an SSH agent:
   ```bash
   ssh-agent bash   # Start the ssh-agent bash process
   ssh-add          # Add a private key to the ssh-agent
   ```

3. Run the `./install.sh --check` command to test the connectivity of the devices where the packages to be installed.
    Ensure that all devices can be properly connected. If a device fails to be connected, check whether the network connection of the device is normal and whether sshd is enabled.

4. The following operation is the same as the above Single-Device Installation steps 2 and 3.

5. When the bulk installation of the tool is completed, exit the SSH agent process in time to avoid security risks.
   ```bash
   exit   # Exit the ssh-agent bash process
   ```

# <a name="pip_manual">Operation instruction: pip install</a>

When the tool is installed with pip, two entrances will be provided for easy operation.

- ascend-download
- ascend-deployer

Both entrances are available to both root and non-root users

## Download

```bash
ascend-download --os-list=<OS1>,<OS2> --download=<PK1>,<PK2>==<Version>
```

Both win10 and Linux can execute

- Download all resources to "ascend-deployer/resources/"

- In windows, the ascend deployer directory is generated in the current directory where the command is executed. When the download is complete, copy the whole directory to the Linux server to be deployed.

- In Linux, the ascend-deployer directory will be generated under the HOME directory. You can replace the user's HOME directory by setting the environment variable ASCEND_Deployer_HOME. Non-root users must ensure that the directory exists and can read and write properly.

## Installation

```bash
ascend-deployer --install=<pkg1,pkg2>
```

The ascend-deployer command is essentially a wrapper of install.sh.The use method is exactly the same as directly executing install.sh in the ascend deployer directory. The ASCEND_Deployer command automatically looks for the file ASCEND_Deployer /install.sh in the user's HOME directory and replaces the user's HOME directory by setting the environment variable ASCEND_Deployer_HOME. Non-root users must ensure that the directory exists and can read and write properly.

# <a name="set_env_var">Environment Variable Configuration</a>
The offline deployment tool can install Python 3.7.5, To ensure that the built-in Python (Python 2.x or Python 3.x) is not affected, you need to configure the following environment variables before using Python 3.7.5:

```
export PATH=/usr/local/python3.7.5/bin:$PATH                         # root
export LD_LIBRARY_PATH=/usr/local/python3.7.5/lib:$LD_LIBRARY_PATH   # root

export PATH=~/.local/python3.7.5/bin:$PATH                         # non-root
export LD_LIBRARY_PATH=~/.local/python3.7.5/lib:$LD_LIBRARY_PATH   # non-root
```
This tool will automatically install the Python 3.7.5 environment variable in /usr/local/ascendrc file. You can easily set the Python 3.7.5 environment variable by following the following command
```
source /usr/local/ascendrc    # root
source ~/.local/ascendrc      # non-root
```

Similarly, other software packages or tools installed by offline deployment tools can be used normally only after users refer to the corresponding official information and configure environment variables or make other Settings.

# Follow-up

- Inference scenario
  If you need to develop applications, please refer to the relevant official materials, such as CANN Application Software Development Guide (C and C++) or CANN Application Software Development Guide (Python).
- Training scenario
  For network model migration and training, please refer to the relevant official materials, such as TensorFlow Network Model Porting and Training Guide or PyTorch Network Model Porting and Training Guide.
- Delete this tool
  This tool is only used for deployment. When installation completed, it should be deleted for free the disk space.

| Something that should be deleted | instructions                        |
|:-------------------------------  |:-------------------------------------|
| ascend-deployer                  | Directory of tool on the controller  |
|`pip3 uninstall ascend-deployer`  | Tool pip-installed on the controller, uninstall using commands|
| ~/ansible                        | Customize information collection configuration files on the controller and remote machines|
| `~/resources和~/resources.tar`   | Resource directory on the controller and remote machines|
| ~/build                          | Source package decompression directory on the controller and remote machines|

# Reference Information

## <a name="parameter">Install Parameter Description</a>

Select corresponding parameters to install the software. The command format is as follows:
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
| --test=<target>                   | Checks whether the specified component works properly.                                                                                                                         |

## <a name="download_parameter">Linux Download Parameter Description</a>

| Parameter           | Description                                    |
|:------------------- | ---------------------------------------------- |
| `--os-list=<OS1>,<OS2>`| set specific os softwares to download          |
| `--download=<PK1>,<PK2>==<Version>`| download specific software. such as 如MindStudio、CANN |

Currently MindStudio supports 2.0.0, 3.0.1 and 3.0.2 versions, and Cann supports 20.2.rc1, 5.0.1 and 5.0.2.1 versions. Only one version of the MindStudio or Cann package should exist in the resources directory at the time of installation, otherwise there may be versions that do not match. `./start_download.sh --download=<PK1>,<PK2>==<Version>`, when `<Version>` is missing, `<PK>` is the latest. MindStudio installation please refer to the [install MindStudio](https://gitee.com/ascend/ascend-deployer/blob/master/docs/Install_MindStudio.md).

## <a name="scene">Installation Scenarios</a>

The offline installation tool provides several basic installation scenarios.

| Installation Scenario | Installed Components                                                          | Description                                            |
| --------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------ |
| auto        | all                                                              | All software packages that can be found are installed |
| vmhost      | sys_pkg、npu、toolbox                                            | VM host scene                                         |
| edge        | sys_pkg、atlasedge、ha                                           | Install MindX middleware, HA                          |
| offline_dev | sys_pkg、python375、npu、toolkit                                  | Offline development scene                            |
| offline_run | sys_pkg、python375、npu、nnrt                                     | Offline run scene                                    |
| mindspore   | sys_pkg、python375、npu、toolkit、mindspore                       | mindspore scene                                      |
| tensorflow_dev | sys_pkg、python375、npu、toolkit、tfplugin、tensorflow         | tensorflow development scene                         |
| tensorflow_run | sys_pkg、python375、npu、nnae、tfplugin、tensorflow            | tensorflow run scene                                 | 
| pytorch_dev | sys_pkg、python375、npu、toolkit、pytorch                         | pytorch development scene                            |
| pytorch_run | sys_pkg、python375、npu、nnae、pytorch                            | pytorch run scene                                    |


The configuration files for the preceding installation scenarios are stored in the **scene** directory. For example, the following shows the configuration file **scene/scene_auto.yml** of the auto scene:

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

To customize an installation scenario, refer to the preceding configuration file.

## <a name="config">Configuration Description</a>

### Proxy Configuration

If you want to use an HTTP proxy, configure the proxy in an environment variable. This tool validates HTTPS certificates by default, if a certificate error occurs during the download process, it may be that the proxy server has a security mechanism for certificate replacement, so you need to install the proxy server certificate first.

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
   verify=true         # Whether to verify the HTTPS certificate. If it is closed, it may encounter a man-in-the-middle attack. Please be aware of the security risks
   ```

### Windows Download Configuration

You can configure and modify the download parameters in the **downloader/config.ini** file to download the required OS components on windows. It is not recommended to modify the configuration file directly. It is recommended to run start_download_ui.bat and use the UI interface to check the required components

```
[download]
os_list=CentOS_7.6_aarch64, CentOS_7.6_x86_64, CentOS_8.2_aarch64, CentOS_8.2_x86_64, Ubuntu_18.04_aarch64, Ubuntu_18.04_x86_64 ...          # OS information of the environment to be deployed.
[software]
pkg_list=CANN_5.0.1,MindStudio_3.0.1  # CANN或MindStudio to be deployed.
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
  [epel]
  baseurl=https://mirrors.huaweicloud.com/epel/7/aarch64
  ```


Indicates that both Base and EPEL sources are enabled from which system components will be queried and downloaded.Huawei source is used by default and can be modified as needed.If you modify, select a safe and reliable source and test whether the download and installation behavior is normal, otherwise it may cause incomplete download of the component or abnormal installation.Deleting the source may result in an incomplete download of the component.

## <a name="url">Public Web Site URL</a>
```
https://github.com
https://gcc.gnu.org
http://mirrors.bclinux.org
https://archive.kylinos.cn
https://mirrors.tencent.com
https://mirrors.bfsu.edu.cn
https://repo.huaweicloud.com
https://mirrors.huaweicloud.com
https://cache-redirector.jetbrains.com
https://obs-9be7.obs.myhuaweicloud.com
https://ms-release.obs.cn-north-4.myhuaweicloud.com
https://obs-9be7.obs.cn-east-2.myhuaweicloud.com
```

## <a name="faq">FAQ</a>
1. Q: The first time you execute './install.sh --check 'or any other installation command, the system dependencies and Python 3.7.5 will be installed automatically. If the installation process is interrupted unintentionally, the second time you execute the command, the RPM and DPKG tools may be locked, or Python 3.7.5 functionality may be missing.
- A: Release the RPM/DPKG tool lock, delete the Python 3.7.5 installation directory, and install again using the tool.(Python 3.7.5 installation directory may refer to <a href="#set_env_var"> to configure the environment variable </a>)

2. Q: Non-root users are prompted for the sudo password when installing the pre-5.0.1 Toolkit.
- A: For security reasons, this tool does not require non-root users to have sudo privileges, so it does not support non-root users to install the toolkit prior to 5.0.1.

3. Q: The tool will use the Huawei Software Integrity Protection Root Certificate, but does it have the ability to verify that the certificate has been revoked?  Is there a mechanism for the CRL files in the installation package to be up to date with the local CRL files on the system? Does the tool have the ability to compare and update CRL files independently?
- A: This tool compares the effective time of the CRL file in the installation package with the CRL file locally on the system, and verifies whether the certificate has been revoked using the latest CRL file.  For the root user, the system of local CRL files to the `/etc/hwsipcrl/ascendsip.crl`, for non-root users, for the file `~/.local/hwsipcrl/ascendsip.crl`. If the system-local CRL file does not exist or takes effect earlier than the CRL file in the installation package, the system-local CRL file will be replaced by the CRL file in the installation package. The update_crl.sh script is placed in the tools directory, execute `bash update_crl.sh <crl_file>` command, `<crl_file>` is the path of the CRL file uploaded by the user.


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
