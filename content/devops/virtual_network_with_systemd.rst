Managing Virtual Network Devices with systemd-networkd
######################################################

:author: copyninja
:date: 2016-01-10 22:26
:slug: systemd-networkd-networking
:tags: systemd-networkd, systemd, networking
:summary: Using systemd-networkd to manage virtual network devices in
          Linux


I've been using bridge networking and tap networking for containers
and virtual machines on my system. Configuration for bridge network
which I use to connect containers was configured using
*/etc/network/interfaces* file as shown below.

.. code-block:: interfaces

   auto natbr0
   iface natbr0 inet static
      address 172.16.10.1
      netmask 255.255.255.0
      pre-up brctl addbr natbr0
      post-down brctl delbr natbr0
      post-down sysctl net.ipv4.ip_forward=0
      post-down sysctl net.ipv6.conf.all.forwarding=0
      post-up sysctl net.ipv4.ip_forward=1
      post-up sysctl net.ipv6.conf.all.forwarding=1
      post-up iptables -A POSTROUTING -t mangle -p udp --dport bootpc -s 172.16.0.0/16 -j CHECKSUM --checksum-fill
      pre-down iptables -D POSTROUTING -t mangle -p udp --dport bootpc -s 172.16.0.0/16 -j CHECKSUM --checksum-fill

Basically I setup masquerading and IP forwarding when network comes up
using this, so all my containers and virtual machines can access
internet.

This can be simply done using systemd-networkd with couple of lines,
yes couple of lines. For this to work first you need to enable
systemd-networkd.

.. code-block:: shell

   systemctl enable systemd-networkd.service

Now I need to write 2 configuration file for the above bridge
interface under */etc/systemd/network*. One file is *natbr0.netdev*
which configures the bridge and the *natbr0.network* which configures
IP address and other stuff for the bridge interface.

.. code-block:: ini

   #natbr0.netdev
   [NetDev]
   Description=Bridge interface for containers/vms
   Name=natbr0
   Kind=bridge

.. code-block:: ini

   #natbr0.network
   [Match]
   Name=natbr0

   [Network]
   Description=IP configuration for natbr0
   Address=172.16.10.1/16
   IPForward=yes
   IPMasquerade=yes

The *IPForward* in above configuration is actually redundant, when I
set *IPMasquerade* it automatically enables IPForward. So these
configuration is equivalent of what I did in my *interfaces* file. It
also avoids me doing additional *iptables* usage to add masquerading
rules. This pretty much simplifies handling of virtual network
devices.

There are many other things which can you do with systemd-networkd,
like running a DHCPServer on the interface and many other things. I
suggest you to read manual pages on *systemd.network(5)* and
*systemd.netdev(5)*.

systemd-networkd allows you configure all type of virtual networking
devices and actual network interfaces. I've not myself used it to
handle actual network interfaces yet.


