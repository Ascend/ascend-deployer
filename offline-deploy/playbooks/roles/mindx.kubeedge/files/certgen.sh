#!/usr/bin/env bash

set -o errexit

readonly caPath=${CA_PATH:-/etc/kubeedge/ca}
readonly subject=${SUBJECT:-/C=CN/ST=Sichuan/L=Chengdu/O=Huawei/OU=Ascend/CN=MindX}

genCA() {
    openssl ecparam -name secp384r1 -genkey -noout -out ${caPath}/rootCA.key
    openssl req -x509 -new -nodes -sha256 -days 3650 -subj ${subject} -key ${caPath}/rootCA.key -out ${caPath}/rootCA.crt
    chmod 400 ${caPath}/rootCA.*
}

ensureCA() {
    if [ ! -e ${caPath}/rootCA.crt ]; then
        genCA
    fi
}

ensureFolder() {
    if [ ! -d ${caPath} ]; then
        mkdir -p -m 700 ${caPath}
    fi
    if [ ! -d ${certPath} ]; then
        mkdir -p -m 700 ${certPath}
    fi
}

genCsr() {
    local name=$1
    openssl ecparam -name secp384r1 -genkey -noout -out ${certPath}/${name}.key
    openssl req -sha256 -new -subj ${subject} -key ${certPath}/${name}.key -out ${certPath}/${name}.csr
}

genCert() {
    local name=$1
    local master_ip=$2
    cat > ${certPath}/v3.ext <<-EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
IP=${master_ip}
EOF

    openssl x509 -req -sha512 -days 3650 -extfile ${certPath}/v3.ext -CA ${caPath}/rootCA.crt -CAkey ${caPath}/rootCA.key \
    -CAcreateserial -in ${certPath}/${name}.csr -out ${certPath}/${name}.crt
    chmod 400 ${certPath}/${name}.* ${certPath}/v3.ext
    chmod 400 ${caPath}/rootCA.srl
}

genCertAndKey() {
    local name=$1
    certPath=$2
    local master_ip=$3
    ensureFolder
    ensureCA
    genCsr $name
    genCert $name $master_ip
}

stream() {
    ensureFolder
    readonly streamsubject=${SUBJECT:-/C=CN/ST=Zhejiang/L=Hangzhou/O=KubeEdge}
    readonly STREAM_KEY_FILE=${certPath}/stream.key
    readonly STREAM_CSR_FILE=${certPath}/stream.csr
    readonly STREAM_CRT_FILE=${certPath}/stream.crt
    readonly K8SCA_FILE=/etc/kubernetes/pki/ca.crt
    readonly K8SCA_KEY_FILE=/etc/kubernetes/pki/ca.key

    if [ -z ${CLOUDCOREIPS} ]; then
        echo "You must set CLOUDCOREIPS Env,The environment variable is set to specify the IP addresses of all cloudcore"
        echo "If there are more than one IP need to be separated with space."
        exit 1
    fi

    index=1
    SUBJECTALTNAME="subjectAltName = IP.1:127.0.0.1"
    for ip in ${CLOUDCOREIPS}; do
        SUBJECTALTNAME="${SUBJECTALTNAME},"
        index=$(($index+1))
        SUBJECTALTNAME="${SUBJECTALTNAME}IP.${index}:${ip}"
    done

    cp /etc/kubernetes/pki/ca.crt ${caPath}/streamCA.crt
    echo $SUBJECTALTNAME > /tmp/server-extfile.cnf

    openssl genrsa -out ${STREAM_KEY_FILE}  2048
    openssl req -new -key ${STREAM_KEY_FILE} -subj ${streamsubject} -out ${STREAM_CSR_FILE}

    # verify
    openssl req -in ${STREAM_CSR_FILE} -noout -text
    openssl x509 -req -in ${STREAM_CSR_FILE} -CA ${K8SCA_FILE} -CAkey ${K8SCA_KEY_FILE} -CAcreateserial -out ${STREAM_CRT_FILE} -days 5000 -sha256 -extfile /tmp/server-extfile.cnf
    #verify
    openssl x509 -in ${STREAM_CRT_FILE} -text -noout
}

buildSecret() {
    local name="edge"
    genCertAndKey ${name} > /dev/null 2>&1
    cat <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: cloudcore
  namespace: kubeedge
  labels:
    k8s-app: kubeedge
    kubeedge: cloudcore
stringData:
  rootCA.crt: |
$(pr -T -o 4 ${caPath}/rootCA.crt)
  edge.crt: |
$(pr -T -o 4 ${certPath}/${name}.crt)
  edge.key: |
$(pr -T -o 4 ${certPath}/${name}.key)

EOF
}

$1 $2 $3 $4
