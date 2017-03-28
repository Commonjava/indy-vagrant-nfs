Vagrant.configure(2) do |config|
  config.vm.define :nfs do |nfs|
    nfs.vm.box = "centos/7"
    nfs.vm.hostname = "nfs.local"

    nfs.vm.provision :shell, :path => 'provision-nfs.sh'
  end
  config.vm.define :nfs do |client|
    client.vm.box = "centos/7"
    client.vm.hostname = "client.local"

    client.vm.provision :shell, :path => 'provision-client.sh'
  end
end
