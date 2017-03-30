# Vagrant Definitions for Testing Indy with NFS storage

This Vagrant setup defines two VMs: `nfs` and `client`. The `nfs` VM defines an NFS export for use with Indy, and runs a tcconfig script. The script is re-run each time the VM starts, allowing the user to redefine the parameters without having to re-provision the system. The `client` detects whether a local Indy directory structure has been rsynced during VM startup (by Vagrant) and uses that if it exists; if not, it will download an Indy tarball, unpack it, and use it.

## Specifying `tc` Configuration

The `nfs/tc.sh` script is intended to allow users to tune the traffic shaping parameters for use with the NFS export. Normally you would use `tcset` here to define the types of network errors / de-optimization you want.

It's important to note that the NFS share takes place on the `192.168.50.0/24` network, on device `eth1`. Therefore, you should confine your `tcset` commands to that device.

## Specifying Indy URL or Directory

The `nfs/start-indy.sh` script tries to detect what Indy version / binary you want to start. First, if you've linked in an `indy/` directory in your vagrant directory, such that the client VM has a `/vagrant/indy/` directory, the script will copy that to `/opt/indy` and use it. However, if that directory doesn't exist, it will download an Indy tarball, unpack it, and use it.

The specific tarball this script tries to download depends on the URL given in the `client/start-indy.sh` script.

## Restarting vs. Re-Provisioning

The scripts used to start the various services in the VMs have been separated from the provisioning scripts on purpose, to allow users to reconfigure the VMs in common ways without the need to undergo an expensive re-provisioning step.

## Connecting to Indy from the Host

Once the VMs are started, you should be able to grab the IP address of the `client` VM and use that to access Indy:

```
    $ vagrant ssh-config client
    Host client
      HostName 192.168.121.19
      User vagrant
      Port 22
      UserKnownHostsFile /dev/null
      StrictHostKeyChecking no
      PasswordAuthentication no
      IdentityFile /home/jdcasey/code/vagrant/test-nfs/.vagrant/machines/client/libvirt/private_key
      IdentitiesOnly yes
      LogLevel FATAL

    $ cd /path/to/maven/project

    $ curl http://192.168.121.19:8080/mavdav/settings/group/settings-public.xml > settings.xml

    $ cat settings.xml
    <?xml version="1.0" encoding="UTF-8"?>
    <!--
      Copyright (c) 2014 Red Hat, Inc..
      All rights reserved. This program and the accompanying materials
      are made available under the terms of the GNU Public License v3.0
      which accompanies this distribution, and is available at
      http://www.gnu.org/licenses/gpl.html
      
      Contributors:
          Red Hat, Inc. - initial API and implementation
    -->
    <settings>
      <localRepository>${user.home}/.m2/repo-group-public</localRepository>
      <mirrors>
        <mirror>
          <id>public</id>
          <mirrorOf>*</mirrorOf>
          <url>http://192.168.121.19:8080/api/group/public</url>
        </mirror>
      </mirrors>
      <profiles>
        <profile>
          <id>resolve-settings</id>
          <repositories>
            <repository>
              <id>central</id>
              <url>http://192.168.121.19:8080/api/group/public</url>
              <releases>
                <enabled>true</enabled>
              </releases>
              <snapshots>
                <enabled>false</enabled>
              </snapshots>
            </repository>
          </repositories>
          <pluginRepositories>
            <pluginRepository>
              <id>central</id>
              <url>http://192.168.121.19:8080/api/group/public</url>
              <releases>
                <enabled>true</enabled>
              </releases>
              <snapshots>
                <enabled>false</enabled>
              </snapshots>
            </pluginRepository>
          </pluginRepositories>
        </profile>
        
      </profiles>
      <activeProfiles>
        <activeProfile>resolve-settings</activeProfile>
        
      </activeProfiles>
    </settings>

    $ mvn -s ./settings.xml clean install
    [...]
```

