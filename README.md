# Vagrant Definitions for Testing Indy with NFS storage

This Vagrant setup defines two VMs: `nfs` and `indy`. The `nfs` VM defines an NFS export for use with Indy, and runs a tcconfig script. The script is re-run each time the VM starts, allowing the user to redefine the parameters without having to re-provision the system. The `indy` detects whether a local Indy directory structure has been rsynced during VM startup (by Vagrant) and uses that if it exists; if not, it will download an Indy tarball, unpack it, and use it.

## Specifying `tc` Configuration

The `nfs/tc.sh` script is intended to allow users to tune the traffic shaping parameters for use with the NFS export. Normally you would use `tcset` here to define the types of network errors / de-optimization you want.

It's important to note that the NFS share takes place on the `192.168.50.0/24` network, on device `eth1`. Therefore, you should confine your `tcset` commands to that device.

## Specifying Indy URL or Directory

The `nfs/start-indy.sh` script tries to detect what Indy version / binary you want to start. First, if you've linked in an `indy/` directory in your vagrant directory, such that the indy VM has a `/vagrant/indy/` directory, the script will copy that to `/opt/indy` and use it. However, if that directory doesn't exist, it will download an Indy tarball, unpack it, and use it.

The specific tarball this script tries to download depends on the URL given in the `indy-scripts/start-indy.sh` script.

## Restarting vs. Re-Provisioning

The scripts used to start the various services in the VMs have been separated from the provisioning scripts on purpose, to allow users to reconfigure the VMs in common ways without the need to undergo an expensive re-provisioning step.

## Connecting to Indy from the Host

Once the VMs are started, you should be able to access Indy at `http://192.168.50.3:8080`.
