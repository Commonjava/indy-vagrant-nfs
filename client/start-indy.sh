#!/bin/bash

# Show everything this script does in the journal.
set -x

# Ensure applicable ports are open on the firewall, just in case
for p in $(rpcinfo -p | awk '{print $4}' | grep -v port | sort -n | uniq); do
    echo "Adding port $p tcp/udp to iptables"
    iptables -A INPUT -p tcp --dport $p -j ACCEPT
    iptables -A INPUT -p udp --dport $p -j ACCEPT
done

INDY_URL=http://repo.maven.apache.org/maven2/org/commonjava/indy/launch/indy-launcher-savant/1.1.5/indy-launcher-savant-1.1.5-launcher.tar.gz
MOUNT_OPTS='rw,relatime,vers=4.0,rsize=65536,wsize=65536,namlen=255,hard,proto=tcp,timeo=600,retrans=2,local_lock=none'
USE_NFS='Y'

# if [ -f /vagrant/client/indy-info ]; then
#     source /vagrant/client/indy-info
# fi

if [ "x${USE_NFS}" = 'xY' ]; then
    # Unmount the NFS volume to refresh it, just in case something has gone stale
    if [ "x" != "x$(df | grep 192.168.50.2)" ]; then
        umount /opt/indy/var/lib/indy
    fi
fi

rm -rf /opt/indy

name=$(basename $INDY_URL)

if [ -d /vagrant/indy ]; then
    # Use an Indy directory uploaded from the host environment
    cp -rf /vagrant/indy /opt/indy
elif [ -f /vagrant/indy.tar.gz ]; then
    # unpack a tarball uploaded from the host environment
    tar -zxf /vagrant/indy.tar.gz -C /opt
else
    # possibly retrieve, and then unpack, the release from the URL
    if [ ! -f /tmp/$name ]; then
        echo "Retrieving Indy from: $INDY_URL to: /tmp/$name"
        wget --quiet -O /tmp/$name $INDY_URL
    fi
    tar -zxf /tmp/$name -C /opt
fi

if [ "x${USE_NFS}" = 'xY' ]; then
    # Be double-sure this directory exists before we try to mount to it
    if [ ! -d /opt/indy/var/lib/indy ]; then
        mkdir -p /opt/indy/var/lib/indy
    fi

    # Save the UI, to overwrite into NFS mount
    rm -rf /opt/ui
    mv /opt/indy/var/lib/indy/ui/ /opt/ui/

    # Re-mount NFS
    if [ "x" == "x$(df | grep 192.168.50.2)" ]; then
        mount -t nfs -o "$MOUNT_OPTS" 192.168.50.2:/exports/test /opt/indy/var/lib/indy
    fi

    # Overwrite UI in NFS mount
    rm -rf /opt/indy/var/lib/indy/ui
    mv /opt/ui/ /opt/indy/var/lib/indy/ui/
fi

# Copy in the overlay files
if [ -d /vagrant/indy-overlay ]; then
    cp -rf /vagrant/indy-overlay/* /opt/indy
fi

INDY_LOGS=/opt/indy/var/log/indy

rm -rf $INDY_LOGS

# Try to divert Indy logs to a place that won't be removed on restart
if [ ! -d /var/log/indy ]; then
    mkdir /var/log/indy
    chown -R vagrant /var/log/indy
fi

ln -s /var/log/indy $INDY_LOGS

# Now, start Indy
exec /opt/indy/bin/indy.sh
