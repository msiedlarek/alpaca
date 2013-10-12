Vagrant.configure("2") do |config|

  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"

  config.vm.provider :virtualbox do |vb|
    vb.customize [
        "modifyvm", :id,
        "--memory", "1024",
    ]
  end

  config.vm.provision :shell, :inline => "dpkg-query -W puppet-common >/dev/null 2>&1 || sudo /usr/bin/apt-get -qq update && sudo /usr/bin/apt-get -qq -y install puppet-common"

  config.vm.provision :puppet do |puppet|
    #puppet.options = "--verbose --debug"
    puppet.manifests_path = "puppet/manifests"
    puppet.manifest_file = "development.pp"
    puppet.module_path = [
      "puppet/services",
      "puppet/modules",
    ]
  end

  config.vm.hostname = "dev-alpaca"
  config.vm.network :private_network, ip: "192.168.60.2"
  config.vm.network :forwarded_port, guest: 8195, host: 8195
  config.vm.network :forwarded_port, guest: 80, host: 8080

end
