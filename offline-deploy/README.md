- [功能简介](#功能简介)
- [环境依赖](#环境依赖)
  - [运行环境要求](#运行环境要求)
  - [软件支持列表](#软件支持列表)
  - [硬件支持列表](#硬件支持列表)
- [安装场景](#安装场景)
- [安装步骤](#安装步骤)
  - [步骤1：准备登录各台服务器的账号](#步骤1准备登录各台服务器的账号)
  - [步骤2：下载离线软件包](#步骤2下载离线软件包)
  - [步骤3：配置安装信息](#步骤3配置安装信息)
  - [步骤4：执行安装](#步骤4执行安装)
- [安装后状态查看](#安装后状态查看)
- [MEF-Center离线安装场景](#mef-center离线安装场景)
- [组件升级](#组件升级)
- [安装脚本对系统的修改](#安装脚本对系统的修改)
- [常用操作](#常用操作)
- [常见问题](#常见问题)
  - [常见安装问题](#常见安装问题)
  - [其他问题](#其他问题)
- [免责声明](#免责声明)
- [历史版本](#历史版本)
- [CHANGELOG](#changelog)

# 功能简介
本软件使用基于Ansible的脚本， 进行批量安装。 简要来说， 具有如下功能：

1. MindX DL全栈安装, 包括集群调度组件、以及运行集群调度组件依赖的软件（Docker、kubernetes）（对应的SCENE_NUM为1）。
2. K8s集群扩容 (纳管工作节点, 对应的SCENE_NUM为2和3， 具体区别请参考[安装场景](#安装场景)）。
3. 纯k8s集群安装 (目前仅用于MEF-Center场景的前置k8s安装, 对应的SCENE_NUM为4）。
4. MEF-Center场景的安装(具体请参考[MEF-Center离线安装场景](#mef-center离线安装场景) )。
5. 配置HCCN网络(具体请参考[常用操作6](#常用操作)).
6. K8s集群状态查询(具体请参考[常用操作7](#常用操作)).

不同的场景应安装不同的组件，具体请参考[安装场景](#安装场景)中的说明， 并通过设置配置文件`inventory_file`中的SCENE_NUM参数生效。 安装前请阅读[环境依赖](#环境依赖)确认环境符合预期；

请按照[安装步骤](#安装步骤)逐步执行。

# 环境依赖
## 运行环境要求

 1. 存放镜像目录的磁盘空间利用率**高于85%**会触发Kubelet的镜像垃圾回收机制，**将导致服务不可用**。请确保每台服务器上存放镜像的目录有足够的磁盘空间，建议≥**1 TB**。
 2. **执行安装K8s和DL组件命令前，需要确认服务器上已经安装好昇腾NPU的驱动和固件**
 3. 如果计划执行集群训练, 需要执行[配置训练服务器NPU的device IP](https://www.hiascend.com/document/detail/zh/canncommercial/60RC1/envdeployment/instg/instg_000039.html), 或在集群安装完毕后, 按[常用操作6](#常用操作)完成device IP配置操作。
 3. 执行安装脚本前，保证安装Kubernetes的服务器的时间一致，可参考[常用操作1](#常用操作)快速设置各节点时间。
 4. 所有节点需要**已安装Python2.7以上**
 5. 安装部署脚本会在节点创建一个uid和gid为9000的用户hwMindX，请保证各节点上该uid和gid未被占用。
 6. 如果用户需要使用Harbor，请保证各节点（包括执行机）能够登录Harbor。
 7. 如果用户已有K8s集群，则需要在master节点的/root/.kube/config文件中放置能够操作K8s资源的授权内容。
 8. 不支持多操作系统混合部署。
 9. 请保证节点的IP与K8s默认集群网段（192.168.0.0/16）没有冲突，如果冲突，请用户修改inventory_file中的`POD_NETWORK_CIRD`参数为其他私有网段，如：10.0.0.0/16。
 10. 如果用户已经安装了Kubernetes，其版本不能高于1.21
 11. 安装脚本支持在下表的操作系统运行，脚本支持在如下操作系统上安装MindX DL的集群调度组件、Docker、Kubernetes软件, 可将安装脚本的执行放到待安装节点(特别是master节点)其中之一上执行, 并在安装完成后删除安装脚本, 安装过程中使用的密钥等。

<table>
  <thead>
    <tr>
      <th align="left">操作系统</th>
      <th align="left">版本</th>
      <th align="left">架构</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2">Ubuntu </td>
      <td rowspan="2">18.04、20.04</td>
      <td>aarch64</td>
    </tr>
    <tr>
      <td>x86_64</td>
    </tr>
    <tr>
      <td rowspan="2">OpenEuler</td>
      <td rowspan="2">20.03LTS、22.03LTS</td>
      <td>aarch64</td>
    </tr>
    <tr>
      <td>x86_64</td>
    </tr>
    <tr>
      <td rowspan="2">CentOS</td>
      <td rowspan="2">7.6</td>
      <td>aarch64</td>
    </tr>
    <tr>
      <td>x86_64</td>
    </tr>
  </tbody>
</table>

## 软件支持列表
<table>
<thead>
  <tr>
    <th align="left">软件名</th>
    <th align="left">软件版本</th>
    <th align="left">架构</th>
    <th align="left">说明</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td rowspan="2">Docker</td>
    <td rowspan="2">18.09</td>
    <td>aarch64</td>
    <td rowspan="2">容器运行时</td>
  </tr>
  <tr>
    <td>x86_64</td>
  </tr>
  <tr>
    <td rowspan="2">Kubernetes</td>
    <td rowspan="2">1.19.16</td>
    <td>aarch64</td>
    <td rowspan="2">容器编排工具</td>
  </tr>
  <tr>
    <td>x86_64</td>
  </tr>
  <tr>
    <td>Ascend Device Plugin</td>
    <td rowspan="6">3.0.0</td>
    <td rowspan="6"><li>aarch64</li><br /><li>x86_64</li></td>
    <td rowspan="6">集群调度组件</td>
  </tr>
  <tr>
    <td>Volcano</td>
  </tr>
  <tr>
    <td>NodeD</td>
  </tr>
  <tr>
    <td>HCCL-Controller</td>
  </tr>
  <tr>
    <td>NPU-Exporter</td>
  </tr>
  <tr>
    <td>Ascend Docker Runtime</td>
  </tr>
</tbody>
</table>

## 硬件支持列表

| 服务器类型 |
|:---------------|
| Atlas 800 训练服务器（型号：9000/9010） |
| Atlas 800 推理服务器（型号：3000/3010） |
| 服务器（插Atlas 300T 训练卡） |
| 服务器（插Atlas 300I 推理卡） |
| 服务器（插Atlas 300I Pro 推理卡） |
| 服务器（插Atlas 300I Duo 推理卡） |
| 服务器（插Atlas 300V Pro 视频解析卡） |
| 服务器（插Atlas 300V 训练解析卡） |



# 安装场景
可选组件默认不安装
<table>
<thead>
  <tr>
    <th align="left">场景</th>
    <th align="left">安装组件</th>
    <th align="left">说明</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td rowspan="8">MindX DL全栈安装(集群调度场景, 全栈）</td>
    <td rowspan="8"><li>Docker</li><br /><li>Kubernetes</li><br /><li>Ascend Docker Runtime</li><br /><li>Ascend Device Plugin</li><br /><li>Volcano</li><br /><li>NodeD</li><br /><li>HCCL-Controller</li><br /><li>NPU-Exporter</li></td>
    <td rowspan="8">该场景适用于你有一台或者多台NPU服务器，需要使用Kubernetes管理。使用该场景会完成NPU服务器的Docker、Kubernetes和NPU集群调度组件的安装。在inventory_file中对应场景一</td>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
    <td rowspan="6">K8s集群扩容(集群调度场景)</td>
    <td rowspan="6"><li>Ascend Docker Runtime</li><br /><li>Ascend Device Plugin</li><br /><li>Volcano</li><br /><li>NodeD(可选)</li><br /><li>HCCL-Controller(可选)</li><br /><li>NPU-Exporter(可选)</li></td>
    <td rowspan="6">该场景适用于你已经有一个部署好的Kubernetes集群，需要纳管新的NPU服务器。使用该场景时，需要在已有的Kubernetes集群的master节点部署NPU管理组件，新接入的NPU机器上部署worker节点的NPU管理组件。在inventory_file中对应场景二</td>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
    <td rowspan="3">K8s集群扩容(设备纳管场景)</td>
    <td rowspan="3"><li>Ascend Docker Runtime</li><br /><li>Ascend Device Plugin</li><br /><li>NPU-Exporter(可选)</li></td>
    <td rowspan="3">该场景适用于你已经有一个部署好的Kubernetes集群，希望使用自己的调度器部署NPU任务。使用该场景时，需要在新接入的NPU服务器上部署worker节点的NPU管理组件。在inventory_file中对应场景三</td>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
  <tr>
    <td rowspan="3">MEF-Center离线安装场景</td>
    <td rowspan="4"><li>Docker</li><br /><li>Kubernetes</li><br /><li>KubeEdge</li><br /><li>MEF-Center</li></td>
    <td rowspan="3">该场景的MEF-Center支持部署在边缘设备或者服务器上，需要确保设备的操作系统为ubuntu和OpenEuler，其中ubuntu版本为20.04，OpenEuler为22.03。在inventory_file中对应场景四，相关操作请查看MEF_README</td>
  </tr>
  <tr>
  </tr>
  <tr>
  </tr>
</tbody>
</table>



# 安装步骤

## 步骤1：准备登录各台服务器的账号

安装部署脚本需要通过ssh登录各台服务器执行命令，支持的ssh登录方式有如下两种：
- 使用ssh免密的方式登录，配置方式可参考[常用操作5](#常用操作)。
- 使用ssh账号、密码登录的方式, 这种方式将把密码直接写入inventory_file文件, 具体方式请参考[步骤3：配置安装信息](#步骤3配置安装信息)

支持ssh登录的账号有如下两种：
- root账号
- 配置了sudo权限的普通账号


## 步骤2：下载离线软件包
选择其中一种方式准备离线安装包, 请确保包下载完整, 注意网络波动.

 - 在Window或其他机器上下载[历史版本](#历史版本)中的resources.zip包，将离线包上传到执行安装命令服务器的/root目录下，然后解压。
 - 登录执行安装命令服务器，将下面`wget`命令后的url替换成[历史版本](#历史版本)中所需版本的resources.zip的地址，然后执行如下命令
```bash
# resources.zip解压出的内容必须放置在家目录下
cd
wget https://ascend-repo-modelzoo.obs.cn-east-2.myhuaweicloud.com/MindXDL/3.0.0/resources.zip
```

然后执行解压操作
```bash
cd
mv resources ~/resources.$(date +%s) 2>/dev/null
unzip resources.zip
mv ~/offline-deploy ~/offline-deploy.$(date +%s) 2>/dev/null
cp resources/ascend-deployer/offline-deploy ~/offline-deploy -a

```
在部分os上， 默认没有unzip组件， 用户可以提前下载 [arm版unzip](https://ascend-repo-modelzoo.obs.cn-east-2.myhuaweicloud.com/MindXDL/5.0.RC1/aarch64/unzip) 或者 [x86_64版unzip](https://ascend-repo-modelzoo.obs.cn-east-2.myhuaweicloud.com/MindXDL/5.0.RC1/x86_64/unzip) 并上传到执行安装命令服务器上的家目录， 并采用如下指令完成相应resource包的解压
```
cd
mv resources ~/resources.$(date +%s) 2>/dev/null
chmod 700 unzip 
mkdir -p resources && ./unzip resources.zip .
mv ~/offline-deploy ~/offline-deploy.$(date +%s) 2>/dev/null
cp resources/ascend-deployer/offline-deploy ~/offline-deploy -a

````

## 步骤3：配置安装信息
cla
修改配置文件参数，用户可根据配置文件注释自行设置，**请勿修改配置文件中的结构**。特别注意配置SCENE_NUM和master/worker下的节点配置, 建议分别以master/worker其下的示例一为模板, 逐项填写; 如果采用提供非免密登陆方式, 用户还需要增加填写`ansible_ssh_pass`等项和相应的密码. 

配置项的具体含义请参考`inventory_file`文件中的注释;

```bash
cd ~/offline-deploy
vi inventory_file

```

## 步骤4：执行安装

运行如下指令进行安装, 请提前将指令中的示例时间设置为当前时间:

```bash
cd ~/offline-deploy
ansible -i inventory_file all -m shell -b -a "date -s '2022-06-01 08:00:00'; hwclock -w"
bash scripts/run_install.sh

```
如果安装过程出现错误，请根据回显中的信息进行排查处理，也可查看[常见问题](#常见问题)进行处理.

说明：
- NPU-Exporter可提供HTTPS或HTTP服务，使用安装脚本仅支持HTTP服务，如对安全性需求较高可参考《MindX DL用户指南》中安装NPU-Exporter的章节，手动部署提供HTTPS服务的NPU-Exporter，升级时仅支持使用HTTP部署的方式。
- 使用安装脚本部署的HCCL-Controller、NodeD、Ascend Device Plugin均使用ServiceAccount授权方式与K8s进行通信，如需使用更加安全的方式与K8s进行通信如通过证书导入工具导入KubeConfig文件，则请参考《MindX DL用户指南》中的“导入证书和KubeConfig”章节，升级时仅支持使用ServiceAccount授权的方式。
- 用户也可以通过在`~/offline-deploy`目录下执行 `scripts/install_ansible.sh`(安装ansible), `scripts/install_npu.sh`(安装驱动), `scripts/install.sh`(按场景安装k8s和DL组件) 分步安装;
- 安装kubeedge须在执行完`bash scripts/run_install.sh`操作后, 根据[MEF-Center离线安装场景](#mef-center离线安装场景)离线安装MEF-Center。注意：MEF相关安装包Ascend-mindxedge-mefcenter_x86/arm64.zip，请到华为昇腾社区上获取.

  
# 安装后状态查看

使用命令`kubectl get nodes`检查kubernetes节点，如下所示表示正常

```bash
NAME             STATUS   ROLES    AGE   VERSION
master           Ready    master   60s   v1.19.16
worker-1         Ready    worker   60s   v1.19.16
```

使用命令`kubectl get pods --all-namespaces`检查kubernetes pods，如下所示表示正常

```
   NAMESPACE        NAME                                      READY   STATUS             RESTARTS   AGE
   kube-system      ascend-device-plugin-daemonset-910-lq     1/1     Running            0          21h
   kube-system      calico-kube-controllers-68c855c64-4fn2k   1/1     Running            1          21h
   kube-system      calico-node-4zfjp                         1/1     Running            0          21h
   kube-system      calico-node-jsdws                         1/1     Running            0          21h
   kube-system      coredns-f9fd979d6-84xd2                   1/1     Running            0          21h
   kube-system      coredns-f9fd979d6-8fld7                   1/1     Running            0          21h
   kube-system      etcd-ubuntu-1                             1/1     Running            0          21h
   kube-system      kube-apiserver-ubuntu-1                   1/1     Running            0          21h
   kube-system      kube-controller-manager-ubuntu-1          1/1     Running            8          21h
   kube-system      kube-proxy-6zr9j                          1/1     Running            0          21h
   kube-system      kube-proxy-w9lw9                          1/1     Running            0          21h
   kube-system      kube-scheduler-ubuntu-1                   1/1     Running            6          21h
   mindx-dl         hccl-controller-8ff6fd684-9pgxm           1/1     Running            0          19h
   mindx-dl         noded-c2h7r                               1/1     Running            0          19h
   npu-exporter     npu-exporter-7kt25                        1/1     Running            0          19h
   volcano-system   volcano-controllers-56cbbb9c6-9trf7       1/1     Running            0          19h
   volcano-system   volcano-scheduler-66f75bf89f-94jkx        1/1     Running            0          19h
```

用户也可通过集群状态报告[常用操作7](#常用操作)确认安装结果;

# MEF-Center离线安装场景

前置条件:

用户需要确保已有能正常运行的K8s系统 (如在相应服务器上完成了场景1或者4的所有[安装步骤](#安装步骤));

## 步骤1：配置安装节点信息
用户需配置`~/offline-deploy/inventory_file`, 将计划安装MEF-Center的节点设置在mef项下, 建议按mef的样例1为模板, 逐项填入; 

并且, 用户需选择如下两种方式之一配置登陆:

- 使用ssh免密的方式登录，配置方式可参考[常用操作5](#常用操作)。
- 使用ssh账号、密码登录的方式, 这种方式将把密码直接写入inventory_file文件, 具体方式请参考[步骤3：配置安装信息](#步骤3配置安装信息)

## 步骤2：导入MEF-Center软件包
  请从昇腾社区提前获取 `Ascend-mindxedge-mefcenter_x86_64.zip` 或 `Ascend-mindxedge-mefcenter_aarch64.zip`, 并放入用户家目录; 然后执行:
```bash
  cd
  cp Ascend-mindxedge-mefcenter_x86_64.zip ~/resources/mef
  cp Ascend-mindxedge-mefcenter_aarch64.zip ~/resources/mef
  
   ```

## 步骤3：安装MEF-Center
注意：当前MEF-Center安装脚本已集成至`install_kubeedge.sh`中，运行该脚本会同步安装MEF-Center
```
cd ~/offline-deploy/scripts
bash install_kubeedge.sh              # 安装kubeedge，MEF-Center会在安装kubeedge时同步安装

```

用户也可以采用 `cd ~/offline-deploy/scripts; bash install_kubeedge.sh --uninstall` 来卸载kubeedge.

## 确认安装成功
使用命令`kubectl get pods --all-namespaces`检查kubernetes pods，如下所示表示正常

```
NAMESPACE        NAME                                      READY   STATUS             RESTARTS   AGE
kube-system      calico-kube-controllers-68c855c64-4fn2k   1/1     Running            1          21h
kube-system      calico-node-4zfjp                         1/1     Running            0          21h
kube-system      calico-node-jsdws                         1/1     Running            0          21h
kube-system      coredns-f9fd979d6-84xd2                   1/1     Running            0          21h
kube-system      coredns-f9fd979d6-8fld7                   1/1     Running            0          21h
kube-system      etcd-ubuntu-1                             1/1     Running            0          21h
kube-system      kube-apiserver-ubuntu-1                   1/1     Running            0          21h
kube-system      kube-controller-manager-ubuntu-1          1/1     Running            8          21h
kube-system      kube-proxy-6zr9j                          1/1     Running            0          21h
kube-system      kube-proxy-w9lw9                          1/1     Running            0          21h
kube-system      kube-scheduler-ubuntu-1                   1/1     Running            6          21h
```


# 组件升级
目前**仅支持MindX DL集群调度组件升级**，**不支持**Docker和Kubernetes的升级，并且升级时会按照之前`/root/offline-deploy/inventory_file`中配置的**节点**、**节点类型**、**场景包含的组件**进行升级。

升级会先卸载旧的MindX DL集群调度组件再重新安装，请选择空闲时间进行，避免影响训练或者推理任务。同时，升级时请一次性升级安装了MindX DL集群调度组件中的某个组件的所有节点，避免部分组件未升级影响正常功能。

升级MindX DL集群调度组件时需要获取[历史版本](#历史版本)中的resources.zip包，上传到脚本执行节点**非/root目录**(如/root/upgrade)下，执行如下命令先备份旧的resources包中的内容。
```
# 解压新的resources
cd /root/upgrade
unzip resources.zip

# 备份旧的resources解压出的内容
cd /root/upgrade/offline-deploy
bash scripts/backup.sh
```
然后执行更新命令，如果在更新过程出现错误，请根据打印信息处理错误，然后再次执行下面的命令进行升级（不需要再执行上面的备份命令，除非更换了resources包）。
```
# 如需修改inventory_file，可在执行下一条命令之前自行修改/root/offline-deploy/inventory_file
cd /root/offline-deploy
bash scripts/upgrade.sh
```


# 安装脚本对系统的修改

 1. 如果安装时选择了安装Kubernetes，脚本会对系统进行如下修改
     1. 关闭swap分区
     2. 将`bridge-nf-call-iptables`和`bridge-nf-call-ip6tables`这两个内核参数置为1
     3. 关闭系统防火墙
 2. 脚本会安装Ascend Docker Runtime，自动为Docker的runtime增加昇腾的`ascend`runtime，配置文件的修改位置`/etc/docker/daemon.json`。
 3. 如果安装时选择了使用Harbor仓库，以下情况会修改`/etc/docker/daemon.json`文件，在“insecure-registries”字段中增加Harbor的地址，以保证能够使用Harbor。
     1. Harbor使用HTTPS服务，但inventory_file中未配置Harbor的CA证书路径
     2. Harbor使用HTTP服务
 4. 安装脚本会在操作系统上安装开源依赖软件，以方便安装驱动及使用`unzip` `lspci` `bc` `ip` `ifconfig`等命令


# 常用操作
 1. 保证安装Kubernetes的各节点的时间一致，避免因为时间问题导致kubernetes集群出现问题。

    **前提条件**：
    1. ansible已安装(用户可以通过在完成[步骤2：下载离线软件包](#步骤2下载离线软件包)后运行 `cd ~/offline-deploy; bash scripts/install_ansible.sh` 安装ansible)
    2. [配置inventory\_file](#步骤3配置安装信息)
    3. 节点已连通，可参考[常用操作2](#常用操作)

    将下面命令中的***2022-06-01 08:00:00***替换成用户需要的时间后，再执行
    ```
    cd /root/offline-deploy
    ansible -i inventory_file all -m shell -b -a "date -s '2022-06-01 08:00:00'; hwclock -w"
    ```

 2. 查看安装脚本执行节点能否访问inventory_file中的其他节点，即检查连通性。

    **前提条件**：
    1. ansible已安装(用户可以通过在完成[步骤2：下载离线软件包](#步骤2下载离线软件包)后运行 `cd ~/offline-deploy; bash scripts/install_ansible.sh` 安装ansible)
    2. [配置inventory\_file](#步骤3配置安装信息)

    **执行命令**：
    ```
    ansible -i inventory_file all -m ping
    ```
    回显中无“UNREACHABLE”表示连通，否则参考[常见安装问题1](#常见安装问题)进行处理
 3. 查看Ascend Docker Runtime是否生效，请执行命令`docker info 2>/dev/null | grep Runtime`，回显中出现“ascend”表示生效，回显示例如下。

    ```
    Runtimes: ascend runc
    Default Runtime: ascend
    ```
 4. 执行如下命令可以将inventory_file中配置的所有节点的k8s都重置（reset）
	```
    cd /root/offline-deploy
    ansible-playbook -i inventory_file yamls/k8s_reset.yaml -vv
    ```
 5. 配置免密登录
 	```
    ssh-keygen # 生成公钥，请按提示进行，在要求输入加密口令时输入复杂度符合所在组织安全规定的口令
    ssh-copy-id <user>@<ip>   # 将管理节点的公钥拷贝到所有节点的机器上(包括本机)，<user>替换成要登录的账号，<ip>替换成要拷贝到的对应节点的ip。
    # 在完成所有节点的免密配置后， 使用ssh-agent做口令缓存, 下面的  ~/.ssh/id_rsa  请根据ssh-keygen时的实际情况替换
    ssh-agent bash
    ssh-add ~/.ssh/id_rsa  
     
    ```
	注意事项: 请用户注意ssh密钥和密钥密码在使用和保管过程中的风险,安装完成后请删除控制节点~/.ssh/目录下的id_rsa和id_rsa_pub文件，和其他节点~/.ssh目录下的authorized_keys文件。
 6. hccn_tool网络配置（仅支持训练环境使用，详情可参考[配置device的网卡IP](https://www.hiascend.com/document/detail/zh/canncommercial/60RC1/envdeployment/instg/instg_000039.html)）
 	```
    下载文档中历史版本中最新的resources包，解压后将resources目录放置于root下

    cd ${HOME}/offline-deploy
    vi hccn_inventory_file
    # 进入offline-deploy目录，编辑hccn_inventory_file文件,新增待配置设备的ip地址、用户名、action（执行配置<config>或者查看当前设备配置信息<view>）、mode（工作模式<SMP>、<AMP>）、ip（npu卡所配ip）、detectip（对端检测ip）、netmask（子网掩码）。格式参考inventory_file。

    bash hccn_set.sh
    # 在offline-deploy/scripts目录下执行bash hccn_set.sh，完成指定设备的npu卡的ip网络配置。
    ```

    注意事项: 

    1、若未配置相关参数，无法完成ip配置；

    2、若执行批量配置时，需提前配置免密登录；

    3、hccn_inventory_file中ip、detectip配置格式有两种：

        <1>输入一个ip，工具自行生成后续ip，例如ip=10.0.0.1，工具会内部自行生成八个ip，10.0.0.1、10.0.1.1、10.0.2.1、10.0.3.1、10.0.0.2、10.0.1.2、10.0.2.2、10.0.3.2（该方法仅限于八卡环境）；
        <2>按照hccn配置官方文档要求，例如八卡环境上，ip=10.0.0.1,10.0.1.1,10.0.2.1,10.0.3.1,10.0.0.2,10.0.1.2,10.0.2.2,10.0.3.2（逗号必须为英文）。detectip类似输入。
    4、hccn_inventory_file其他配置可直接参考hccn_inventory_file中的样例;

 7. DL离线安装组件报告查看工具查看集群状态, 注意该功能仅能在master节点上运行;
    ```
     export current_arch=$(arch)
     cd ${HOME}/offline-deploy/tools/report
     ./k8s_status_report_$current_arch -h #查看帮助说明
     ./k8s_status_report_$current_arch -inventoryFilePath ${HOME}/offline-deploy/inventory_file -path /root -format csv   # 运行样例
     # 运行以上命令后，即可在本目录下生成nodeData.csv文件，可以查看相关节点和pod，容器等信息,将上述命令中的format改为json，
     # 会在本地生成master.json与work.json节点对应信息
     # 查看hccn,driver,docker等相关系统描述信息，可以执行scripts/machine_report.sh，会在/root目录下生成report_temp.txt文件, 运行命令如下
     cd ${HOME}/offline-deploy/scripts
     bash machine_report.sh
     cat /root/report_temp.txt # 查看docker, driver, hccn等相关信息
    
    ```

 8. 驱动、固件安装说明
    ```
    cd /root/offline-deploy
    # 批量安装驱动、固件需编辑当前目录的inventory_file文件中的worker节点, 将需要安装驱动设备加入，建议以worker其下的示例一为模板, 逐项填写, 并提前配置好免密登陆
    bash install_npu.sh                   # 安装驱动、固件
    # bash install_npu.sh --type=run        # 默认使用zip包安装，可指定为用run包安装
    ```

    注意事项：
    1. 若执行批量配置，需提前配置免密登录。
  
9. 导入镜像
 	```
    
    cd ${HOME}/offline-deploy
    vi inventory_file
    # 进入offline-deploy目录，编辑inventory_file文件。格式参考inventory_file。

    bash image_load.sh <镜像路径> <待安装节点> 
    # 在~/offline-deploy/scripts目录下执行image_load.sh <镜像路径> <待安装节点> ，提供的镜像应为docker save导出的tar格式镜像, 待安装节点取值范围为master/worker/all/mef, 对应inventory_file中对应项, 完成镜像的导入。
    # 可执行bash image_load.sh或bash image_load.sh -h查看help信息
    ```

    注意事项: 

    1、镜像路径需为绝对路径
    2、inventory_file其他配置可直接参考inventory_file中的样例;
    3、host只能为master,worker或all。

# 常见问题
## 常见安装问题

 1. 回显信息出现“UNREACHABLE”，参考信息如下：
     ```
     172.0.0.100 | UNREACHABLE! => {
        "changed": false, 
        "msg": "Failed to connect to the host via ssh: \nAuthorized users only. All activities may be monitored and reported.\nroot@172.0.0.100: Permission denied (publickey,gssapi-keyex,gssapi-with-mic,password).", 
        "unreachable": true
    }

     ```
     **原因**：<br />
     ansible脚本无法ssh登录到inventory_file中配置的服务器上

     **解决方法**：<br />
     请检查对应服务器的ssh配置是否正确，ssh服务是否启动，以及inventory_file文件配置是否正确
 2. 安装说明
 	- 安装脚本对Docker和Kubernetes的处理逻辑
 		- 场景包含的安装组件中没有Docker或Kubernetes时，脚本不会执行安装，以及初始化、加入集群等操作。
 		- 场景包含的安装组件中有Docker或Kubernetes时
 			- 如果用户已在部分节点安装过Docker或Kubernetes，则脚本会打印这些节点上软件的版本信息，并且跳过软件的安装；剩余未安装的节点，则会根据[软件支持列表](#软件支持列表)中的软件版本安装软件;此时用户需要保证自行安装的Docker或Kubernetes版本与软件支持列表中的软件版本一致，避免出现不可预测的问题。
 			- 如果master节点已经加入过Kubernetes集群，则该master节点会跳过初始化，不做任何操作；否则会初始化集群或者多master场景下会加入已有master集群；用户需要自行保证各master节点Kubernetes版本一致，避免不可预测的问题。
 			- 如果worker节点已经加入过集群，则该worker节点不会再加入master的集群，不做任何操作；未加入过集群的worker节点会加入到master集群中；用户需要自行保证各worker节点，以及worker节点与master节点Kubernetes版本一致，避免不可预测的问题。
 	- 安装脚本安装的组件由两部分组成，每个场景默认安装的组件加上EXTRA_COMPONENT中配置的组件
 	- 如果用户已经安装了Kubernetes，其版本不能高于1.21
 	- 多Master场景下每个Master的kube_interface参数的值必须为本机上已存在的网卡名
 	- 无论是单Master、还是多Master场景，k8s_api_server_ip参数必须配置为本机上已经存在的IP
 	- 节点的存放Docker镜像的磁盘分区需要保留至少30%的空间
 	- 如果节点的IP网段与默认的K8s默认集群网段（192.168.0.0/16）冲突，请用户修改inventory_file中的`POD_NETWORK_CIRD`参数为其他私有网段，如：10.0.0.0/16
 	- 训练节点需要配置device IP，可参考[配置训练服务器NPU的device IP](https://www.hiascend.com/document/detail/zh/canncommercial/60RC1/envdeployment/instg/instg_000039.html)
 	- 使用集群调度场景(全栈)部署时，inventory_file配置文件`[master]`下配置的节点个数必须为奇数，如1,3,5...

 3. 使用Harbor时，docker login失败了，运行日志出现如下内容
 	```
    ...
    TASK [faild to login] *************************************************************************************************************
    task path: /root/offline-deploy/tset.yaml:19
    fatal: [172.0.0.99]: FAILED! => {"changed": false, "msg": "login harbor failed, please check whether docker proxy is set"}
    ...
    ```

  	**原因**：<br />
    节点的Docker配置了代理，`docker login`命令无法连接到Harbor

    **解决方法**：<br />
    通过命令`docker info`依次查看登录失败的服务器是否配置了代理，回显如下表示本节点配置了代理
    ```
    ...
    HTTP Proxy: http://proxy.example.com:80/
    HTTPS Proxy: http://proxy.example.com:80/
    ...
    ```
    找到本节点上Docker配置代理的文件，如`/etc/systemd/system/docker.service.d/proxy.conf`，为Harbor地址（如：**192.168.0.2:7443**）配置`NO_PROXY`，示例如下
    ```
    [Service]
    ...
    Environment="NO_PROXY=192.168.0.2:7443"
    ...
    ```
    然后重启Docker服务，再进行安装
    ```
    systemctl daemon-reload
    systemctl restart docker
    ```
 4. 回显信息出现`Missing sudo password`
 	```
    TASK [create mindx-dl image pull secret]
    ****************************************************************************************************************************************
    task path: /root/offline-deploy/tset.yaml:12
    fatal: [172.0.0.100]: FAILED! => {"msg": "Missing sudo password"}
    ```
	**原因**：<br />
    inventory_file中配置的非root账号登录，且未在对应节点/etc/sudoers中为账号配置NOPASSWD，

    **解决方法**：<br />
    - 参考inventory_file中的注释，配置`ansible_become_password`参数
    - 在/etc/sudoers文件中为账号配置NOPASSWD
 5. 如果安装时选择了安装K8s，脚本运行过程中，出现K8s加入集群失败相关错误，建议执行reset命令后再重新安装，reset命令会重置inventory_file中配置的master和worker节点的K8s集群，请确认后再操作。命令执行参考[常用操作4](#常用操作)。
 6. 如果安装部署过程出现K8s的master与worker通信异常，如打标签失败，通信超时等问题导致脚本执行失败，可以按照如下思路手动进行排查处理。
    1. 先排查K8s节点之间网络是否连通，是否因为网络代理原因的影响。
    2. 根据安装部署脚本回显的日志信息，在对应节点手动执行日志中出现的命令，看是否成功；如果执行失败，可先在[常见问题](#常见问题)中寻找错误处理方案。
    3. 解决错误之后，可再次执行安装部署命令。
 7. 使用本工具部署时，如果/etc/ansible/facts-cache/ 目录存在，请先删除后再开始部署。
 8. 安装部署脚本执行时，master或者worker节点加入K8s集群，或者执行kubectl命令时出现类似如下错误信息
 	```
    read: connection reset by peer\nerror: unexpected error when reading response body. Please retry.
    ```
	**原因**：<br />
    可能由于节点之间网络通信不稳定，server端关闭了连接，导致申请加入集群的节点，或者发送kubectl命令的节点无法收到响应。

    **解决方法**：<br />
    1. 如果是加入集群时出现该错误，请在成功的master节点使用命令`kubectl get node`确认失败的节点是否加入成功
    	- 如果节点加入失败了，建议在对应节点上将K8s重置之后再执行安装命令，命令为`kubeadm reset -f && rm -rf $HOME/.kube /etc/cni/net.d`
    	- 如果worker节点加入成功了，则重新执行安装命令即可
    	- 如果master节点加入成功了，则需要执行下面命令，解除master隔离后，再重新执行安装命令
          ```
          # {nodename}为节点在K8s中的名字
          kubectl taint nodes {nodename} node-role.kubernetes.io/master-
          ```
    2. 如果是执行`kubectl`命令时失败了，根据回显的信息处理完错误后再执行安装命令。

## 其他问题

 1. 某个节点的calico-node-**出现READY “0/1”

     **分析：**
    - 使用`kubectl describe pod `命令查看K8s master节点的`calico-node`Pod时有报错信息“calico/node is not ready: BIRD is not ready: BGP not established with...”
    - kubelet日志报错“failed to run Kubelet: running with swap on is not supported, please disable swap”，通过`free`查询，存在swap空间。

    **原因：**<br />
    操作系统的swap分区未关闭

    **解决方案：**<br />
    执行命令`swapoff -a`


 2. 部署高可用集群时，出现phase preflight: couldn't validate the identity of the API Server: Get `"https://192.168.56.120:6443/api/v1/namespaces/kube-public/configmaps/cluster-info?timeout=10s"`: dial tcp 192.168.56.120:6443: connect: connection refused\nTo see the stack trace of this error execute with --v=5 or higher

    **原因：**<br />
    有多个master节点存在虚拟ip

     **解决方案：**<br />
    重启master节点，使kube-vip部署的虚拟ip地址失效

 3. 使用`kubectl`命令时，报错:The connection to the server xxxxx:6443 was refused - did you specify the right host or port?
    **原因：**<br />
    有可能是配置了代理；k8s服务未启动；未给用户配置授权文件

    **解决方案：**<br />
    如果是配置了代理，使用如下命令，去掉代理后再试
    ```
    unset http_proxy https_proxy
    ```
    如果是k8s服务未启动，使用如下命令，启动K8s服务后再试
    ```
    systemctl start kubelet
    ```
    如果未给用户配置授权文件，使用如下命令，配置授权文件后再试
    ```
    export KUBECONFIG=/etc/kubernetes/admin.conf
    或者
    export KUBECONFIG=/etc/kubernetes/kubelet.conf
    ```

 4. 部署多master集群时，需要使用ip a查看每个节点虚拟ip有没有被分配，如果有则需要在对应节点上使用以下命令删除
    ```
    ip addr delete <ip地址> dev <网卡名>
    ```
# 免责声明
如需在生产环境中安装并使用Docker和Kubernetes，请参考对应的官方文档进行安装、配置和安全加固。
# 历史版本
<table>
<thead>
  <tr>
    <th>版本</th>
    <th>资源</th>
    <th>发布日期</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>5.0.RC1</td>
    <td><a href="https://ascend-repo-modelzoo.obs.myhuaweicloud.com/MindXDL/5.0.RC1/resources.zip">https://ascend-repo-modelzoo.obs.myhuaweicloud.com/MindXDL/5.0.RC1/resources.zip</a></td>
    <td>2022.12.30</td>
  </tr>
  <tr>
    <td>3.0.0</td>
    <td><a href="https://ascend-repo-modelzoo.obs.cn-east-2.myhuaweicloud.com/MindXDL/3.0.0/resources.tar.gz">https://ascend-repo-modelzoo.obs.cn-east-2.myhuaweicloud.com/MindXDL/3.0.0/resources.tar.gz</a></td>
    <td>2022.12.30</td>
  </tr>
  <tr>
    <td>3.0.RC3</td>
    <td><a href="https://ascend-repo-modelzoo.obs.cn-east-2.myhuaweicloud.com/MindXDL/3.0.RC3/resources.tar.gz">https://ascend-repo-modelzoo.obs.cn-east-2.myhuaweicloud.com/MindXDL/3.0.RC3/resources.tar.gz</a></td>
    <td>2022.09.30</td>
  </tr>
</tbody>
</table>

# CHANGELOG
<table>
<thead>
  <tr>
    <th>版本</th>
    <th>版本说明</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>5.0.RC1</td>
    <td><li>支持按场景进行安装部署</li><br /><li>部署脚本支持运行环境为：Ubuntu 18.04、20.04和CentOS 7.6和OpenEuler 20.03 LTS、22.03 LTS</li><br /><li>支持使用Harbor仓</li><br /><li>支持K8s多master部署</li></td>
  </tr>
  <tr>
    <td>3.0.0</td>
    <td><li>支持按场景进行安装部署</li><br /><li>部署脚本支持运行环境为：Ubuntu 18.04和OpenEuler 20.03 LTS</li><br /><li>支持使用Harbor仓</li><br /><li>支持K8s多master部署</li></td>
  </tr>
</tbody>
</table>
