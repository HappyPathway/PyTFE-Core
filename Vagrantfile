# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.define "jupyter" do |jupyter|
    jupyter.vm.network "forwarded_port", guest: 8888, host: 8888
    jupyter.vm.provision "shell", inline: "rm /etc/profile.d/vault.sh || echo"
    jupyter.vm.provision "shell", inline: "echo export VAULT_ADDR=#{ENV['VAULT_ADDR']} >> /etc/profile.d/vault.sh"
    jupyter.vm.provision "shell", inline: "echo export VAULT_TOKEN=#{ENV['VAULT_TOKEN']} >> /etc/profile.d/vault.sh"
    jupyter.vm.provision "shell", inline: <<-SHELL
       apt-get update
       apt-get install -y python3-pip ipython3 ipython3-notebook
       pip3 install jupyter
       cd /vagrant; python3 setup.py install
       cd /vagrant/notebooks; jupyter notebook --allow-root --ip=0.0.0.0
    SHELL
  end
  config.vm.define "pypi" do |pypi|
    pypi.vm.provision "shell", inline: "rm /etc/profile.d/vault.sh || echo"
    pypi.vm.provision "shell", inline: "echo export VAULT_ADDR=#{ENV['VAULT_ADDR']} >> /etc/profile.d/vault.sh"
    pypi.vm.provision "shell", inline: "echo export VAULT_TOKEN=#{ENV['VAULT_TOKEN']} >> /etc/profile.d/vault.sh"
    pypi.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install -y python3-pip ipython3 ipython3-notebook
      pip3 install tfe
    SHELL
  end
end
