Note to Self: Enabling the secureboot with UKI on Debian
########################################################

:date: 2024-09-24 11:30
:slug: enable_secureboot_ukify
:tags: debian, secureboot, systemd, uki
:author: copyninja
:summary: Post explains how to enable self signed secureboot with UKI on Debian

.. note::
   *This post is continuation from my previous post on enabling the UKI image
   on Debian.*

* `Enabling Unified Kernel Image on Debian
  <https://copyninja.in/blog/enable_ukify_debian.html>`_

In the secure boot mode, I will be taking full control of device by removing
any preinstalled keys and installing my own key. This post from `rodsbooks
<https://www.rodsbooks.com/efi-bootloaders/controlling-sb.html>`_ gives a good
idea of benifits of this as well as entire process.

For the process we need following 3 keys
 1. Platform Key (PK): Is the top-level key in the secure boot and is normally
    provided by motherboard manufacturer and for controlling the entire secure
    boot process its important to replace this vendor supplied PK with our own
    PK.
 2. Key Exchange Key (KEK): Keys used to sign Signatures Database and Forbidden
    Signatures Database updates.
 3. Database Key (DB): This is the key used to sign or verify binaries
    (bootloaders, boot managers, shells, drivers etc.)

There is also Forbidden Signature Key (dbx) which is opposite to what db key
does. We will not be generating this key.

For enrolling the keys, we need to first put the device in *Secure Boot Setup
Mode* once done the status can be checked using `bootctl status` command and you
should see something similar to below image.

.. image:: {static}/images/uefi_setupmode.png

I followed `these instructions
<https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot#Creating_keys>`_
from here to generate the keys manually. We would require `efitools` and
`openssl` package for this step. I used `rsa:2048` as the key size instead of
`rsa:4096`, reason being just to be on safer side as some old firmware might not
support 4096 bit keys.

Once you have followed the Arch wiki link above to generate your keys you need
to copy all the *.auth* keys to */efi/loader/keys/<hostname>/* folder. In my
case its following

.. code-block:: sh

   ❯ sudo ls /efi/loader/keys/chamunda
   db.auth  KEK.auth  PK.auth


Next up is signing the *systemd-boot* bootloader with our new keys This can be
done with following command.

.. code-block:: sh

   sbsign --key <path-to db.key> --cert <path-to db.crt> \
      /usr/lib/systemd/boot/efi/systemd-bootx64.efi

Once signing is done you will see a file *systemd-bootx64.efi.signed* in the
same location as above. This needs to be installed using *bootctl install*
command. You will see something like below.

.. image:: {static}/images/bootctl_install.png

.. note::

   *My original installation post was using /boot/efi, I just remounted it
   to /efi here. The warnings are because it was not mounted with umask=0077.
   After the warning I updated fstab to have this option and post that the
   warning goes away.*

We can now verify if its signed with out keys using *sbsign --verify* command
and output is seen below.

Next up is adding the key in uki.conf which we created for generating UKI image.
Add following 2 lines to */etc/kernel/uki.conf*.

.. code-block:: conf

   SecureBootPrivateKey=/path/to/db.key
   SecureBootCertificate=/path/to/db.crt

Generally running `kernel-install -v add-all` should work, but on Debian this
does not as *kernel-install* expects the vmlinuz to be present in
*/lib/modules/<kernel-version>* path. So for all kernels we need to trigger
`dpkg-reconfigure` to sign the uki image.

.. code-block:: sh

   dpkg-reconfigure linux-image-$(uname -r)
   # additionally for any other versions

Here is the sample output you will see if everything is configured properly.

.. code-block:: sh

   sudo dpkg-reconfigure linux-image-(uname -r)
   /etc/kernel/postinst.d/dracut:
   dracut: Generating /boot/initrd.img-6.10.9-amd64
   Updating kernel version 6.10.9-amd64 in systemd-boot...
   Signing Unsigned original image
   Using config file: /etc/kernel/uki.conf
   + sbverify --list /boot/vmlinuz-6.10.9-amd64
   + sbsign --key /home/vasudeva.sk/Documents/personal/secureboot/db.key --cert /home/vasudeva.sk/Documents/personal/secureboot/db.crt /tmp/ukicc7vcxhy --output        /tmp/kernel-install.staging.QLeGLn/uki.efi
   Wrote signed /tmp/kernel-install.staging.QLeGLn/uki.efi
   /etc/kernel/postinst.d/zz-systemd-boot:
   Installing kernel version 6.10.9-amd64 in systemd-boot...
   Signing Unsigned original image
   Using config file: /etc/kernel/uki.conf
   + sbverify --list /boot/vmlinuz-6.10.9-amd64
     + sbsign --key /home/vasudeva.sk/Documents/personal/secureboot/db.key --cert /home/vasudeva.sk/Documents/personal/secureboot/db.crt /tmp/ukit7r1hzep --output /tmp/kernel-install.staging.dWVt5s/uki.efi
   Wrote signed /tmp/kernel-install.staging.dWVt5s/uki.efi

Now the final and important part is to enroll our keys into the firmware. I used
*systemd-boot* to complete this step. We have already copied the all *.auth*
files to */efi/loader/keys/<hostname>/* location before, so we just need to boot
to *systemd-boot* boot menu and select enroll option which already display with
our <hostname> option. This is done using following command.

.. code-block:: sh

   systemctl reboot --boot-loader-menu=0

Once enrolling is done system will reboot into the newly signed kernel which can
be verified using *bootctl* which will be something like below.

.. image:: {static}/images/bootctl_uefi_enabled.png

Now that we enabled secureboot there is one small problem, that is lockdown
comes along with secureboot on all distro shipped kernel. Lockdown means no more
kprobes/bpf or dkms drivers etc. The option is to compile upstream kernel
directly which will not put the system in lockdown mode. As my colleague said to
me "I follow the torvalds ideology, of there is no reason to tie secureboot to
lockdown lsm".

The credit for helping to me to get this entire thing done goes to my colleague
who does not want to be named or linked here ;-).
