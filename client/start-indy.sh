#!/bin/bash

set -x

for p in $(rpcinfo -p | grep -v port | awk '{print $4}' | sort -n | uniq)
do
    echo "Adding port $p tcp/udp to iptables"
    iptables -A INPUT -p tcp --dport $p -j ACCEPT
    iptables -A INPUT -p udp --dport $p -j ACCEPT
done

INDY_URL=http://repo.maven.apache.org/maven2/org/commonjava/indy/launch/indy-launcher-savant/1.1.5/indy-launcher-savant-1.1.5-launcher.tar.gz

if [ -f /vagrant/indy-info ]
then
    source /vagrant/indy-info
fi

rm -rf /opt/indy

name=$(basename $INDY_URL)

if [ -d /vagrant/indy ]
then
    cp -rf /vagrant/indy /opt/indy
else
    if [ ! -f /tmp/$name ]
    then
        echo "Retrieving Indy from: $INDY_URL to: /tmp/$name"
        wget --quiet -O /tmp/$name $INDY_URL
    fi
    tar -zxf /tmp/$name -C /opt
fi

if [ ! -d /opt/indy/var/lib/indy/storage ]
then
    mkdir -p /opt/indy/var/lib/indy/storage
fi

if [ "x" == "x$(df | grep 192.168.50.2)" ]; then
    mount -t nfs -o "$MOUNT_OPTS" 192.168.50.2:/exports/test /opt/indy/var/lib/indy/storage
fi

exec /opt/indy/bin/indy.sh
