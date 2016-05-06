# -*- mode: ruby -*-
# vi: set ft=ruby :

# (c) 2014-2016, Sebastian Schulze <info@bascht.com>
#
# This file is part of eurucamp_transcoder
#
# eurucamp_transcoder is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# eurucamp_transcoder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with eurucamp_transcoder.  If not, see <http://www.gnu.org/licenses/>.

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
