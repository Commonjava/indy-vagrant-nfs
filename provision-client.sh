yum install -y epel-release wget
yum update -y

cd /tmp
wget http://repo.maven.apache.org/maven2/org/commonjava/indy/launch/indy-launcher-savant/1.1.5/indy-launcher-savant-1.1.5-launcher.tar.gz
tar -zxvf /tmp/indy-launcher-savant-1.1.5-launcher.tar.gz -C /opt

if [ ! -d /opt/indy/var/lib/indy/storage ]; then
	mkdir -p /opt/indy/var/lib/indy/storage
fi

mount -t nfs nfs.local:/exports/test /opt/indy/var/lib/indy/storage
