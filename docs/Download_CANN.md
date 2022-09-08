## 下载

```bash
./start_download.sh --download=CANN
```

需满足以下条件：

1. 用户环境需为Windows系统或Ubuntu 18.04.1/5系统，其它的Linux系统未经验证，不建议使用。注意本工具的存放路径中不要包含中文。

2. 确保能正常登录[华为企业业务网站](https://support.huawei.com)，并提前申请相应软件包(驱动与固件包、CANN软件包以及Toolbox软件包)的下载权限，可通过点击ascend-deployer/downloader/software/CANN_`<version>`.json内的url链接跳转申请。

3. 系统中已安装并可通过直接执行`firefox`命令成功运行firefox浏览器。Windows系统下可从[firefox官网](https://www.mozilla.org/en-US/firefox/all/#product-desktop-release)下载对应的安装包后安装该软件，并把安装路径加入到Path环境变量中；Ubuntu系统下可使用系统自带的包管理器进行安装(`apt install firefox`)。

4. 获取firefox浏览器驱动geckodriver。

   4.1 对于Windows系统和Ubuntu x86_64系统，可从[geckodriver官网](https://github.com/mozilla/geckodriver/releases)获取。Windows系统下载geckodriver-vx.x.x-win64.zip并解压得到geckodriver.exe，Ubuntu x86_64系统下载geckodriver-vx.x.x-linux64.tar.gz并解压得到geckodriver。

   4.2 对于Ubuntu aarch64系统，由于geckodriver官网未提供arm版的geckodriver，可从[镜像源网站](https://mirrors.bfsu.edu.cn/ubuntu-ports/pool/main/f/firefox)下载firefox-geckodriver_`<version>`ubuntu0.18.04.1_arm64.deb软件包，参考如下操作解压得到geckodriver。
   ```bash
   dpkg -x firefox-geckodriver_<version>ubuntu0.18.04.1_arm64.deb .   # 把软件包解压到当前目录，解压后会生成一个"usr"目录
   ls usr/bin/geckodriver   # 查看生成的usr/bin/geckodriver文件，得到geckodriver后清理这些临时文件
   ```

   4.3 请将geckodriver.exe(或geckodriver)文件放置于ascend-deployer工具的同级目录下。安全起见，Linux系统下请确保geckodriver属主为当前用户且权限为500，Windows系统下请确保其他用户对geckodriver.exe无读写权限。

5. 参考README中“下载操作”步骤，确保系统中python3命令可用，然后执行`pip3 install selenium`安装selenium。若无pip3工具请先自行安装，用户参考patch自己进行修改。

6. Linux系统下，安全起见，需要控制程序的开启端口和文件权限。用户需执行如下命令对selenium打patch。若无patch工具请先自行安装。
```bash
patch <系统python3的第三方包目录>/selenium/webdriver/firefox/webdriver.py < <ascend-deployer目录>/patch/selenium_firefox.patch
patch <系统python3的第三方包目录>/selenium/webdriver/firefox/firefox_profile.py < <ascend-deployer目录>/patch/selenium_firefox_profile.patch
```

7. 测试：执行`firefox`命令运行firefox浏览器，并在地址栏输入网址["https://support.huawei.com"]，能正常访问。如无法访问，请检查网络或代理是否可用。
8. 如果提示下载失败，说明网络有问题，请多尝试几次下载。


## 说明

1. 本工具会把软件包及.asc数字签名同时下载下来，用户可从下载页面处获取数字签名验证工具对软件包进行人工验签。
2. 这个功能要在有GUI界面的linux服务器上直接运行。
3. 请确保下载软件包时网络通畅。
4. 如果下载失败，请确认ascend-deployer/downloader/software/CANN_`<version>`.json内的URL可以正常访问，如果出现资源不存在或已删除，请访问网址["https://support.huawei.com/enterprise/zh/ascend-computing/ascend-data-center-solution-pid-251167910/software"]查看版本配套关系，参考ascend-deployer/downloader/software/CANN_`<version>`.json的格式替换失效的filename和url。