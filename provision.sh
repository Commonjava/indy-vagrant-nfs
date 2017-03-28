yum install -y epel-release
yum update -y
yum install -y python-pip

pip install --upgrade pip
pip install tcconfig

mkdir -p /exports/test

cat > /etc/exports << '__EOF__'
/exports/test  *(rw,no_root_squash)
__EOF__

for s in rpcbind nfs-mountd nfs-idmapd; do
	systemctl enable $s
	systemctl start $s
done

ip addr show | grep 'inet '
