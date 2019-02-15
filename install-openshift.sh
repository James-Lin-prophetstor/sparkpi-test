#/bin/sh
vim: ts=4 sw=4 et smarttab
DOCKER_DAEMON_JSON=/etc/docker/daemon.json
OC_URL="https://github.com/openshift/origin/releases/download/v3.11.0/openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz"
OC_FILENAME_TARGZ=`basename ${OC_URL}`
OC_LOGIN="oc login -u admin -p password"
HELM_URL="https://storage.googleapis.com/kubernetes-helm/helm-v2.9.0-linux-amd64.tar.gz"
TILLER_URL="https://github.com/openshift/origin/raw/master/examples/helm/tiller-template.yaml"
SPARKPI_RESOURCE="https://radanalytics.io/resources.yaml"
SPARKPI_PROJECT="spark-cluster"
SPARKPI_EXAMPLE="https://github.com/radanalyticsio/tutorial-sparkpi-python-flask.git"
SPARKPI_OC="oc -n $SPARKPI_PROJECT"
IP_ADDRESS=`cat /etc/sysconfig/network-scripts/ifcfg-*| 
            grep IPADDR | 
            grep -v '127.0.0.1' |
            awk -F= '{print $2}' |
            sed "s/\"//g"`

DOCKER_CE_REPO=/etc/yum.repos.d/docker-ce.repo
OC_BASE_DIR=/opt/oc/
OC_CLUSTER_UP=/usr/local/sbin/oc_cluster_up.sh
mkdir -p $OC_BASE_DIR
SELINUX=/etc/selinux/config

date
#=======================================================
echo "## Step 1:  OS confirm: "
echo "## Only for CentOS Linux release 7.5.1804 (Core) and later"
echo "## Create a standalone openshift 3.11 OKD test environment by 'oc cluster up'."
echo "## Install helm, sparkpi on openshift"
echo "System:"
uname -a
cat /etc/redhat-release
echo
read -p "Press Enter to install or CTRL-C to exit"

echo "## Disable selinux first"
for SETTING in enforcing permissive ; do
    if grep "SELINUX=${SETTING}" $SELINUX ; then
        echo "Please reboot server once for SELINUX disabled, now."
        echo "And run this script again."
        echo -e "\n\n"
        sed -i -e "s/SELINUX=${SETTING}/SELINUX=disabled/" $SELINUX
        echo "## Configure:"
        grep "SELINUX=disabled" $SELINUX
        exit 0
    fi
done

echo "## Install required packeds: yum-utils device-mapper-persistent-data lvm2 screen git"
sudo yum clean all
sudo yum install -y yum-utils \
                    device-mapper-persistent-data \
                    lvm2 \
                    screen \
                    git \
                    NetworkManager-tui

echo  "## Add docker-ce edge repo to yum repository"  
cat >${DOCKER_CE_REPO} <<'EOF'
[docker-ce-edge]
name=Docker CE Edge - $basearch
baseurl=https://download.docker.com/linux/centos/7/$basearch/edge
enabled=1
gpgcheck=1
gpgkey=https://download.docker.com/linux/centos/gpg
EOF
cat ${DOCKER_CE_REPO}
echo

echo "## Remove old default docker"
if rpm -qa | grep docker-1 ; then
    yum remove -y docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine
fi

echo "## Install docker-ce-edge"
yum -y install docker-ce
echo "## Systemctl start docker"
systemctl start docker
echo "## Systemctl enable docker start on boot"
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
if [ -f "${DOCKER_DAEMON_JSON}" ] ; then
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

echo "## Systemctl daemon-reload"
systemctl daemon-reload
echo
echo "## Systemctl restart docker"
systemctl restart docker

echo "## Confirm docker version"
docker version
if $? != 0 ; then
    echo "Can not check docker version."
    echo "Please install docker first."
    exit 1
fi
echo "## Check docker running stat"
systemctl status docker
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
echo -e "firewall stat is \c"
firewall-cmd --stat
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
sleep 1
echo

date
#=======================================================
echo "## Step 6: start up oc cluster"
echo "## command:"
echo "oc cluster up --public-hostname=${IP_ADDRESS} --base-dir=${OC_BASE_DIR}"
oc cluster up \
  --public-hostname=${IP_ADDRESS} \
  --base-dir=${OC_BASE_DIR}
cat >>${OC_CLUSTER_UP} <<'EOF'
IP_ADDRESS=`cat /etc/sysconfig/network-scripts/ifcfg-*| 
    grep IPADDR | 
    grep -v '127.0.0.1' |
    awk -F= '{print $2}' |
    sed "s/\"//g"`

BASE_DIR=/opt/oc
OC=/usr/local/bin/oc

$OC cluster up \
        --public-hostname=${IP_ADDRESS} \
        --base-dir=${BASE_DIR}
EOF

chmod 755 ${OC_CLUSTER_UP}

date
docker images

date
#=======================================================
echo "## Step 7: Openshift : "
echo "           Create default user admin as cluster administrator and password is password"
oc login -u system:admin
oc create user admin
echo "## Map RBAC (role-based access control) to admin"
oc adm policy add-cluster-role-to-user cluster-admin admin
$OC_LOGIN
echo

date
#=======================================================
echo "## Step 8: Install helm:"
$OC_LOGIN
oc project kube-system
curl -s ${HELM_URL} | tar xz
cp linux-amd64/helm /usr/local/bin
chmod 755 /usr/local/bin/helm
helm init --service-account tiller
echo "## Install helm tiller server on openshift"
oc process -f ${TILLER_URL} -p TILLER_NAMESPACE=kube-system -p HELM_VERSION=v2.9.0 |
     oc create -f -
echo
while true ; do
	  if oc get pod -n kube-system | grep tiller |grep -v deploy| grep Running ; then
		    break
	  fi
done
echo
sleep 20
echo "## Map RBAC (role-based access control) to tiller "
oc adm policy add-scc-to-user anyuid system:serviceaccount:kube-system:tiller
oc adm policy add-scc-to-group anyuid system:authenticated
echo "## Get helm & tiller version"
helm version
echo

date
# #=======================================================
# echo "## Step 9: Install Sparkpi on openshift "
# oc new-project ${SPARKPI_PROJECT} 
# oc project ${SPARKPI_PROJECT}
# oc create -f ${SPARKPI_RESOURCE}
# oc new-app \
#         --template oshinko-python-spark-build-dc \
#         -p APPLICATION_NAME=sparkpi \
#         -p GIT_URI=${SPARKPI_EXAMPLE}
# while true ; do
#     if oc get bc | grep sparkpi ; then
#         break
#     fi
# done
# sleep 5

# oc logs -f bc/sparkpi
# oc expose svc/sparkpi
# echo "## oc get $SPARKPI_PROJECT status"
# $SPARKPI_OC status 
# echo "## oc get $SPARKPI_PROJECT pods"
# $SPARKPI_OC get pod
# echo "## oc get $SPARKPI_PROJECT route"
# $SPARKPI_OC get route
echo "oc get pod --all-namespaces"
oc get pod --all-namespaces
echo "## Finished."
