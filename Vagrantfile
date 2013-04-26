Vagrant::Config.run do |config|

    config.vm.box = "precise64"
    config.vm.box_url = "http://files.vagrantup.com/precise64.box"

    config.vm.forward_port 8195, 8195
    config.vm.forward_port 80, 8080

    config.vm.host_name = "dev-alpaca"
    config.vm.customize [
        "modifyvm", :id,
        "--memory", "1024",
    ]

    config.vm.provision :shell, :inline => "sudo /usr/bin/apt-get -qq update && sudo /usr/bin/apt-get -qq -y install puppet-common"

    config.vm.provision :puppet do |puppet|
        puppet.manifests_path = "puppet/manifests"
        puppet.manifest_file  = "site.pp"
        puppet.module_path    = [
            "puppet/services",
            "puppet/modules",
        ]
    end

end
