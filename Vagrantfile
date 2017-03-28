Vagrant.configure(2) do |config|
  config.vm.define :testnfs do |testnfs|
    testnfs.vm.box = "centos/7"
    testnfs.vm.hostname = "test-nfs.local"

    testnfs.vm.provision :shell, :path => 'provision.sh'

  end
end
