Installing and Configuring NetBSD on Qemu in Debian
###################################################

:date: 2014-03-01 22:10
:slug: netbsd-on-qemu
:tags: debian, netbsd, qemu, vde, networking
:author: copyninja
:summary: An introduction to installing NetBSD on Qemu and enabling
	  networking on a Debian host.

First step will be getting a NetBSD ISO image for installation
purpose. It can be downloaded from `here
<http://www.netbsd.org/mirrors/torrents/#6.1.3-ports>`_.

Next step will be creating a disk image for installing NetBSD. This is
done using ``qemu-img`` tool like below

.. code-block:: shell-session

   $ qemu-img create -f raw netbsd-disk.img 10G

Image format used is *raw* and size is specified as last
arugment. Tune the size as per your need.

To start the installation run the following command

.. code-block:: shell-session

   $ qemu-system-x86_64 -m 256M -hda netbsd-disk.img -cdrom \
		NetBSD-6.1.3-amd64.iso -display curses -boot d \
		-net nic -net user

So this is using user mode networking so you won't be able to have
internet access during installation. I couldn't figure out on how to
get network working during installation so I configured network after
installation.

Once you run above command you will be given with 4 options as
follows.

1. install netbsd
2. install netbsd with ACPI disabled
3. install netbsd with ACPI and SMP disabled
4. drop to boot shell

Even though I first installed using the option 1 I couldn't get it
boot after installation so had to reinstall with option 2 and it works
fine. I'm not gonna explain each step of installation here because the
installer is really simple and straight forward! I guess the NetBSD
installer is the first simplest installer I have encountered from the
day I started with Linux. Its simple but powerful and gets job done
very easily, and I didn't read manual for installation before using
it.


Enabling Networking
-------------------

This section involves mixture of configuration in Debian host and
inside NetBSD to get the network working. The wiki page of Debian on
`Qemu <https://wiki.debian.org/QEMU#Networking>`_. helped me here.

To share the network with Qemu there are 2 possiblities

1. Bridged networking between host and guest using *bridge-utils*
2. Using VDE *(Virtual Distributed Ethernet)*

The option 1 which is explained in wiki linked above didn't work for
me as I use CDC Ether based datacard for connecting to Internet which
gets detected as *eth1* on my machine. When bridging happens between
*tap0* and *eth1* I end up loosing Internet on my host machine. So I
selected to use VDE instead.

First install packages *vde2* and *uml-utilities* once done edit the
*/etc/network/interfaces* file and add following lines::

   auto vdetap
   iface vdetap inet static
      address 192.168.2.1
      netmask 255.255.255.0
      vde2-switch -t vdetap

We can use *dnsmasq* as a DHCP server for the *vdetap* interface, but
I'm not gonna explain the configuration of *dnsmasq* here. Run the
below command to get vdetap up

.. code-block:: shell-session

   modprobe tun
   ifup vdetap
   /etc/init.d/dnsmasq restart 
   newgrp vde2-net # run as user starting Qemu VM's

I couldn't get successful output for *newgrp* command, I was getting
some ``crypt: Invalid argument`` output. But I could still get
network working on NetBSD so I considered to ignore that for now.

Now start the NetBSD qemu instance running using following command

.. code-block:: shell-session

   $ qemu-system-x86_64 -m 256M -hda \
		/mnt/kailash/BSDWorld/netbsd-disk.img \
		-net nic -net vde,sock=/var/run/vde2/vdetap.ctl -display curses

Once the system is up login using *root* user, NetBSD will warn you
for this and suggest to create another user but for now ignore
it. To find the network interface in NetBSD just run the usual
*ifconfig* command. In my case interface is named *wm0*.

First step will be configuring the IP address for your interface and
setting up the gateway route. Run the below command for this purpose

.. code-block:: shell-session

   # ifconfig wm0 192.168.2.2 netmask 255.255.255.0
   # route add default 192.168.2.1

Note that I added gateway as IP address of vdetap on my host
machine. Now try pinging the host and even you can try ssh to host
system.

But note that this is not persistent over the reboots and for some
reason I didn't yet figure out how to make NetBSD get address over
DHCP from my host machine. I will update once I figure it out. Now to
make the connection address persistent over reboots you need to create
a file by name */etc/ifconfg.<interface>*. Replace *interface* with a
proper interface on your running NetBSD. In my case this file is
*/etc/ifconfig.wm0* and has following content.::

  192.168.2.2 netmask 0xffffff00 media autoselect

Set the DNS server as host by adding file */etc/resolv.conf* with
following content.::

  nameserver 192.168.2.1

After this you need to do NAT/masquerading using iptables. Just copy
following script to a file and execute it as root

.. code-block:: shell

   #!/bin/sh

   # Restart the dnsmasq
   /etc/init.d/dnsmasq restart
	 
   # Set nat rules in iptables
   iptables --flush
   iptables --table nat --flush
   iptables --delete-chain
   iptables --table nat --delete-chain
	 
   # Replace accordingly usb0 with ppp0 for 3G
   iptables --table nat --append POSTROUTING --out-interface eth1 -j MASQUERADE
   iptables --append FORWARD --in-interface vdetap -j ACCEPT
	 
   # Enable IP forwarding in Kernel
   sysctl -w net.ipv4.ip_forward=1
   

With the above setup you will be able to get DNS resolution even after
you reboot the Qemu instance but Internet connection will not work
untill you run the ``route`` command I mentioned above. I still didn't
figure out how to persist route but I will update it here once I
figure it out.

  Note that you won't be able to SSH as root to NetBSD (may be its
  configured to not allow by default), so you would need to create a
  normal user before trying to SSH from host to guest. Also make sure
  you add the user to *wheel* group to allow him execute su command.

So now I've NetBSD running on my laptop with mere 256M ram and its
amazingly fast even at such low RAM. I've created a new user and can
SSH into it from host machine and use it just like I use a
server!. I will put up the notes of my BSD adventure here
periodically.

The feeling of using a BSD is amazing :-)

  **Update**: I forgot to add masquerading step, I've added it
  now.
