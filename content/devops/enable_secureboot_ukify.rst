Note to Self: Enabling Secure Boot with UKI on Debian
#####################################################

:date: 2024-09-24 11:30
:slug: enable_secureboot_ukify
:tags: debian, secureboot, systemd, uki
:author: copyninja
:summary: This post explains how to enable self-signed Secure Boot with UKI on Debian.

.. note::
   *This post is a continuation of my previous post on enabling the UKI image
   on Debian.*

* `Enabling Unified Kernel Image on Debian
  <https://copyninja.in/blog/enable_ukify_debian.html>`_

In Secure Boot mode, I will be taking full control of the device by removing
any preinstalled keys and installing my own. This post from `rodsbooks
<https://www.rodsbooks.com/efi-bootloaders/controlling-sb.html>`_ gives a good
overview of the benefits and the entire process.

For the process, we need the following three keys:
 1. Platform Key (PK): This is the top-level key in Secure Boot, usually
    provided by the motherboard manufacturer. To control the entire Secure Boot
    process, it's important to replace the vendor-supplied PK with our own.
 2. Key Exchange Key (KEK): These keys are used to sign the Signatures Database
    and Forbidden Signatures Database updates.
 3. Database Key (DB): This key is used to sign or verify binaries
    (bootloaders, boot managers, shells, drivers, etc.).

There is also the Forbidden Signature Key (dbx), which is the opposite of what
the DB key does. We will not be generating this key.

To enroll the keys, we first need to put the device in *Secure Boot Setup Mode*.
Once done, the status can be checked using the `bootctl status` command. You
should see something similar to the image below.

.. image:: {static}/images/uefi_setupmode.png

I followed `these instructions
<https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot#Creating_keys>`_
from the Arch Wiki to generate the keys manually. We will need the `efitools`
and `openssl` packages for this step. I used `rsa:2048` as the key size instead
of `rsa:4096`, just to be on the safe side, as some older firmware might not
support 4096-bit keys.

Once you have followed the instructions in the Arch Wiki to generate your keys,
you need to copy all the *.auth* keys to the */efi/loader/keys/<hostname>/*
folder. In my case, it looks like this:

.. code-block:: sh

   ❯ sudo ls /efi/loader/keys/chamunda
   db.auth  KEK.auth  PK.auth

Next, we need to sign the *systemd-boot* bootloader with our new keys. This can
be done with the following command:

.. code-block:: sh

   sbsign --key <path-to db.key> --cert <path-to db.crt> \
      /usr/lib/systemd/boot/efi/systemd-bootx64.efi

Once signing is done, you will see a file called *systemd-bootx64.efi.signed* in
the same location. This needs to be installed using the *bootctl install*
command. The output will look something like the image below.

.. image:: {static}/images/bootctl_install.png

.. note::

   *In my original installation post, I used /boot/efi, but here I just remounted it
   to /efi. The warnings appear because it was not mounted with umask=0077.
   After the warning, I updated fstab with this option, and the warnings went away.*

We can now verify if it's signed with our keys using the *sbsign --verify*
command. The output is shown below.

.. image:: {static}/images/sbsign_verify_systemdboot.png

Next, add the key to the uki.conf file that we created earlier for generating
the UKI image. Add the following two lines to */etc/kernel/uki.conf*:

.. code-block:: ini

   SecureBootPrivateKey=/path/to/db.key
   SecureBootCertificate=/path/to/db.crt

Generally, running `kernel-install -v add-all` should work, but on Debian, this
doesn’t because *kernel-install* expects the vmlinuz to be present in
*/lib/modules/<kernel-version>*. So, for all kernels, we need to trigger
`dpkg-reconfigure` to sign the UKI image.

.. code-block:: sh

   dpkg-reconfigure linux-image-$(uname -r)
   # additionally for any other versions

Here is a sample output that you should see if everything is configured properly:

.. code-block:: sh

   sudo dpkg-reconfigure linux-image-$(uname -r)
   /etc/kernel/postinst.d/dracut:
   dracut: Generating /boot/initrd.img-6.10.9-amd64
   Updating kernel version 6.10.9-amd64 in systemd-boot...
   Signing unsigned original image
   Using config file: /etc/kernel/uki.conf
   + sbverify --list /boot/vmlinuz-6.10.9-amd64
   + sbsign --key /home/vasudeva.sk/Documents/personal/secureboot/db.key --cert /home/vasudeva.sk/Documents/personal/secureboot/db.crt /tmp/ukicc7vcxhy --output        /tmp/kernel-install.staging.QLeGLn/uki.efi
   Wrote signed /tmp/kernel-install.staging.QLeGLn/uki.efi
   /etc/kernel/postinst.d/zz-systemd-boot:
   Installing kernel version 6.10.9-amd64 in systemd-boot...
   Signing unsigned original image
   Using config file: /etc/kernel/uki.conf
   + sbverify --list /boot/vmlinuz-6.10.9-amd64
   + sbsign --key /home/vasudeva.sk/Documents/personal/secureboot/db.key --cert /home/vasudeva.sk/Documents/personal/secureboot/db.crt /tmp/ukit7r1hzep --output /tmp/kernel-install.staging.dWVt5s/uki.efi
   Wrote signed /tmp/kernel-install.staging.dWVt5s/uki.efi

The final and most important part is to enroll our keys into the firmware. I
used *systemd-boot* to complete this step. We already copied all the *.auth*
files to the */efi/loader/keys/<hostname>/* location, so we just need to boot
into the *systemd-boot* menu and select the enroll option that shows our
<hostname>. This can be done with the following command:

.. code-block:: sh

   systemctl reboot --boot-loader-menu=0

Once the keys are enrolled, the system will reboot into the newly signed kernel,
which can be verified using *bootctl*. You should see something like the image
below:

.. image:: {static}/images/bootctl_uefi_enabled.png

Now that we have enabled Secure Boot, there’s one small problem: lockdown mode
comes with Secure Boot on all distro-shipped kernels. Lockdown means no more
kprobes/BPF, DKMS drivers, etc. The solution is to compile the upstream kernel
directly, which will not enable lockdown mode.

As my colleague said to me, "I follow the Torvalds ideology: there is no reason
to tie Secure Boot to lockdown LSM." I agree. You can read more about `Torvalds'
opinion on UEFI tied with lockdown
<https://www.phoronix.com/news/UEFI-Kernel-Lockdown-Concerns>`_.

Credit goes to my colleague who helped me throughout this process, though they
prefer to remain anonymous.
