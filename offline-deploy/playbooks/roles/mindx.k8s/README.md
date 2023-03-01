mindx.k8s
=========

install k8s: kubeadm, kubectl, kubelet


cni plugin

```bash
CNI_VERSION="v0.8.2"
ARCH="amd64"
sudo mkdir -p /opt/cni/bin
wget https://github.com/containernetworking/plugins/releases/download/${CNI_VERSION}/cni-plugins-linux-${ARCH}-${CNI_VERSION}.tgz
```

cri-tool

```bash
CRICTL_VERSION="v1.17.0"
ARCH="amd64"
wget https://github.com/kubernetes-sigs/cri-tools/releases/download/${CRICTL_VERSION}/crictl-${CRICTL_VERSION}-linux-${ARCH}.tar.gz
```

Requirements
------------

mindx.docker

License
-------

Apache
