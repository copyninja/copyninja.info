Taming systemd-nspawn for running containers
############################################

:date: 2015-11-09 12:52
:slug: taming_systemd_nsapwn
:tags: systemd-nspawn, containers, debian
:author: copyninja
:summary: Brief notes on maintaining container using systemd-nspawn

I've been trying to run containers using systemd-nspawn for quite some
time. I was always bumping to one or other dead end. This is not
systemd-nspawn's fault, rather my impatience stopping me from reading
manual pages properly lack of good tutorial like article available
online. Compared to this LXC has a quite a lot of good tutorials and
howto's available online.

This article is my effort to create a notes putting all required
information in one place.


Creating a Debian Base Install
==============================

First step is to have a minimal Debian system some where on your hard
disk. This can be easily done using *debootsrap*. I wrote a custom
script to avoid reading manual every time I want to run
debootstrap. Parts of this script (mostly packages and the root
password generation) is stolen from *lxc-debian* template provided by
lxc package.

.. code-block:: shell

   #!/bin/sh

   set -e
   set -x

   usage () {
       echo "${0##/*} [options] <suite> <target> [<mirror>]"
       echo "Bootstrap rootfs for Debian"
       echo
       cat <<EOF
       --arch         set the architecture to install
       --root-passwd  set the root password for bootstrapped rootfs
       EOF
   }

   # copied from the lxc-debian template
   packages=ifupdown,\
   locales,\
   libui-dialog-perl,\
   dialog,\
   isc-dhcp-client,\
   netbase,\
   net-tools,\
   iproute,\
   openssh-server,\
   dbus

   if [ $(id -u) -ne 0 ]; then
       echo "You must be root to execute this command"
       exit 2
   fi

   if [ $# -lt 2 ]; then
      usage $0
   fi

   while true; do
       case "$1" in
           --root-passwd|--root-passwd=?*)
	       if [ "$1" = "--root-passwd" -a -n "$2" ]; then
	           ROOT_PASSWD="$2"
		   shift 2
	       elif [ "$1" != "${1#--root-passwd=}" ]; then
		   ROOT_PASSWD="${1#--root-passwd=}"
		   shift 1
	       else
		   # copied from lxc-debian template
		   ROOT_PASSWD="$(dd if=/dev/urandom bs=6 count=1 2>/dev/null|base64)"
		   ECHO_PASSWD="yes"
	       fi
	       ;;
           --arch|--arch=?*)
	       if [ "$1" = "--arch" -a -n "$2" ]; then
	           ARCHITECTURE="$2"
		   shift 2
	       elif [ "$1" != "${1#--arch=}" ]; then
	           ARCHITECTURE="${1#--arch=}"
		   shift 1
	       else
	           ARCHITECTURE="$(dpkg-architecture -q DEB_HOST_ARCH)"
	       fi
	       ;;
	   *)
	       break
	       ;;
       esac
   done



   release="$1"
   target="$2"

   if [ -z "$1" ] || [ -z "$2" ]; then
       echo "You must specify suite and target"
       exit 1
   fi

   if [ -n "$3" ]; then
       MIRROR="$3"
   fi

   MIRROR=${MIRROR:-http://httpredir.debian.org/debian}

   echo "Downloading Debian $release ..."
   debootstrap --verbose --variant=minbase --arch=$ARCHITECTURE \
		--include=$packages \
		"$release" "$target" "$MIRROR"

   if [ -n "$ROOT_PASSWD" ]; then
       echo "root:$ROOT_PASSWD" | chroot "$target" chpasswd
       echo "Root password is '$ROOT_PASSWRD', please change!"
   fi

It just gets my needs done, if you don't like it feel free to modify
or use debootstrap directly.

**!NB Please install dbus package in the minimal base install,
otherwise you will not be able to control the container using
machinectl**

Manually Running Container and then persisting it
=================================================

Next we need to run the container manually. This is done by using
following command.

.. code-block:: shell

   systemd-nspawn -bD   /path/to/container --network-veth \
	--network-bridge=natbr0 --machine=Machinename

*--machine* option is not mandatory, if not specified systemd-nspawn
will take the directory name as machine name, and if you have
characters like - in the directory name it translates to hexcode \x2d
and controlling container with name becomes difficult.

*--network-veth* specifies the systemd-nspawn to enable virtual
ethernet based networking and *--network-bridge* tells the bridge
interface on host system to be used by systemd-nspawn. These options
together constitutes *private networking* for container. If not
specified container can use host systems interface there by removing
network isolation of container.

Once you run this command container comes up. You can now run
machinectl to control the container. Container can be persisted using
following command

.. code-block:: shell

   machinectl enable container-name

This will create a symbolic link of
*/lib/systemd/system/systemd-nspawn@service* to
*/etc/systemd/system/machine.target.wants/*. This allows you to start
or stop container using *machinectl* or *systemctl* command. Only
catch here is your base install should be in
*/var/lib/machines/*. What I do in my case is create a symbolic link
from my base container to */var/lib/machines/container-name*.

**!NB Note that symbolic link name under /var/lib/machines should be
same as the container name you gave using --machine switch or the
directory name if you didn't specify --machine**

Persisting Container Networking
===============================

We did persist the container in above step, but this doesn't persist
the networking options we provided in command
line. systemd-nspawn@.service provides following command to invoke
container.

.. code-block:: ini

   ExecStart=/usr/bin/systemd-nspawn --quiet --keep-unit --boot --link-journal=try-guest --network-veth --settings=override --machine=%I

To persist the bridge networking configuration we did in command line,
we need the help of systemd-networkd. So first we need to enable the
systemd-networkd.service on both container and the host system.

.. code-block:: shell
   
   systemctl enable systemd-networkd.service

Now inside the container, interfaces will be named as
*hostN*. Depending on how many interfaces we have N increments. In our
example case we had single interface, hence it will named as
*host0*. By default network interfaces will be down inside container,
hence systemd-networkd is needed to put it up.

We put the following in /etc/systemd/network/host0.network file inside
the container.

.. code-block:: ini

   [Match]
   Name=host0

   [Network]
   Description=Container wired interface host0
   DHCP=yes

And in the host system we just configure the bridge interface using
systemd-nspawn. I put following in *natbr0.netdev* in
/etc/systemd/network/

.. code-block:: ini

   [NetDev]
   Description=Bridge natbr0
   Name=natbr0
   Kind=bridge		

In my case I already had configured the bridge using
*/etc/network/interfaces* file for lxc. I think its not really needed
to use systemd-networkd in this case. Since systemd-networkd doesn't
do anything if network / virtual device is already present I safely
put above configuration and enabled systemd-networkd.

Just for the notes here is my natbr0 configuration in *interfaces*
file.

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

Once this is done just reload the *systemd-networkd* and make sure you
have dnsmasq or any other DHCP server running in your system.

Now the last part is to tell systemd-nspawn to use the bridge
networking interface we have defined. This is done using
*container-name.nspawn* file. Put this file under
*/etc/systemd/nspawn* folder.

.. code-block:: ini

   [Exec]
   Boot=on

   [Files]
   Bind=/home/vasudev/Documents/Python/upstream/apt-offline/

   [Network]
   VirtualEthernet=yes
   Bridge=natbr0

Here you can specify networking, and files mounting section of the
container. For full list please refer the *systemd.nspawn* manual
page.


Now all this is done you can happily do

.. code-block:: shell

   machinectl start container-name
   #or
   systemctl start systemd-nspawn@container-name

Resource Control
================

Now all things said and done, one last part remains. Yes what is the
point if we can't control how much resource does the container
use. Atleast it is more important for me, because I use old and bit
low powered laptop.

Systemd provides way to control the resource using Control
interface. To see all the the interfaces exposed by systemd please
refer *systemd.resource-control* manual page.

The way to control the resource is using *systemctl*. Once container
starts running we can run following command.

.. code-block:: shell

   systemctl set-property container-name CPUShares=200 CPUQuota=30% MemoryLimit=500M

The manual page does say that these things can be put under [Slice]
section of unit files. Now I don't have clear idea if this can be put
under .nspawn files or not. For the sake of persisting the container I
manually wrote the service file for container by copying
systemd-nspawn@.service and adding [Slice]  section. But if I don't
know how to find out if this had any effect or not.

If some one knows about this please share your suggestions to me and I
will update this section with your provided information.

Conclussion
===========

All in all I like systemd-nspawn a lot. I use it to run container for
development of *apt-offline*. I previously used lxc where all can be
controlled using a single config file. But I feel systemd-nspawn is
more tightly integrated with system than lxc.

There is definitely more in systemd-nspawn than I've currently figured
out. Only thing is its not as popular as other alternatives and
definitely lacks good howto documentation.For now only way out is dig
the manual pages, scratch your head, pull your hair out and figure out
new possibilities in systemd-nspawn. ;-)
