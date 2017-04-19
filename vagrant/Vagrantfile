Vagrant.configure(2) do |config|
  config.vm.define :nfs do |nfs|
    nfs.vm.box = "centos/7"
    nfs.vm.hostname = "nfs.local"

    nfs.vm.provision :shell, :path => 'provision-nfs.sh'

    nfs.vm.network :private_network, :ip => '192.168.50.2', :netmask => '255.255.255.0', :gateway => '192.168.50.1'
  end
  config.vm.define :indy, :primary => true do |indy|
    indy.vm.box = "centos/7"
    indy.vm.hostname = "indy.local"

    indy.vm.provision :shell, :path => 'provision-indy.sh'

    indy.vm.network :private_network, :ip => '192.168.50.3', :netmask => '255.255.255.0', :gateway => '192.168.50.1'

    # indy.vm.provider :virtualbox do |v|
    #   v.memory = 2048
    #   v.cpus = 4
    # end
    indy.vm.provider :libvirt do |libvirt|
      libvirt.memory=2048
      libvirt.cpus=4
    end
  end
end
