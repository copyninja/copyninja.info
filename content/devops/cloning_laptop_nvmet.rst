Cloning a laptop over NVME TCP
##############################

:date: 2024-03-10 15:50
:slug: clone_laptop_nvmet
:tags: debian, nvmet, clone
:author: copyninja
:summary: Cloning old laptoip over NVME TCP

Recently I got a new laptop and had to set it up so I can start using it. But I
was really not in mood to do the same old steps which I had explained in this
`post earlier <https://copyninja.in/blog/live_install_debian.html>`_.  I was
cribbing about this to my colleague, and there came the suggestion of why not
copy entire disk to new laptop. Though it sounded like interesting thing to me I
had my doubts so here is what I told him in return.

1. I don't have tools to open my old laptop and connect new disk over USB to my
   new laptop
2. I use full disk encryption and my old laptop is 512G where as new laptop is
   1T NVME and I'm not so familiar with resizing LUKS

He promptly suggested both can be done for step 1 just expose the disk using
NVME over TCP and connect it over network and do a full disk copy and rest is
pretty simple to achive. In short he suggested following

1. Export  disk using nvmet-tcp from old laptop
2. Do a disk copy to new laptop
3. Do a partition resize to use full 1T
4. Do luks resize
5. And finally do btrfs reszie of root disk

Exporting Disk over NVME TCP
============================

Easiest way suggested by my colleague to do is using `systemd-storagetm.service
<https://www.freedesktop.org/software/systemd/man/latest/systemd-storagetm.service.html>`_.
This service can be invoked by simply booting into *storage-target-mode.target*
by specifying *rd.systemd.unit=storage-target-mode.target*. But he suggested not
to use this as I need to tweak the dracut initrd image to involve network
services as well as configuring wifi from this mode is painful thing to do.

So alternatively I simply booted both my laptops with GRML rescue CD. And
following step was done to export the nvme disk on my current laptop using
nvmet-tcp module of Linux

.. code-block:: shell

   modprobe nvemt-tcp
   cd /sys/kernel/config/nvmet
   mkdir ports/0
   cd ports/0
   echo "ipv4" > addr_adrfam
   echo 0.0.0.0 > addr_traaddr
   echo 4420 > addr_trsvcid
   echo tcp > addr_trtype

   cd /sys/kernel/config/nvmet/subsystems
   mkdir testnqn
   echo 1 testnqn/allow_any_host
   mkdir testnqn/namespaces/1

   cd testnqn
   # replace the devie name with disk you want to export
   echo "/dev/nvme0n1" > namespaces/1/device_path
   echo 1 > namespaces/1/enable

   ln -s "../../subsystems/testnqn" /sys/kernel/config/nvmet/ports/0/subsystems/testnqn

These steps make sure the device is now exported usingNVME over TCP. Next is to
detec this on the new laptop and connect the device

.. code-block:: shell

   nvme discover -t tcp -a <ip> -s 4420
   nvme connectl-all -t tcp -a <> -s 4420

Finally *nvme list* shows the device which is connected to the new laptop and we
can go ahead with next step that is o do disk copy.

Copying the Disk
================

I simply used dd command to copy the root disk to my new laptop. Since new
laptop didn ot had ethernet port I had t oonly rely on Wifi and it took about 7
and half hour to copy entire 512G to new laptop. Speed with which I was copying
was about 18-20MB/s. The other option would have been to create initial
partition and file system and do rsync of root disk or use btrfs itself for file
system transfer.

.. code-block:: shell

    dd if=/dev/nvme2n1 of=/dev/nvme0n1 status=progress bs=40M

Resizing partition and LUKS container
#####################################

The final part was very easy when I launched parted it detected that partition
table does not match disk size and asked if it can fix it and I said yes. Next I
had to install *cloud-guest-utils* to get *growpart* to fix the second partition
and following command extended the partition to full 1T

.. code-block:: shell

    growpart /dev/nvem0n1 p2

Next used *cryptsetup-resize* to incrrease the LUKS container size.

.. code-block:: shell

    cryptsetup luksOpen /dev/nvme0n1p2 ENC
    cryptsetup rezize ENC

Finally rebooted into the disk and everyting worked fine post logging into the
system did resize of BTRFS file system. BTRFS requires system to be mounted for
resize so could not attempt it in live boot.

.. code-block:: shell

    btfs fielsystem resize max /

And now I'm writing this blog from my newlaptop without needing to do any
resetup or reinstallation of software. Even though copy takes a while I did not
spending more than an hour to do this entire stuff and a lot of time is saved by
not having to re-install every software you need and reconfigure it to original
settings and it will definitely take a week for you to adjust to your new laptop
