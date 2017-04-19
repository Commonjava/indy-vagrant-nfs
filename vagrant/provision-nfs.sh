yum install -y epel-release
yum update -y
yum install -y python-pip tcpdump
yum clean all

pip install --upgrade pip
pip install tcconfig

mkdir -p /exports/test

cat > /etc/exports << '__EOF__'
/exports/test  *(rw,no_root_squash)
__EOF__

for s in nfs-idmapd.service rpc-statd.service rpcbind.socket; do
	systemctl enable $s
	systemctl start $s
done

cat > /etc/systemd/system/tcconfig.service << '__EOF__'
[Unit]
Description=Network Configuration
Wants=network-online.target
After=network.target network-online.target

[Service]
Restart=always
RestartSec=10
ExecStart=/bin/bash -l /vagrant/nfs/tc.sh

[Install]
WantedBy=multi-user.target
__EOF__

systemctl daemon-reload

systemctl disable firewalld
systemctl stop firewalld

systemctl enable tcconfig
systemctl start tcconfig
