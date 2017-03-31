# Multibuild script for Maven Projects

This setup is intended to run multiple builds against a specific Indy instance.

## User Input

The user must provide the following:

* A project to build, normally in the `./project` directory (or you can specify a different directory)
* An Indy URL, with httprox enabled and everything setup to work with the `public` group

## Using with the Vagrant VMs

To use this with the Vagrant configuration contained in this project, run the VMs. You can use the instructions in
the root README to fine-tune these VMs for your test.

Use `vagrant ssh-config client` in the root directory of this repository to get the host IP address for the Indy
instance. Once you have this, you can use `http://<IP>:8080` as the Indy URL for input into the multibuild script.

## Example

Starting from the project root directory (directory above this one):

```
    $ vagrant up
    $ export INDY=$(vagrant ssh-config client | grep HostName | awk '{print $2}')

    [CONNECT TO INDY UI AT http://${INDY}:8080 and configure it appropriately]

    $ cd multibuild
    $ git clone https://github.com/Commonjava/indy project
    $ ./multibuild.py -b 4 -t 2 -P 8081 http://${INDY}L:8080

    [BUILDS RUN]
```

