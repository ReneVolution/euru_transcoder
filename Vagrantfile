# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", "2048"]
    vb.customize ["modifyvm", :id, "--cpus", "4"]   
  end  

  config.vm.provider :aws do |aws, override|
    aws.ami               = 'ami-076ca270'
    aws.region            = 'eu-west-1'
    aws.instance_type     = 'c3.8xlarge'
    aws.access_key_id     = ENV['AWS_ACCESS_KEY_ID']
    aws.secret_access_key = ENV['AWS_SECRET_ACCESS_KEY']
    aws.keypair_name      = ENV['AWS_KEYPAIR_NAME']

    override.ssh.private_key_path = ENV['AWS_PRIVATE_KEY']
    override.vm.box = "dummy"
    override.vm.box_url = 'https://github.com/mitchellh/vagrant-aws/raw/master/dummy.box'
    override.ssh.username = 'ubuntu'
   end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = 'playbook.yml'
    ansible.verbose = false
  end
end
