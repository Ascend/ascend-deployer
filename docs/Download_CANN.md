## 下载

```bash
./start_download.sh --download=CANN
```

需满足以下条件：

1. 用户环境需为Windows系统或Ubuntu系统，其它的Linux系统未经验证，不建议使用。注意本工具的存放路径中不要包含中文。

2. 确保能正常登录[华为企业业务网站](https://support.huawei.com)，并提前申请相应软件包(驱动与固件包、CANN软件包以及Toolbox软件包)的下载权限，可通过点击ascend-deployer/downloader/software/CANN_<version>.json内的url链接跳转申请。

3. 系统中已安装并可通过直接执行`firefox`命令成功运行firefox浏览器。Windows系统下可从[firefox官网](https://www.mozilla.org/en-US/firefox/all/#product-desktop-release)下载对应的安装包后安装该软件，并把安装路径加入到Path环境变量中；Ubuntu系统下可使用系统自带的包管理器进行安装(`apt install firefox`)。

4. 获取firefox浏览器驱动geckodriver。

   4.1 对于Windows系统和Ubuntu x86_64系统，可从[geckodriver官网](https://github.com/mozilla/geckodriver/releases)获取。Windows系统下载geckodriver-vx.x.x-win64.zip并解压得到geckodriver.exe，Ubuntu x86_64系统下载geckodriver-vx.x.x-linux64.tar.gz并解压得到geckodriver。

   4.2 对于Ubuntu aarch64系统，由于geckodriver官网未提供arm版的geckodriver，但镜像源中有提供firefox-geckodriver软件包，可参考如下操作获取软件包并解压得到geckodriver。
   ```bash
   wget https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/pool/main/f/firefox/firefox-geckodriver_92.0+build3-0ubuntu0.18.04.1_arm64.deb   # 下载firefox-geckodriver软件包，也可使用"apt download firefox-geckodriver"命令下载
   dpkg -x firefox-geckodriver_92.0+build3-0ubuntu0.18.04.1_arm64.deb .   # 把软件包解压到当前目录，解压后会生成一个"usr"目录
   ls usr/bin/geckodriver   # 查看生成的usr/bin/geckodriver文件，得到geckodriver后清理这些临时文件
   ```

   4.3 请将geckodriver.exe(或geckodriver)文件放置于ascend-deployer工具的同级目录下。安全起见，Linux系统下请确保geckodriver属主为当前用户且权限为500，Windows系统下请确保其他用户对geckodriver.exe无读写权限。

5. 参考README中“下载操作”步骤，确保系统中python3命令可用，然后执行`pip3 install selenium`安装selenium。若无pip3工具请先自行安装。

6. Linux系统下，安全起见，需要控制程序的开启端口和文件权限。用户需执行如下命令对selenium打patch。若无patch工具请先自行安装。
```bash
patch <系统python3的第三方包目录>/selenium/webdriver/firefox/webdriver.py < <ascend-deployer目录>/patch/selenium_firefox.patch
patch <系统python3的第三方包目录>/selenium/webdriver/firefox/firefox_profile.py < <ascend-deployer目录>/patch/selenium_firefox_profile.patch
```

7. Linux系统下，确保X11功能可用和相关配置正确，并设置DISPLAY环境变量
```bash
export DISPLAY=$(echo $SSH_CLIENT |awk ' {print $1 }'):0.0
```

8. 测试：执行`firefox`命令运行firefox浏览器，并在地址栏输入网址["https://support.huawei.com"]，能正常访问。如无法访问，请检查网络或代理是否可用。


## 说明

1. 本工具会把软件包及.asc数字签名同时下载下来，用户可从下载页面处获取数字签名验证工具对软件包进行人工验签。