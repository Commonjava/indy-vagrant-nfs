#!/bin/bash

systemctl status nfs || systemctl restart nfs

#tcset --device eth1 --delay 50 --loss 10 --overwrite
tcshow --device eth1

nohup tcpdump -w /tmp/tcdump.log port nfs &

