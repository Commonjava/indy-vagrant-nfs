#!/bin/bash

tcset --device eth1 --delay 50 --loss 10 --overwrite
tcshow --device eth1
