Notes: LXC How-To
#################

:date: 2014-12-26 08:11
:slug: lxc_howto
:tags: lxc, container, debian
:author: copyninja
:summary: A short how to on LXC basics

LXC - Linux Containers allows us to run multiple isolated Linux system
under same control host. This will be useful for testing application
without changing our existing system.

To create an LXC container we use the `lxc-create` command, it can
accepts the template option, with which we can choose the OS we would
like to run under the virtual isolated environment. On a Debian system
I see following templates supported

.. code-block:: shell

   [vasudev@rudra: ~/ ]% ls /usr/share/lxc/templates 
   lxc-alpine*    lxc-archlinux*  lxc-centos*  lxc-debian*    lxc-fedora*  lxc-openmandriva*  lxc-oracle*  lxc-sshd*    lxc-ubuntu-cloud*
   lxc-altlinux*  lxc-busybox*    lxc-cirros*  lxc-download*  lxc-gentoo*  lxc-opensuse*      lxc-plamo*   lxc-ubuntu*

For my application testing I wanted to create a Debian container for
my By default the template provided by lxc package creates Debian
stable container. This can be changed by passing the option to
debootstrap after `--` as shown below.

.. code-block:: shell

   sudo MIRROR=http://localhost:9999/debian lxc-create -t debian \
	-f   container.conf -n container-name -- -r sid

`-r` switch is used to specify the release, MIRROR environment
variable is used to choose the required Debian mirror. I wanted to use
my own local *approx* installation, so I can save some bandwidth.

`container.conf` is the configuration file used for creating the LXC,
in my case it contains basic information on how container networking
should b setup. The configuration is basically taken from `LXC Debian
wiki <https://wiki.debian.org/LXC>`_

.. code-block:: ini

   lxc.utsname = aptoffline-dev
   lxc.network.type = veth
   lxc.network.flags = up
   lxc.network.link = br0.1
   lxc.network.name = eth0
   lxc.network.ipv4 = 192.168.3.2/24
   lxc.network.veth.pair = vethvm1

I'm using VLAN setup described in `Debian wiki: LXC VLAN Networking
<https://wiki.debian.org/LXC/VlanNetworking>`_ page. Below is my
`interfaces` file.

::

   iface eth0.1 inet manual

   iface br0.1  inet manual
      bridge_ports eth0.1
      bridge_fd 0
      bridge_maxwait 0

Before launching the LXC make sure you run below command

.. code-block:: shell

   sudo ifup eth0.1
   sudo ifup br0.1

   # Also give ip to bridge in same subnet as lxc.network.ipv4
   sudo ip addr add 192.168.3.1/24 dev br0.1

I'm giving ip address to bridge so that I can communicate with
container from my control host, once it comes up.

Now start the container using below command

.. code-block:: shell

   sudo lxc-start -n container -d -c tty8

We are starting lxc in daemon mode and attaching it to console
`tty8`. If you want, you can drop -d and -c option to start lxc in
foreground. But its better you start it in background and attach using
`lxc-console` command shown below.

.. code-block:: shell

   sudo lxc-console -n container -t tty8

You can detach from console using `Ctrl+a q` combination and let lxc
execute in background.

Its also possible to simply ssh into the running container since we
have enabled networking.
   
Stopping the container should be done using `lxc-stop` command, but
without `-k` switch (kill) this command never returned. Even with
timeout container is not stopped.

.. code-block:: shell

   sudo lxc-stop -n container

`-r` can be used for reboot of container. Since I couldn't get clean
shutdown I normally attach the console and issue a `halt` command in
container itself. Not sure if this is the right way, but it gets the
thing done.

I consider Linux container as a better alternative for spawning a
virtual Linux environment instead of running a full blown VM like
Virtualbox or VMware.
