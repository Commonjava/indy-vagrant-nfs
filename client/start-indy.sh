#!/bin/bash

set -x

for p in $(rpcinfo -p | awk '{print $4}' | grep -v port | sort -n | uniq)
do
    echo "Adding port $p tcp/udp to iptables"
    iptables -A INPUT -p tcp --dport $p -j ACCEPT
    iptables -A INPUT -p udp --dport $p -j ACCEPT
done

INDY_URL=http://repo.maven.apache.org/maven2/org/commonjava/indy/launch/indy-launcher-savant/1.1.5/indy-launcher-savant-1.1.5-launcher.tar.gz
MOUNT_OPTS='rw,relatime,vers=4.0,rsize=65536,wsize=65536,namlen=255,hard,proto=tcp,timeo=600,retrans=2,local_lock=none'

if [ -f /vagrant/client/indy-info ]
then
    source /vagrant/client/indy-info
fi

if [ "x" != "x$(df | grep 192.168.50.2)" ]; then
    umount /opt/indy/var/lib/indy/storage
fi

rm -rf /opt/indy

name=$(basename $INDY_URL)

if [ -d /vagrant/indy ]
then
    cp -rf /vagrant/indy /opt/indy
elif [ -f /vagrant/indy.tar.gz ]
then
    tar -zxf /vagrant/indy.tar.gz -C /opt
else
    if [ ! -f /tmp/$name ]
    then
        echo "Retrieving Indy from: $INDY_URL to: /tmp/$name"
        wget --quiet -O /tmp/$name $INDY_URL
    fi
    tar -zxf /tmp/$name -C /opt
fi

if [ -d /vagrant/indy-overlay ]; then
    cp -rf /vagrant/indy-overlay/* /opt/indy
fi

if [ ! -d /opt/indy/var/lib/indy/storage ]
then
    mkdir -p /opt/indy/var/lib/indy/storage
fi

INDY_LOGS=/opt/indy/var/log/indy

if [ ! -e $INDY_LOGS -o ! -L $INDY_LOGS ]; then
    rm -rf $INDY_LOGS

    if [ ! -d /var/log/indy ]; then
        mkdir /var/log/indy
        chown -R vagrant /var/log/indy
    fi

    if [ ! -d /opt/indy/var/log ]; then
        mkdir -p /opt/indy/var/log
    fi

    ln -s /var/log/indy $INDY_LOGS
fi

if [ "x" == "x$(df | grep 192.168.50.2)" ]; then
    mount -t nfs -o "$MOUNT_OPTS" 192.168.50.2:/exports/test /opt/indy/var/lib/indy/storage
fi

exec /opt/indy/bin/indy.sh
