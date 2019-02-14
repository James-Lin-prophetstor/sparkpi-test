#/bin/sh

DOCKER_DAEMON_JSON=/etc/docker/daemon.json
#OC_URL="https://github.com/openshift/origin/releases/download/v3.9.0/openshift-origin-client-tools-v3.9.0-191fece-linux-64bit.tar.gz"
OC_URL="https://github.com/openshift/origin/releases/download/v3.11.0/openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz"
OC_FILENAME_TARGZ=`basename ${OC_URL}`
IP_ADDRESS=`ip address show|grep 'ens' | grep 'inet'|awk '{print $2}'|sed 's/\/.*//g'`
DOCKER_CE_REPO=/etc/yum.repos.d/docker-ce.repo
OC_BASE_DIR=/opt/oc/
OC_CLUSTER_UP=/usr/local/sbin/oc_cluster_up.sh
mkdir -p $OC_BASE_DIR

date
#=======================================================
echo "## Step 1:  OS version confirm: "
uname -a
cat /etc/redhat-release
echo

# install packages
echo "## install required packeds: yum-utils device-mapper-persistent-data lvm2 screen git"
sudo yum install -y yum-utils \
  device-mapper-persistent-data \
  lvm2 \ 
  screen \ 
  git

# Install docker-ce-edge
#sudo yum-config-manager \
#    --add-repo \
#    https://download.docker.com/linux/centos/docker-ce.repo
# Docker installer
#echo "## Install docker "
#yum -y install docker
#echo
# add docker-ce edge repo to yum repository
echo >${DOCKER_CE_REPO} <<EOF
[docker-ce-edge]
name=Docker CE Edge - $basearch
baseurl=https://download.docker.com/linux/centos/7/$basearch/edge
enabled=1
gpgcheck=1
gpgkey=https://download.docker.com/linux/centos/gpg
EOF
cat ${DOCKER_CE_REPO}
echo
echo "## install docker-ce-edge"
yum -y install docker-ce
echo "## systemctl start docker"
systemctl start docker
echo "## systemctl enable docker autostart"
systemctl enable docker

date
#=======================================================
echo "## Step 2: Set net.ipv4.ip_forward"
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
systemctl restart network
grep net.ipv4.ip_forward /etc/sysctl.conf
echo "sysctl net.ipv4.ip_forward"
sysctl net.ipv4.ip_forward
echo

date
#=======================================================
echo "## Step 3: Set registry & Restart docker"
if [ -f "${DOCKER_DAEMON_JSON}" ]; then
  cp ${DOCKER_DAEMON_JSON} ${DOCKER_DAEMON_JSON}.org
fi

cat >${DOCKER_DAEMON_JSON} <<EOF
{
   "insecure-registries": [
     "172.30.0.0/16"
   ]
}
EOF
cat ${DOCKER_DAEMON_JSON}
echo

echo "## systemctl daemon-reload"
systemctl daemon-reload
echo
echo "## systemctl restart docker"
systemctl restart docker

echo "## confirm docker version"
docker version
if $? != 0; then
    echo "Can not check docker version."
    echo "Please install docker first."
    exit 1
fi
echo

date
#=======================================================
echo "## Step 4: Set for firewall"
sudo systemctl stop firewalld
sudo systemctl disable firewalld
# firewall-cmd --permanent --new-zone dockerc
# firewall-cmd --permanent --zone dockerc --add-source 172.17.0.0/16
# firewall-cmd --permanent --zone dockerc --add-port 8443/tcp
# firewall-cmd --permanent --zone dockerc --add-port 53/udp
# firewall-cmd --permanent --zone dockerc --add-port 8053/udp
# firewall-cmd --reload
echo

date
echo "## Step 5: get and setting oc: "
#=======================================================
yum install -y wget
wget  ${OC_URL}
tar xvpf ${OC_FILENAME_TARGZ}
DIRNAME=`echo ${OC_FILENAME_TARGZ} |sed s/.tar.gz//g`
cp ${DIRNAME}/oc /usr/local/bin
chmod 755 /usr/local/bin/oc
which oc
oc version
echo

date
#=======================================================
echo "## Step 6: start up oc cluster"
#oc cluster up --host-data-dir="/opt"
oc cluster up --public-hostname=${IP_ADDRESS} --base-dir=${OC_BASE_DIR}
cat >${OC_CLUSTER_UP} <<EOF
LOCAL_IP=$(ip address show | grep 'ens' |grep 'inet ' |awk '{print $2}' |awk -F/ '{print $1}' )
BASE_DIR=/opt/oc
OC=/usr/local/bin/oc

$OC cluster up \
--public-hostname=${LOCAL_IP} \
--base-dir=${BASE_DIR}
EOF

chmod 755 ${OC_CLUSTER_UP}

date
docker images

date
#=======================================================
echo "## Step 7: oc login -u developer"
oc login -u developer
echo "## Finished."
