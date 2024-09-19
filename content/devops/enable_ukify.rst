Note to Self: Enabling ukify kernel on Debian
#############################################

:date: 2024-09-19 11:40
:slug: enable_ukify_debian
:tags: debian,systemd,ukify
:author: copyninja
:summary: Enabling the systemd-ukify based booting on Debian

*These steps may not work on your system if you are using default Debian
 installation, this will work only when you are using systemd-boot as bootloader
 in your system, which is explained in this post
 <https://copyninja.in/blog/live_install_debian.html>__*

A unified kernel image (UKI) is a single executable which can be booted directly
from UEFI firmware, or automatically sourced by boot loaders with little or no
configuration. It is the combination of a UEFI boot stub program like
systemd-stub(7), a Linux kernel image, an initrd, and further resources in a
single UEFI PE file.

systemd-boot already ships hook for kernel installation via
*/etc/kernel/postinst.d/zz-systemd-boot*. We only need couple of configuration
to generate the uki image. We need to install *systemd-ukify* package which
provides uki image generator. This can be done with following command.

.. code-block:: sh

    apt-get install systemd-ukify

First write following to */etc/kernel/install.conf*

.. code-block:: conf

    layout=uki
    initrd_generator=dracut
    uki_generator=ukify

The configuration suggests how to generate uki image for given kernel and which
generator to use. ukify is provided by systemd-ukify package.

Next we need to tell what is the kernel command line to be used with uki image.
This can be done by adding */etc/kernel/uki.conf* with following content.

.. code-block:: conf

    [UKI]
    Cmdline=@/etc/kernel/cmdline

Now we need to reconfigure the running kernel to generate uki image for the
kernel. This can be done with following command.

.. code-block:: sh

    dpkg-reconfigure linux-image-`uname -r`


Post running this run the *bootctl list* command and see if you can see *Type
#2* entry for current kernel. Output will looks something like below.

.. code-block::

   bootctl list
         type: Boot Loader Specification Type #2 (.efi)
        title: Debian GNU/Linux trixie/sid (2d0080583f1a4127ac0b073b1a9d3e61-6.10.9-amd64.efi) (default) (selected)
           id: 2d0080583f1a4127ac0b073b1a9d3e61-6.10.9-amd64.efi
       source: /boot/efi//EFI/Linux/2d0080583f1a4127ac0b073b1a9d3e61-6.10.9-amd64.efi
     sort-key: debian
        linux: /boot/efi//EFI/Linux/2d0080583f1a4127ac0b073b1a9d3e61-6.10.9-amd64.efi
      options: systemd.gpt_auto=no quiet root=LABEL=root_disk ro systemd.machine_id=2d0080583f1a4127ac0b073b1a9d3e61

         type: Boot Loader Specification Type #2 (.efi)
        title: Debian GNU/Linux trixie/sid (2d0080583f1a4127ac0b073b1a9d3e61-6.10.7-amd64.efi)
           id: 2d0080583f1a4127ac0b073b1a9d3e61-6.10.7-amd64.efi
       source: /boot/efi//EFI/Linux/2d0080583f1a4127ac0b073b1a9d3e61-6.10.7-amd64.efi
     sort-key: debian
        linux: /boot/efi//EFI/Linux/2d0080583f1a4127ac0b073b1a9d3e61-6.10.7-amd64.efi
      options: systemd.gpt_auto=no quiet root=LABEL=root_disk ro systemd.machine_id=2d0080583f1a4127ac0b073b1a9d3e61

         type: Automatic
        title: Reboot Into Firmware Interface
           id: auto-reboot-to-firmware-setup
       source: /sys/firmware/efi/efivars/LoaderEntries-4a67b082-0a4c-41cf-b6c7-440b29bb8c4f

Once *Type #2* entries are generated make sure to remove unlink *Type #1*
entries using *bootctl unlink* command. Post this you can reboot the system to
boot into UKI based image.

Main usecase of UKI image will be in secure boot. Signing the UKI image can also
be configured in above configuration but I've not done it yet as I've not setup
the secure boot yet on my system.
