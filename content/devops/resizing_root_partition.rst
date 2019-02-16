Note to Self: Growing the Root File System on First Boot
########################################################

:date: 2019-02-16 22:13 +0530
:slug: grow_rootfs
:tags: resize2fs, notetoself
:author: copyninja
:summary: Post discusses about expanding root file system of a system to full
          extent of available space in device.

These 2 are the use cases I came across for expanding root file system.

1. RaspberryPi images which comes in smaller image size like 1GB which you write
   bigger size SD cards like 32GB but you want to use full 32GB of space when
   system comes up.

2. You have a VM image which is contains basic server operating system and you want
   to provision the same as a VM with much larger size root file system.

My current use case was second but I learnt the trick from 1, that is the
`RaspberryPi3 image spec <https://github.com/Debian/raspi3-image-spec>`_ by
Debian project.

Idea behind the expanding root file system is first expanding the root file
system to full available size and then run resize2fs on the expanded partition
to grow file system. *resize2fs* is a tool specific for ext2/3/4 file system.
But this needs to be done before the file system is mounted.

Here is my modified script from `raspi3-image-spec repo
<https://github.com/Debian/raspi3-image-spec/blob/master/rpi3-resizerootfs>`_.
Only difference is I've changed the logic of extracting root partition device to
my need, and of course added comments based on my understanding.

.. code:: shell

   #!/bin/sh

   # Just extracts root partition and removes partition number to get the device
   # name eg. /dev/sda1 becomes /dev/sda
   roottmp=$(lsblk -l -o NAME,MOUNTPOINT | grep '/$')
   rootpart=/dev/${roottmp%% */}
   rootdev=${rootpart%1}

   # Use sfdisk to extend partition to all available free space on device.
   flock $rootdev sfdisk -f $rootdev -N 2 <<EOF
   ,+
   EOF

   sleep 5

   # Wait for all pending udev events to be handled
   udevadm settle

   sleep 5

   # detect the changes to partition (we extended it).
   flock $rootdev partprobe $rootdev

   # remount the root partition in read write mode
   mount -o remount,rw $rootpart

   # Finally grow the file system on root partition
   resize2fs $rootpart

   exit 0fs


raspi3-image-spec uses `sytemd service
<https://github.com/Debian/raspi3-image-spec/blob/master/rpi3-resizerootfs.service>`_
file to execute this script just before any file system is mounted. This is done
by a making service execute before *local-fs.pre* target. From the man page for
*systemd.special*

   local-fs.target
       systemd-fstab-generator(3) automatically adds dependencies of type
       Before= to all mount units that refer to local mount points for this
       target unit. In addition, it adds dependencies of type Wants= to this
       target unit for those mounts listed in /etc/fstab that have the auto
       mount option set.

Service also disables itself on executing to avoid re-runs on every boot. I've
used the service file from raspi3-image-spec as is.

Testing with VM
===============

*raspi3-image-spec* is well tested, but I wanted to make sure this works with my
use case for VM. Since I didn't have any spare physical disks to experiment with
I used kpartx with raw file images. Here is what I did

1. Created a stretch image using vmdb2 with grub installed. Image size is 1.5G
2. I created another raw disk using fallocate of 4G size.
3. I created a partition on 4G disk.
4. Loop mounted the disk and wrote 1G image on it using dd
5. Finally created a VM using virt-install  with this loop mounted device as
   root disk.

Below is my vmdb configuration yml again derived from `raspi3-image-spec
<https://github.com/Debian/raspi3-image-spec/blob/master/raspi3.yaml>`_ one with
some modifications to suit my needs.

.. code:: yaml

   # See https://wiki.debian.org/RaspberryPi3 for known issues and more details.
   steps:
   - mkimg: "{{ output }}"
     size: 1.5G

   - mklabel: msdos
     device: "{{ output }}"

   - mkpart: primary
     device: "{{ output }}"
     start: 0%
     end: 100%
     tag: /

   - kpartx: "{{ output }}"

   - mkfs: ext4
     partition: /
     label: RASPIROOT

   - mount: /

   - unpack-rootfs: /

   - debootstrap: stretch
     mirror: http://localhost:3142/deb.debian.org/debian
     target: /
     variant: minbase
     components:
     - main
     - contrib
     - non-free
     unless: rootfs_unpacked

   # TODO(https://bugs.debian.org/877855): remove this workaround once
   # debootstrap is fixed
   - chroot: /
     shell: |
       echo 'deb http://deb.debian.org/debian buster main contrib non-free' > /etc/apt/sources.list
       apt-get update
     unless: rootfs_unpacked

   - apt: install
     packages:
     - ssh
     - parted
     - dosfstools
     - linux-image-amd64
     tag: /
     unless: rootfs_unpacked

   - grub: bios
     tag: /

   - cache-rootfs: /
     unless: rootfs_unpacked

   - shell: |
        echo "experimental" > "${ROOT?}/etc/hostname"

        # '..VyaTFxP8kT6' is crypt.crypt('raspberry', '..')
        sed -i 's,root:[^:]*,root:..VyaTFxP8kT6,' "${ROOT?}/etc/shadow"

        sed -i 's,#PermitRootLogin prohibit-password,PermitRootLogin yes,g' "${ROOT?}/etc/ssh/sshd_config"

        install -m 644 -o root -g root fstab "${ROOT?}/etc/fstab"

        install -m 644 -o root -g root eth0 "${ROOT?}/etc/network/interfaces.d/eth0"

        install -m 755 -o root -g root rpi3-resizerootfs "${ROOT?}/usr/sbin/rpi3-resizerootfs"
        install -m 644 -o root -g root rpi3-resizerootfs.service "${ROOT?}/etc/systemd/system"
        mkdir -p "${ROOT?}/etc/systemd/system/systemd-remount-fs.service.requires/"
        ln -s /etc/systemd/system/rpi3-resizerootfs.service "${ROOT?}/etc/systemd/system/systemd-remount-fs.service.requires/rpi3-resizerootfs.service"

        install -m 644 -o root -g root rpi3-generate-ssh-host-keys.service "${ROOT?}/etc/systemd/system"
        mkdir -p "${ROOT?}/etc/systemd/system/multi-user.target.requires/"
        ln -s /etc/systemd/system/rpi3-generate-ssh-host-keys.service "${ROOT?}/etc/systemd/system/multi-user.target.requires/rpi3-generate-ssh-host-keys.service"
        rm -f ${ROOT?}/etc/ssh/ssh_host_*_key*

     root-fs: /

   # Clean up archive cache (likely not useful) and lists (likely outdated) to
   # reduce image size by several hundred megabytes.
   - chroot: /
     shell: |
        apt-get clean
        rm -rf /var/lib/apt/lists

   # TODO(https://github.com/larswirzenius/vmdb2/issues/24): remove once vmdb
   # clears /etc/resolv.conf on its own.
   - shell: |
        rm "${ROOT?}/etc/resolv.conf"
     root-fs: /

I could not run with vmdb2 installed from Debian archive, so I cloned
raspi3-image-spec and used vmdb2 submodule from it. And here are rest of
commands used for testing the script.

.. code:: shell

   fallocate -l 4G rootdisk.img
   # Create one partition with full disk
   sfdisk -f rootdisk.img <<EOF
   ,+
   EOF
   kpartx -av rootdisk.img # mounts on /dev/loop0 for me
   dd if=vmdb.img of=/dev/loop0
   sudo virt-install --name experimental --memory 1024 --disk path=/dev/loop0 --controller type=scsi,model=virtio-scsi --boot hd --network bridge=lxcbr0

Once VM booted I could see the root file system is 4G of size instead of 1.5G it
was after using dd to write image on to it. So success!.
