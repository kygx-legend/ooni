# Author: legend
# Mail: kygx.legend@gmail.com
# File: docker.py

#!/usr/bin/python
# -*- coding: utf-8 -*-

def install():
    """
    Ref:
    1. https://github.com/dhiltgen/docker-machine-kvm
    2. https://www.howtoforge.com/how-to-install-kvm-and-libvirt-on-centos-6.2-with-bridged-networking
    3. http://blog.arungupta.me/docker-machine-swarm-compose-couchbase-wildfly
    4. https://www.linux.com/learn/how-use-docker-machine-create-swarm-cluster
    5. https://wiredcraft.com/blog/multi-host-docker-network
    6. https://linuxctl.com/2016/02/docker-networking---change-docker0-subnet
    7. http://supercomputing.caltech.edu/blog/index.php/2016/05/03/open-vswitch-installation-on-centos-7-2/
    8. http://docker-k8s-lab.readthedocs.io/en/latest/docker/docker-ovs.html#containers-connect-with-docker0-bridge
    """
    docker = 'brew install --build-from-source --ignore-dependencies docker'
    docker_machine = 'brew install --build-from-source --ignore-dependencies docker-machine'
    docker_machine_driver_kvm = 'curl -L https://github.com/dhiltgen/docker-machine-kvm/releases/download/v0.8.2/docker-machine-driver-kvm > /bin/docker-machine-driver-kvm && chmod +x /bin/docker-machine-driver-kvm'

def create_container():
    create = 'docker-machine create -d kvm --engine-env HTTP_PROXY=http://proxy.cse.cuhk.edu.hk:8000 --engine-env HTTPS_PROXY=https://proxy.cse.cuhk.edu.hk:8000 default'

def run():
    """
    Set no_proxy for the created machine.
    $ export no_proxy=docker-machine-ip
    """

def main():
    pass

if __name__ == "__main__":
    main()
