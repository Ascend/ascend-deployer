# Overview

## Functions

The offline installation tool provides automatic download and one-click installation of the OS components and Python third-party dependencies. It also supports the installation of the driver, firmware, and CANN software packages. The tools directory additionally places the Device IP configuration script, the use method can refer to [Device IP configuration](https://gitee.com/ascend/ascend-deployer/blob/master/docs/Device_IP_Configuration.md).

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
|   UOS    |20-1020e |     aarch64      | A minimal image is installed by default. |
|   UOS    |   20    |     aarch64      | A minimal image is installed by default. |
|   UOS    |   20    |      x86_64      | A minimal image is installed by default. |
|  Ubuntu  |18.04.1/5|     aarch64      | A minimal image is installed by default. |
|  Ubuntu  |18.04.1/5|      x86_64      | A minimal image is installed by default. |
|  Ubuntu  |20.04.1  |     aarch64      | A minimal image is installed by default. |
|  Ubuntu  |20.04.1  |      x86_64      | A minimal image is installed by default. |

### Description of supported hardware configuration
|  Central Inference Hardware  |  Central Training Hardware  |  Intelligent Edge Hardware  |
|:-------------:|:-------------:|:-------------:|
|  A300-3000    |  A300T-9000   |  A500 Pro-3000|
|  A300-3010    |  A800-9000    |  Atlas200(EP) |
|  A300I Pro    |  A800-9010    |               |
|  A300V Pro    |               |               |
|  A800-3000    |               |               |
|  A800-3010    |               |               |

## Precautions

- By default, the offline installation tool downloads and installs Python-3.7.5 as a Python version of the Cann package. This is explained in Python-3.7.5.Users can select the Python version by setting the ASCEND_PYTHON_VERSION environment variable, or the ASCEND_PYTHON_VERSION configuration item in the downloader/config.ini file (environment variable is preferred when setting at the same time).The optional Python versions are 3.7.0 to 3.7.11 and 3.8.0 to 3.8.11. This tool has only been fully adapted and tested on Python-3.7.5, and it is strongly recommended not to change the default configuration.
- Basic commands such as **tar**, **cd**, **ls**, **find**, **grep**, **chown**, **chmod**, **unzip**, **ssh** must be installed in the OS. It is recommended that during the installation process of Ubuntu/Debian system, select the option of [OpenSSH Server]/[SSH Server] when going to [Software Selection] to avoid missing SSH command.
- The offline installation tool supports only the default environment after the OS image is successfully installed. Do not install or uninstall software after the OS is installed. If some system software has been uninstalled, causing inconsistency with the default system package, you need to manually configure the network and use tools such as apt, yum, and dnf to install and configure the missing software.
- The offline installation tool can install only basic libraries to ensure that TensorFlow and PyTorch can run properly. If you need to run complex inference services or model training, the model code may contain libraries related to specific services. You need to install the libraries by yourself.
- Offline installation tools except install.sh、start_download.sh、start_download_ui.bat and start_download.bat, the rest of the files are not designed for the user to use the interface or command. Do not use them directly.
- It is forbidden to put the password in the inventory_file file.
- CentOS 7.6 x86_64 with lower version kernel (below 4.5) of ATLAS 300T training card requires CentOS to be upgraded to 8.0 or above or a kernel patch is added. Failure to do so may result in firmware installation failure.Add a kernel patch method please refer to the reference [link] (https://support.huawei.com/enterprise/zh/doc/EDOC1100162133/b56ad5be).
- A300I Pro and A300V Pro must be set variable **cus_npu_info** in inventory_file, A300I pro should be **300i-pro**, A300V Pro should be **300v-pro**.
- The hardware configurations of the Atlas200 EP and A300 card (A300-3000, A300-3010, A800-3000, and A800-3010) cannot be distinguished. The following conditions must be met when using the Atlas200 EP. The Atlas200 EP and A300 inference card environments cannot be deployed in batches. If the deployed machine contains the Atlas200 EP, do not store the NPU package of the A300 EP in the Resources directory. If the deployed machine contains the A300 inference card, do not store the NPU package of the Atlas200 EP in the Resources directory. Because of the above two restrictions, `--download=CANN` does not include the NPU package of Atlas200 EP. Please prepare it yourself.
- When installing the SLES driver, the offline installer will set "allow_unsupported_modules" in /etc/modprob. d/10-unsupported-modules.conf to "1", which means that non-native drivers are allowed to be loaded during system boot.
- By default, the **root** user is not allowed to remotely log in to OSs such as EulerOS. Therefore, you need to set **PermitRootLogin** to **yes** in the **sshd_config** file before using this tool(Individual OS configuration methods may be different, please refer to the OS official description), and close the remote connection of root user after using this tool.
- Support for Ubuntu 18.04.1/5 installation of cross-compiled related components and the Aarch64 architecture toolkit package.

- After the kylin V10 system's dependencies are installed, you need to wait for the system configuration to complete before you can use docker and other commands.
- Since the docker and containerd installed under cenos can coexist in multiple versions, it is recommended to confirm whether docker has been installed on the system before installing system dependency on CentOS 7.6 and CentOS 8.2 systems. If so, please uninstall it with `yum -y remove docker-ce`、`yum -y remove docker-ce-cli`、`yum -y remove containerd.io` command before installing system dependency.
- You need to modify /etc/pam.d/su, delete # before 'auth efficient pam_ rootok.so', so that the root user switch to other users without entering a password when the system is Linx.
- After the default installation of tlinux system, the total space of the root directory is about 20G, and the packages that exceed the available disk space can not be placed in the resources directory to avoid decompression or installation failure.
- BCLinux 7.6 does not have python3 by default. The `yum install python3` command is run before the download operation. Because the BCLinux 7.6 system source does not contain python3, modify the source configuration file by referring to the BCLinux official configuration file, or change "el7.6" to "el7.7" in "/etc/yum.repos.d/BCLinux-Base.repo"(Run the `sed -i 's/el7.6/el7.7/g' /etc/yum.repos.d/BCLinux-Base.repo` command). After the installation, restore the original configuration.
- tensorflow-1.15.0 aarch64 and torch-1.5.0/apex-0.1 aarch64/x86_64 are not available for download. You need to place them in your resources/pylibs directory, otherwise the installation will be skipped.
- Euleros, SLES, Debian and other systems may trigger driver source compilation when installing the driver. Users are required to install the kernel header package consistent with the kernel version of the system (which can be viewed through 'uname -r' command). The details are as follows.
- Based on security considerations, it is recommended to reinforce the unzipped installation directory(ascend-deployer) and set its permission to only allow owner to use.

- Description of the kernel header package

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

Click the "clone / download" button in the upper right corner, and then click the "download zip" below to download and unzip to use.In order to prevent the software package from being maliciously tampered with during delivery or storage, it is recommended that users download the software package and use sha256sum to verify the integrity of the software. For the latest official version of sha256sum, please refer to readme of the master branch. This tool can be used by root and non-root users. To avoid the risk of excessive permissions after unzipping, it is recommended to set the environment umask to 077 before unzipping the zip package, and only unzip and use tools in the user's HOME directory, and only for the user's own use. The above two installation methods please pay attention to the tool directory permissions risk.

# Operation Instructions

## Download Instructions

The download function can be used in the Windows or Linux OSs.

### Download Notice

- Modify the configuration file to download required OS components(Windows), edit the **downloader/config.ini** file. For details, see <a href="#config">Configuration Description</a>.
- A large amount of open source software needs to be installed. The open source software downloaded using the offline installation tool comes from the OS source. You need to fix the vulnerabilities of the open source software as required. You are advised to use the official source to update the software regularly. For details, see <a href="#sourceconfig">Source Configuration</a>.
- The downloaded software is automatically stored in the **resources** directory.
- Docker user groups are created and the Docker service is started during the installation. After the installation, it is recommended to uninstall the third-party components such as gcc and g++ and cpp and jdk that may have security risks in the system.

### Download

- Windows
  1. Python 3 is required in Windows. Python 3.7 or later is recommended.
     Download link: [python3.7.5](https://www.python.org/ftp/python/3.7.5/python-3.7.5-amd64.exe), Complete the installation as prompted.
     During the installation, select **Add Python to environment variables** on the **Advanced Options** page. Otherwise, you need to manually add environment variables.

  2. Start download.
     Set the os_list or software configuration item of "downloader/config.ini" and run **start_download.bat**.Run **start_download_ui.bat** (recommended because it allows you to select the Related components of OS or PKG to be downloaded on the displayed UI).

- Linux
  1. Run the `./start_download.sh --os-list=<OS1>,<OS2> --download=<PK1>,<PK2>==<Version>` command to start download, refer to <a href="#download_parameter">Download Parameter Description</a>. The following call ` * * sh ` script using `. / * * sh ` way, also can use ` bash * * sh ` calls, please according to actual use.It is recommended to set the environment umask to 077 before downloading.

  2. The presence of Python 3 on the environment is checked when the download is performed. If python3 does not exist, it can be divided into two types: if the current user is root, the tool will automatically download python3 through APT, YUM and other tools;If the current user is not root, the tool prompts the user to install Python3.

## Installation Instructions

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

- The install_path parameter can specify the CANN package's installation path. This parameter is valid for root (The CANN package is not installed on the environment, i.e., there is no `/etc/scend/cann_install.info` file, otherwise it will be installed to the path specified by the contents of the file) and not for non-root (only to the default ~/Ascend path).The install_path parameter does not specify the installation path for the driver package and edge components (AtlasEdge and HA). The driver package can only be installed to the default path /usr/local/Ascend and edge components (AtlasEdge and HA) can only be installed to the default path /usr/local.
- The install_path parameter can only specify the Toolbox package's installation path. This parameter is valid for root (The Toolbox package is not installed on the environment, i.e., there is no `/etc/scend/cann_install.info` and `/etc/Ascend/ascend_toolbox_install.info` file, otherwise it will be installed to the path specified by the contents of the file) and not for non-root (only to the default ~/Ascend path).
- When the offline tool is a zip package, the user needs to confirm that the decompression directory of the offline tool is a new decompression, and the directory permission is 700 without soft links.
- After installation, the configuration needs to be modified. It is recommended to cancel the login of root user.
- The driver software packages will user HwHiAiUser and group as default user. The **HwHiAiUser** user must be created first and guarantee the password of the created user, the expiration date of the password and the security issues in subsequent use. The commands to create user and group is below:

```bash
#add HwHiAiUser group
groupadd HwHiAiUser

#add HwHiAiUser user add it to HwHiAiUser group
#set /home/HwHiAiUser as HwHiAiUser's HOME directory and create
#set /bin/bash HwHiAiUser's default shell
useradd -g HwHiAiUser -d /home/HwHiAiUser -m HwHiAiUser -s /bin/bash
```

- When installing edge components (AtlasEdge and HA) in versions 2.0.2, mabey need limit the login status of user HwHiAiUser. When installing the driver package, set user HwHiAiUser to the login state. Set this parameter based on the actual scenario.
```bash
usermod -s /sbin/nologin HwHiAiUser   # When installing edge components (AtlasEdge and HA) in versions 2.0.2
usermod -s /bin/bash HwHiAiUser   # When installing the driver package
```

- When installing AtlasEdge components in versions 2.0.3 and later, the component creates a MindXEdge user by default.

- When installing the edge components in version 2.0.4, you need to install haveged in advance. For example, Ubuntu system uses the command `apt install haveged`. After installation, you need to execute `systemctl enable haveged` and `systemctl start haveged` to start the haveged service.

- If you need to specify the running user and user group, modify the **inventory_file** file. The file content is as follows:

```
[ascend:vars]
user=HwHiAiUser
group=HwHiAiUser
```

- List of software supported by non-root users

|Software name  | description|
|:------------- |:------------------------------------- |
|Python, gcc | python3.7.5 and gcc7.3.0 is installed in the $HOME/.local/ directory|
|Python framework | tensorflow, pytorch, mindpore|
|CANN | toolbox, nnae, nnrt, tfplugin and toolkit are installed in the $HOME directory by default, and the specified path is not supported|
|MindStudio | installed in the $HOME/ directory|

Note:
  1. Non-root users need root users to install system components and driver before they can install the above components.
  2. After installing gcc7.3.0, you need to establish a symbolic link to use it. For example, gcc7.3.0 installed by root executes the command `ln -sf /usr/local/gcc7.3.0/bin/gcc /usr/bin/gcc`.
  3. Non-root users need to join the driver installation group to install and use nnrt and toolkit normally. The default driver installation group is HwHiAiUser, Modify the user group command as follows:

```bash
usermod -a -G HwHiAiUser non-root-user
```

### Obtaining Software Packages

1. Prepare the software packages to be installed as required (The driver, firmware, and CANN software packages can be installed). Save the software packages to be installed in the **resources** directory. The following is an example.
   - Driver and firmware: [Link](https://www.huaweicloud.com/intl/en-us/ascend/resource/Software)
   - CANN software package: [Link](https://www.huaweicloud.com/intl/en-us/ascend/cann)
2. The package only supports the ZIP format. Only one version of the package should exist in the resources directory at installation time, otherwise there may be version mismatch. If there are no packages in the resources directory, the tool skips the installation.
3. Support Atlas 500 and Atlas 500Pro batch installation of IEF Agent, refer to UserManual-IEF documentation to prepare IEF product certificate, registration tools, installation tools, placed in the resources directory.
   - IEF relevant certificates and tools: [Link](https://support.huaweicloud.com/usermanual-ief/ief_01_0100.html)
   - The Atlas 500 comes pre-loaded with registration tools and installation tools, so you just need to prepare the product certificate and place it in the Resources directory.The Atlas 500Pro requires all three certificates and tools
   - Atlas 500 only supports the Euleros 2.8 Aarch64 tailoring operating system, not other systems, so it does not support the offline deployment tool to run locally, only supports remote installation, and also does not support non-root installation. Atlas 500Pro supports both local and remote installations
   - Depending on the edge node AtlasEdge middleware working properly, Atlas 500 comes with AtlasEdge middleware， Atlas 500Pro needs to install AtlasEdge middleware first
   - Depends that the IEF server is working properly and that the network between the edge device and the IEF is working properly. Whether the edge node is successfully managed needs to be observed at the IEF Web front end. Refer to the usermanual-IEF documentation for other restrictions
4. The files of docker image require the user to log in to ascendhub, pull the image, and then transfer it to resources/docker_images directory before docker-images' installation. please create this directory by yourself.The file name of docker image is like to ubuntu_18.04_{x86_ 64 | aarch64}.tar, the system architecture is in the brackets, and only the two architectures in the brackets are supported.The installation of docker image will install the system package first, so download the corresponding system package before installing docker image; Users need to ensure the security of the docker image to be installed.

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

   Edit the inventory_file file. The default is as follows:

   ```
   [ascend]
   localhost ansible_connection='local'
   ```

2. Run the installation script and select an installation mode (software-specific installation or scenario-specific installation) as required.Note: if other users need to be able to use Python installed by root user, please set umask to 022 in advance. Before setting, confirm that the umask permission meets the security requirements of your organization.

    - 2.1 Software-specific installation

    run the `./install.sh --install=<package_name_1>,<package_name_2>`. The following is an example.

    ```
    ./install.sh --help     # Viewing Help Information.
    ./install.sh --install=sys_pkg,python,npu     # Installing system dependencies and python3.7.5 and driver and firmware.
    ```

    Notes:

        - Installation sequence: sys_pkg > python > npu(driver and firmware) > CANN software package(such as the Toolkit and nnrt) > AI framework(pytorch、tensorflow、mindspore).
        - After the driver or firmware is installed, maybe you need run the `reboot` command to restart the device for the driver and firmware to take effect.
        - Some components require runtime dependencies. For example, PyTorch requires the Toolkit to provide runtime dependencies, TensorFlow and npubridge require TFPlugin to provide runtime dependencies, and mindspore require driver and toolkit to provide runtime dependencies.
        - All the installation of Python libraries must first install Python 3.7.5, such as python, tensorflow, Mindstore, etc.

    - 2.2 Scenario-specific installation(Recommended for non-professional users)

    run the `./install.sh --install-scene=<scene_name>`. The following is an example.
    ```
    ./install.sh --install-scene=auto     # Automatic installation of all software packages that can be found
    ```
    The offline installation tool provides several basic installation scenarios. For details, see <a href="#scene">Installation Scenarios</a>.

3. After the installation.

    run the `./install.sh --test=<target>`. The following is an example.
    ```
    ./install.sh --test=driver     # Test whether the driver is normal.
    ```

### Batch Installation

1. SSH connection based on key authentication,Please confirm that paramiko is not installed in the system before installation (ansible will use paramiko in some cases, and its improper configuration may cause security problems).

   Configure the IP addresses of other devices where the packages to be installed. Edit the **inventory_file** file. The format is shown as follows:
   ```
   [ascend]
   ip_address_1 ansible_ssh_user='root'      # root user
   ip_address_2 ansible_ssh_user='root'
   ip_address_3 ansible_ssh_user='username'  # non-root user
   ```

   Configure the reference operation for key authentication.Please pay attention to the risks during the use and storage of SSH keys and key passwords, especially when the keys are not encrypted. Users should configure them according to the security policies of their organization, including but not limited to software version, password complexity requirements, security configuration (protocol, encryption suite, key length, etc,especially the configuration under /etc/ssh and ~/.ssh)
   ```bash
   ssh-keygen -t rsa -b 3072   # Log in to the management node and generate the SSH Key. For security reasons, it is recommended that the user Enter the key password at the "Enter passphrase" step, and ensure that the password complexity is reasonable. It is recommended to set the umask to 0077 before executing this command and to restore the original umask after executing it.
   ssh-copy-id -i ~/.ssh/id_rsa.pub <user>@<ip>   # Copy the public key of the management node to the machines of all nodes, and replace <user>@<ip> with the account and ip of the corresponding node to be copied to.
   ssh <user>@<ip>   # Verify that it is possible to log on to the remote node, and replace <user>@<ip> with the account and IP of the corresponding node to be logged in. After verifying that the login is OK, run the 'exit' command to exit the SSH connection.
   ```

   Note: Please be aware of the risks involved in the use and storage of SSH keys.

2. Set up the SSH agent to manage the SSH key to avoid entering the key password during the bulk installation of the tool. The following are the guidelines for setting up an SSH agent:
   ```bash
   ssh-agent bash   # Start the ssh-agent bash process
   ssh-add ~/.ssh/id_rsa         # Add a private key to the ssh-agent
   ```

3. Run the `./install.sh --check` command to test the connectivity of the devices where the packages to be installed. Ensure that all devices can be properly connected. If a device fails to be connected, check whether the network connection of the device is normal and whether sshd is enabled.

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

Select corresponding parameters to install the software. The command likes `./install.sh [options]`.
The following table describes the parameters. You can run the `./install.sh --help` command to view the options of the following parameters.

| Parameter                         | Description                                                                                                                                                                    |
|:--------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| --help  -h                        | Queries help information.                                                                                                                                                      |
| --check                           | Check the environment to ensure that the control machine has installed Python 3.7.5, Ansible and other components, and check the connectivity with the device to be installed. |
| --clean                           | Clean the Resources directory under the user's home directory for the device to be installed.                                                                                  |
| --nocopy                          | Forbids resources copying during batch installation.                                                                                                                           |
| --force_upgrade_npu               | Can force upgrade NPU when not all devices have exception                                         |
| --verbose                           | Print verbose.                                                                                                                                                            |
| --output-file=<output_file>       | Set the output format of the command execution. The available parameters can be viewed with the command "ansible -doc-t callback-l".                                           |
| --stdout_callback=<callback_name> | Performs debugging.                                                                                                                                                            |
| --install=<package_name>          | Specifies the software to be installed. If **--install=npu** is specified, the driver and firmware are installed.                                                              |
| --install-scene=<scene_name>      | Specifies the scenario for installation. For details about the installation scenarios, see <a href="#scene">Installation Scenarios</a>.                                        |
| --patch=<package_name>            | Patching specific package                                                                  |
| --patch-rollback=<package_name>   | Rollback specific package                                                                  |
| --test=<target>                   | Checks whether the specified component works properly.                                                                                                                         |

## <a name="download_parameter">Linux Download Parameter Description</a>

| Parameter           | Description                                    |
|:------------------- | ---------------------------------------------- |
| `--os-list=<OS1>,<OS2>`| set specific os softwares to download          |
| `--download=<PK1>,<PK2>==<Version>`| download specific components. such as MindSpore、MindStudio、CANN |

This tool downloads python component packages by default. If the system specified by --os-list has only aarch64 architecture, only python component packages required by aarch64 architecture system will be downloaded. If the system specified by --os-list has only x86_64 architecture, only python component packages required by x86_64 architecture are downloaded. When --os-list is empty or the specified system has both aarch64 and x86_64 architectures, the Python component packages required for both architectures are downloaded. Same logic as above to download CANN package for aarch64 or x86_64 architectures.

| optional components| version 1 | version 2 | version 3 | version 4 |
|:------------------ | --------  | --------  | --------  | -------- |
| MindStudio         |  2.0.0    |  3.0.1    |  3.0.2    |  3.0.3   |
| MindSpore          |  1.1.1    |  1.2.1    |  1.3.0    |  1.5.0    |
| CANN               |  20.3.0   |  5.0.1.spc103|  5.0.2.1 |  5.0.3.1 |

Only one version of MindSpore or MindStudio that matches CANN package version should exist in the Resources directory during installation, as shown above. `./start_download.sh --download=<PK1>,<PK2>==<Version>`, when `<Version>` is missing, `<PK>` is the latest. `--download=MindSpore`, --os-list specifies the corresponding OS, please refer to the official website of [mindspore](https://mindspore.cn/versions) for some instructions. MindStudio installation please refer to the [install MindStudio](https://gitee.com/ascend/ascend-deployer/blob/master/docs/Install_MindStudio.md).

## <a name="scene">Installation Scenarios</a>

The offline installation tool provides several basic installation scenarios.

| Installation Scenario | Installed Components                                                          | Description                                            |
| --------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------ |
| auto        | all                                                              | All software packages that can be found are installed |
| vmhost      | sys_pkg、npu、toolbox                                            | VM host scene                                         |
| edge        | sys_pkg、atlasedge、ha                                           | Install MindX middleware, HA                          |
| offline_dev | sys_pkg、python、npu、toolkit                                  | Offline development scene                            |
| offline_run | sys_pkg、python、npu、nnrt                                     | Offline run scene                                    |
| mindspore   | sys_pkg、python、npu、toolkit、mindspore                       | mindspore scene                                      |
| tensorflow_dev | sys_pkg、python、npu、toolkit、tfplugin、tensorflow         | tensorflow development scene                         |
| tensorflow_run | sys_pkg、python、npu、nnae、tfplugin、tensorflow            | tensorflow run scene                                 | 
| pytorch_dev | sys_pkg、python、npu、toolkit、pytorch                         | pytorch development scene                            |
| pytorch_run | sys_pkg、python、npu、nnae、pytorch                            | pytorch run scene                                    |


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

## <a name="patch">Install and rollback cann patch package</a>
The ascend deployer tool supports cann cold patch installation and fallback.
1. Cann patch packages do not support online downloading using the ascend deployer tool. Users need to obtain the required cann patch packages by themselves and place them in the ascend deployer / resources / patch (if there is no patch directory, users should create it by themselves). Note that the cann package corresponding to the patch package in the ascend deployer / resources directory should be deleted before installation.
2. The execution commands for installing and fallback cann cold patch are as follows:
   - Install cann cold patch (take nnae and tfplugin packages as examples): `./install.sh --patch=nnae,tfplugin`
   - Fallback cann cold patch (take nnae and tfplugin packages as examples): `./install.sh --patch-rollback=nnae,tfplugin`
3. The relevant constraints on cann cold patch are as follows:
   - The patch can only support the upgrade of the corresponding baseline version or related patch version.
   - For patches based on the same baseline version, ensure that the patch version installed later is greater than the patch version installed earlier.
   - The patch only supports fallback once.
## <a name="config">Configuration Description</a>

### <a name="proxy_configuration">Proxy Configuration</a>

If you want to use an proxy, configure the proxy in an environment variable. Users need to pay attention to the security of the proxy.This tool validates HTTPS certificates by default, if a certificate error occurs during the download process, it may be that the proxy server has a security mechanism for certificate replacement, so you need to install the proxy server certificate first.

1. Configure the agent in the environment variable as follows

   ```
   # Configure environment variables.
   export http_proxy="http://user:password@proxyserverip:port"
   export https_proxy="http://user:password@proxyserverip:port"
   ```

   Where "user" is the user's internal network name, "password" is the user's password (special characters need to be escaped), "proxyserverip" is the IP address of the proxyserver, and "port" is the port. The principle of configuring proxies in Windows environment variables is the same as that in Linux. For details, see official instructions.

2. Configure the agent in the downloader/config.ini file as follows:

   ```
   [proxy]
   verify=true         # Whether to verify the HTTPS certificate. If it is closed,Please be aware of the security risks
   ```

### Windows Download Configuration

You can configure and modify the download parameters in the **downloader/config.ini** file to download the required OS components on windows. It is not recommended to modify the configuration file directly. It is recommended to run start_download_ui.bat and use the UI interface to check the required components

```
[download]
os_list=CentOS_7.6_aarch64, CentOS_7.6_x86_64, CentOS_8.2_aarch64, CentOS_8.2_x86_64, Ubuntu_18.04_aarch64, Ubuntu_18.04_x86_64 ...          # OS information of the environment to be deployed.
[software]
pkg_list=CANN_5.0.3.1,MindStudio_3.0.3  # CANN or MindStudio to be deployed.
```

### <a name="sourceconfig">Source Configuration</a>

The offline installation tool provides the source configuration file. Replace it as required.

1. Python source configuration. Configure the Python source in the **downloader/config.ini** file.The Huawei source is used by default.

  ```
  [pypi]
  index_url=https://repo.huaweicloud.com/repository/pypi/simple
  ```
2. OS source configuration. OS source configuration file: **downloader/config/*{os}\__{version}\__{arch}*/source.*xxx***
  Using CentOS 7.6 AArch64 as an example, the content of the source configuration file **downloader/config/CentOS_7.6_aarch64/source.repo** is as follows. This indicates that both Base and EPEL sources are enabled from which system components will be queried and downloaded.Huawei source is used by default.It can be modified according to business requirements and installation requirements to ensure that its source meets the security / vulnerability repair requirements of the organization.If you modify, select a safe and reliable source and test whether the download and installation behavior is normal, otherwise it may cause incomplete download of the component or abnormal installation.Deleting the source may result in an incomplete download of the component.

  ```
  [base]
  baseurl=https://mirrors.huaweicloud.com/centos-altarch/7/os/aarch64
  [epel]
  baseurl=https://mirrors.huaweicloud.com/epel/7/aarch64
  ```

3. When downloading the centos-like system component, you need to parse the XML files in the system source. You are advised to install the defusedxml component in python3 to improve the security against potential XML vulnerability attacks.


## <a name="url">Public Web Site URL</a>
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
## <a name='sha256sum'>Sha256sum verification</a>
| sha256sum                                                        | Version of the ascend-deployer |
| ---------------------------------------------------------------- | ------------------------------ |
| 22f7e10677658e7c3d223b32f73786c765e85cf6f66440bf620c3e4275f11e7f | ascend-deployer-2.0.4.B093.zip | 

## <a name="faq">FAQ</a>
1. Q: The first time you execute './install.sh --check 'or any other installation command, the system dependencies and Python 3.7.5 will be installed automatically. If the installation process is interrupted unintentionally, the second time you execute the command, the RPM and DPKG tools may be locked, or Python 3.7.5 functionality may be missing.

- A: Release the RPM/DPKG tool lock, delete the Python 3.7.5 installation directory, and install again using the tool.(Python 3.7.5 installation directory may refer to <a href="#set_env_var"> to configure the environment variable </a>)

2. Q: Non-root users are prompted for the sudo password when installing the pre-5.0.1 Toolkit.

- A: For security reasons, this tool does not require non-root users to have sudo privileges, so it does not support non-root users to install the toolkit prior to 5.0.1.

3. Q: What is the mechanism of crl file update and signature verification? Whether the crl file can be updated independently?

- A: There are two methods for crl file update and signature verification. The tool at toolbox/latest/Ascend-DMI/bin/ascend-cert is preferred. If this tool does not exist in the environment, openssl is preferred. To be compatible with old and new software package signature formats, the tool uses two sets of certificates. The tool compares the validity time of the crl file in the installation package with that of the local crl file, and uses the latest crl file to check whether the certificate is revoked. For the root user, the system of local crl files for `/etc/hwsipcrl/ascendsip.crl(or ascendsip_g2.crl)`, for non-root users, This file is `~/.local/hwsipcrl/ascendsip.crl(or ascendsip_g2.crl)`. If the local crl file does not exist or takes effect earlier than the crl file in the installation package, the local crl file is replaced by the crl file in the installation package. The tools/update_crl.sh supports independent crl file update, Run `bash update_crl.sh <crl_file>` command to update an independent crl file, `<crl_file>` is the path of the crl file uploaded by the user.

3. Q: What is the reason why "certificate verify failed" appears when downloading some components?

- A: The tool verifies the HTTPS certificate by default. The preceding error may be caused by an exception of the proxy server certificate. Contact the system administrator. The verification function can be configured in the downloader/config.ini file. For details, see <a href="#proxy_configuration">Proxy Configuration</a>。
