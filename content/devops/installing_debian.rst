Installing Debian from GRML Live CD
###################################

:date: 2022-12-12 12:35
:slug: live_install_debian
:tags: debian,live,grml,systemd-boot,btrfs
:author: copyninja
:summary: New experiment to install Debian from GRML Live boot

I had bought a Thinkpad E470 laptop back in 2018 which was lying unused for
quite some time. Recently when I wanted to use it, I found that the keyboard is
not working, especially some keys and after some time the laptop will hang in
Lenovo boot screen. I came back to Bangalore almost after 2 years from my
hometown (WFH due to Covid) and thought it was the right time to get my laptop
back to normal working state. After getting the keyboard replaced I noticed that
1TB HDD is no longer fast enough for my taste!. I've to admit I never thought I
would start disliking HDD so quickly thanks to modern SSD based work laptops. So
as a second upgrade I got the HDD removed from my laptop and got a 240G SSD.
Yeah I know its reduction from my original size but I intend to continue using
my old HDD via USB SATA enclosure as an external HDD which can house the extra
data which I need to save.


So now that I've a SSD I need to install Debian Unstable again on it and this is
where I tried something new. My colleague (name redacted on request) suggested
to me use GRML live CD and install Debian via *debootstrap*. And after giving a
thought I decided to try this out. Some reason for going ahead with this are
listed below


1. Debian Installer does not support a proper BTRFS based root file system. It
   just allows btrfs as root but no subvolume support. Also I'm not sure about
   the luks support with btrfs as root.

2. I also wanted to give a try to systemd-boot as my laptop is UEFI capable and
   I've slowly started disliking Grub.

3. I really hate installing task-kde-desktop (Yeah you read it right, I've switched
   to be a KDE user for quite some time) which will pull tons of unwanted stuff
   and bloat. Well it's not just task-kde-desktop but any other task-desktop
   package does similar and I don't want to have too much of unused stuff and
   services running.


Disk Preparation
================

As a first step I went to GRML website and downloaded `current pre-release
<https://grml.org/download/prerelease/>`_. Frankly, I'm using GRML for first
time and I was not sure what to expect. When I booted it up I was bit taken a
back to see its console based and I did not have a wired lan just a plain
wireless dongle (Jiofi device) and was wondering what it will take to connect.
But surprisingly curses based UI was pretty much straight forward to allow me to
connect to Wifi AP. Another thing was the rescue CD had non-free firmware as the
laptop was using ath10k device and needed non-free blobs to operate.

Once I got shell prompt in rescue CD first thing I did was to reconfigure
console-setup to increase  font size which was very very small on default boot.
Once that is done I did the following to create a 1G (FAT32) partition for EFI.

.. code-block:: shell

   parted -a optimal -s /dev/sda mklabel gpt
   parted -a optimal -s /dev/sda mkpart primary vfat 0% 1G
   parted -a optimal -s /dev/sda set 1 esp on
   mkfs.vfat -n boot_disk -F 32 /dev/sda1

So here is what I did: created a 1G vfat type partition and set the esp flag on
it. This will be mounted to /boot/efi for systemd-boot. Next I created a single
partition on the rest of the available free disk which will be used as the root
file system.

Next I encrypted the root parition using LUKS and then created the BTRFS file
system on top of it.

.. code-block:: shell

   cryptsetup luksFormat /dev/sda2
   cryptsetup luksOpen /dev/sda2 ENC
   mkfs.btrfs -L root_disk /dev/mapper/ENC


Next is to create subvolumes in BTRFS. I followed suggestion by colleague and
created a top-level *@* as subvolume below which created *@/home* *@/var/log* *@/opt* .
Also enabled compression with zstd and level of 1 to avoid battery drain.
Finally marked the *@* as default subvolume to avoid adding it to fstab entry.

.. code-block:: shell

   mount -o compress=zstd:1 /dev/mapper/ENC /mnt
   btrfs subvol create /mnt/@
   cd /mnt/@
   btrfs subvol create ./home
   btrfs subvol create ./opt
   mkdir -p var
   btrfs subvol create ./var/log
   btrfs suvol set-default /mnt/@


Bootstrapping Debian
====================

Now that root disk is prepared next step was to bootstrap the root file system.
I used debootstrap for this job. One thing I missed here from installer was
ability to preseed. I tried looking around to figure out if we can preseed
debootstrap but did not find much. If you know the procedure do point it to me.


.. code-block:: shell

    cd /mnt/
    debootstrap --include=dbus,locales,tzdata unstable @/ http://deb.debian.org/debian

Well this just gets a bare minimal installation of Debian I need to install rest
of the things post this step manually by chroot into target folder @/.

I like the **grml-chroot** command for chroot purpose, it does most of the job of
mounting all required directory like /dev/ /proc /sys etc. But before entering
chroot I need to mount the ESP partition we created to **/boot/efi** so that I
can finalize the installation of kernel and **systemd-boot**.

.. code-block:: shell

	umount /mnt
	mount -o compress=zstd:1 /dev/mapper/ENC /mnt
	mkdir -p /mnt/boot/efi
	mount /dev/sda1 /mnt/boot/efi
	grml-chroot /mnt /bin/bash

I remounted the root subvolume *@* directly to /mnt now, remember I made *@* as
default subvolume before. I also mounted ESP partition with FAT32 file system to
*/boot/efi*. Finally I used grml-chroot to get into chroot of newly bootstrapped
file system.

Now I will install the kernel and minimal KDE desktop installation and configure
locales and time zone data for the new system. I wanted to use dracut instead of
default initramfs-tools for initrd. I also need to install cryptsetup and
btrfs-progs so I can decrypt and really boot into my new system.

.. code-block:: shell

	apt-get update
	apt-get install linux-image-amd64 dracut openssh-client \
				kde-plasma-desktop plasma-workspace-wayland \
				plasma-nm cryptsetup btrfs-progs sudo

Next is setting up crypttab and fstab entries for new system. Following entry is
added to fstab

::

	LABEL="root_disk" / btrfs defaults,compress=zstd:1 0 0

And the crypttab entry

::

	ENCRYPTED_ROOT UUID=xxxx none discard,x-initrd.attach

I've not written actual UUID above this is just for the purpose of showing the
content of /etc/crypttab. Once these entries are added we need to recreate
initrd. I just reconfigured the installed kernel package for retriggerring the
recreation of initrd using dracut.
..
Reconfiguration was locales is done by editing /etc/locales.gen to uncomment
*en_US.UTF-8* and writing /etc/timezone with *Asia/Kolkata*. I used
*DEBIAN_FRONTEND=noninteractive* to avoid another prompt asking for locale and
timezone information.

.. code-block:: shell

	export DEBIAN_FRONTEND=noninteractive
	dpkg-reconfigure locales
	dpkg-reconfigure tzdata

Added my user using *adduser* command and also set the root password as well.
Added my user to *sudo* group so I can use sudo to elevate privileges.


Setting up systemd-boot
=======================

So now basic usable system is ready last part is enabling the systemd-boot
configuration as I'm not gonna use grub. I did following to install
systemd-boot. Frankly I'm not expert of this it was colleague's suggestion.

Before installing the systemd-boot I had to setup kernel command line. This can
be done by writing command line to /etc/kernel/cmdline with following contents.

::

   systemd.gpt_auto=no quiet root=LABEL=root_disk

I'm disabling systemd-gpt-generator to avoid race condition between crypttab
entry and auto generated entry by systemd. I faced this mainly because of my
stupidity of not adding entry *root=LABEL=root_disk*

.. code-block:: shell

	apt-get install -y systemd-boot
	bootctl install --make-entry-directory=yes --entry-token=machine-id
	dpkg-reconfigure linux-image-6.0.0-5-amd64

Finally exit from the chroot and reboot into the freshly installed system.

*systemd-boot* already ships a hook file *zz-systemd-boot* under */etc/kernel*
so its pretty much usable without any manual intervention. Previously after
kernel installation  we had to manually update kernel image in efi partitions
using *bootctl*

Conclussion
===========

Though installing from live image is not new and debian-installer also does the
same only difference is more control over installation and doing things which is
installer is not letting you do (or should I say is not part of default
installation?). If properly automated using scripts we can leverage this to do
custom installation in large scale environments. I know there is FAI but I've
not explored it and felt there is too much to setup for a simple installations
with specific requirements.

So finally I've a system with Debian which differs from default Debian
installation :-). I should thank my colleague for rekindling nerd inside me who
had stopped experimenting quite a long time back.
