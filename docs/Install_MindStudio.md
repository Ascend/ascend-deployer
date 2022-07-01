# 安装MindStudio
版本配套、环境要求等详情请参考MindStudio官网及手册
https://www.hiascend.com/software/mindstudio/download

## 支持的操作系统

- Ubuntu_18.04_x86_64、Ubuntu_18.04_aarch64、EulerOS_2.8_aarch64

## 下载

```bash
./start_download.sh --os-list=Ubuntu_18.04_x86_64 --download=MindStudio
```
目前MindStudio 2.0.0、3.0.1、3.0.2版本只支持在以上3个OS，--download=MindStudio时，--os-list需同时指定这3个OS的某一个或某几个。

## 安装

```bash
./install.sh --install=python,mindstudio
```

## 版本配套
MindStudio 2.0.0配套CANN 20.2.RC1，MindStudio 3.0.1配套CANN 5.0.1，MindStudio 3.0.2配套CANN 5.0.2.1, MindStudio 3.0.3配套CANN 5.0.3.1, MindStudio 3.0.4配套CANN 5.0.4, MindStudio 5.1.RC1配套CANN 5.1.RC1

## 说明

安装MindStudio的过程将安装相关操作系统依赖和python库
