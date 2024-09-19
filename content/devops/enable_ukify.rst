Note to Self: Enabling ukify kernel on Debian
#############################################

:date: 2024-09-19 11:40
:slug: enable_ukify_debian
:tags: debian, systemd, ukify
:author: copyninja
:summary: Enabling systemd-ukify based booting on Debian

*These steps may not work on your system if you are using the default Debian
installation. This guide assumes that your system is using systemd-boot as the
bootloader, which is explained in the post linked below.*

* `Install Debian from grml-liveboot <https://copyninja.in/blog/live_install_debian.html>`__.

A unified kernel image (UKI) is a single executable that can be booted directly
from UEFI firmware or automatically sourced by bootloaders with little or no
configuration. It combines a UEFI boot stub program like
systemd-stub(7), a Linux kernel image, an initrd, and additional resources into
a single UEFI PE file.

systemd-boot already provides a hook for kernel installation via
*/etc/kernel/postinst.d/zz-systemd-boot*. We just need a couple of additional
configurations to generate the UKI image. First, we need to install the
*systemd-ukify* package, which includes the UKI image generator. This can be done
with the following command:

.. code-block:: sh

    apt-get install systemd-ukify

Next, create the following configuration in */etc/kernel/install.conf*:

.. code-block:: conf

    layout=uki
    initrd_generator=dracut
    uki_generator=ukify

This configuration specifies how to generate the UKI image for the installed
kernel and which generator to use. The *ukify* generator is provided by the
*systemd-ukify* package.

Now, we need to define the kernel command line for the UKI image. Add the file
*/etc/kernel/uki.conf* with the following content:

.. code-block:: conf

    [UKI]
    Cmdline=@/etc/kernel/cmdline

To apply these changes, we need to regenerate the UKI image for the currently
running kernel. This can be done using the following command:

.. code-block:: sh

    dpkg-reconfigure linux-image-`uname -r`

After running this command, use the *bootctl list* command to verify the presence
of a *Type #2* entry for the current kernel. The output should look something
like this:

.. code-block:: conf

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

Once the *Type #2* entries are generated, you should remove any *Type #1* entries
using the *bootctl unlink* command. After this, you can reboot your system to
boot from the UKI-based image.

The primary use case for a UKI image is secure boot. Signing the UKI image can
also be configured in the settings above, but I have not done this yet since I
haven’t set up secure boot on my system.
