Vagrant.configure("2") do |config|

  config.vm.define "mac" do |mac|
    mac.vm.box = "jhcook/macos-sierra"
    mac.vm.network "private_network", ip: "192.168.44.100"
  end

  config.vm.define "win" do |win|
    # win.vm.box = "Microsoft/EdgeOnWindows10"    
    # win.vm.box = "ramreddy06/windows7-sp1"    
    # win.vm.box = "opentable/win-7-professional-amd64-nocm"
    win.vm.box = "eyewaretech/windows-10-1709-base-winrm"
    
    win.vm.guest = :windows
    win.vm.communicator = :winrm
    win.winrm.username = "vagrant"
    win.winrm.password = "vagrant"
    win.vm.network "private_network", ip: "192.168.44.101", netmask: "255.255.0.0"

    win.vm.provision :shell, path: "provisioning/win/main.cmd"

    win.vm.provider :virtualbox do |vb|
      vb.gui = true
      vb.memory = 4091
      vb.cpus = 4
      # vb.customize ["modifyvm", :id, "--memory", "4096"]
    end

    
  end
end
