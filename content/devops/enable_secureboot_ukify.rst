Note to Self: Enabling Secure Boot with UKI on Debian
#####################################################

:date: 2024-09-24 11:30
:slug: enable_secureboot_ukify
:tags: debian, secureboot, systemd, uki
:author: copyninja
:summary: This post explains how to enable self-signed Secure Boot with Unified
          Kernel Image (UKI) on Debian.

.. note::
   *This post is a continuation of my previous article on enabling the Unified
   Kernel Image (UKI) on Debian.*

* `Enabling Unified Kernel Image on Debian
  <https://copyninja.in/blog/enable_ukify_debian.html>`_

In this guide, we'll implement Secure Boot by taking full control of the device,
removing preinstalled keys, and installing our own. For a comprehensive overview
of the benefits and process, refer to this excellent post from `rodsbooks
<https://www.rodsbooks.com/efi-bootloaders/controlling-sb.html>`_.

Key Components
--------------

To implement Secure Boot, we need three essential keys:

1. Platform Key (PK): The top-level key in Secure Boot, typically provided by
   the motherboard manufacturer. We'll replace the vendor-supplied PK with our
   own for complete control.
2. Key Exchange Key (KEK): Used to sign updates for the Signatures Database and
   Forbidden Signatures Database.
3. Database Key (DB): Used to sign or verify binaries (bootloaders, boot
   managers, shells, drivers, etc.).

There's also a Forbidden Signature Key (dbx), which is the opposite of the DB
key. We won't be generating this key in this guide.

Preparing for Key Enrollment
----------------------------

Before enrolling our keys, we need to put the device in *Secure Boot Setup
Mode*. Verify the status using the ``bootctl status`` command. You should see
output similar to the following image:

.. image:: {static}/images/uefi_setupmode.png
    :alt: UEFI Setup mode
    :align: center

Generating Keys
---------------

Follow `these instructions from the Arch Wiki
<https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot#Creating_keys>`_
to generate the keys manually. You'll need the ``efitools`` and ``openssl``
packages. I recommend using ``rsa:2048`` as the key size for better
compatibility with older firmware.

After generating the keys, copy all ``.auth`` files to the
``/efi/loader/keys/<hostname>/`` folder. For example:

.. code-block:: sh

   ❯ sudo ls /efi/loader/keys/chamunda
   db.auth  KEK.auth  PK.auth

Signing the Bootloader
----------------------

Sign the ``systemd-boot`` bootloader with your new keys:

.. code-block:: sh

   sbsign --key <path-to db.key> --cert <path-to db.crt> \
      /usr/lib/systemd/boot/efi/systemd-bootx64.efi

Install the signed bootloader using ``bootctl install``. The output should
resemble this:

.. image:: {static}/images/bootctl_install.png
           :alt: bootctl install
           :align: center

.. note::

   *If you encounter warnings about mount options, update your fstab with the
   `umask=0077` option for the EFI partition.*

Verify the signature using ``sbsign --verify``:

.. image:: {static}/images/sbsign_verify_systemdboot.png
           :alt: sbsign verify
           :align: center

Configuring UKI for Secure Boot
-------------------------------

Update the ``/etc/kernel/uki.conf`` file with your key paths:

.. code-block:: ini

   SecureBootPrivateKey=/path/to/db.key
   SecureBootCertificate=/path/to/db.crt

Signing the UKI Image
---------------------

On Debian, use ``dpkg-reconfigure`` to sign the UKI image for each kernel:

.. code-block:: sh

   sudo dpkg-reconfigure linux-image-$(uname -r)
   # Repeat for other kernel versions if necessary

You should see output similar to this:

.. code-block:: sh

   sudo dpkg-reconfigure linux-image-$(uname -r)
   /etc/kernel/postinst.d/dracut:
   dracut: Generating /boot/initrd.img-6.10.9-amd64
   Updating kernel version 6.10.9-amd64 in systemd-boot...
   Signing unsigned original image
   Using config file: /etc/kernel/uki.conf
   + sbverify --list /boot/vmlinuz-6.10.9-amd64
   + sbsign --key /home/vasudeva.sk/Documents/personal/secureboot/db.key --cert /home/vasudeva.sk/Documents/personal/secureboot/db.crt /tmp/ukicc7vcxhy --output /tmp/kernel-install.staging.QLeGLn/uki.efi
   Wrote signed /tmp/kernel-install.staging.QLeGLn/uki.efi
   /etc/kernel/postinst.d/zz-systemd-boot:
   Installing kernel version 6.10.9-amd64 in systemd-boot...
   Signing unsigned original image
   Using config file: /etc/kernel/uki.conf
   + sbverify --list /boot/vmlinuz-6.10.9-amd64
   + sbsign --key /home/vasudeva.sk/Documents/personal/secureboot/db.key --cert /home/vasudeva.sk/Documents/personal/secureboot/db.crt /tmp/ukit7r1hzep --output /tmp/kernel-install.staging.dWVt5s/uki.efi
   Wrote signed /tmp/kernel-install.staging.dWVt5s/uki.efi

Enrolling Keys in Firmware
--------------------------

Use ``systemd-boot`` to enroll your keys:

.. code-block:: sh

   systemctl reboot --boot-loader-menu=0

Select the enroll option with your hostname in the ``systemd-boot`` menu.

After key enrollment, the system will reboot into the newly signed kernel.
Verify with ``bootctl``:

.. image:: {static}/images/bootctl_uefi_enabled.png
           :alt: uefi enabled
           :align: center

Dealing with Lockdown Mode
--------------------------

Secure Boot enables lockdown mode on distro-shipped kernels, which restricts
certain features like kprobes/BPF and DKMS drivers. To avoid this, consider
compiling the upstream kernel directly, which doesn't enable lockdown mode by
default.

As Linus Torvalds has stated, "there is no reason to tie Secure Boot to lockdown
LSM." You can read more about `Torvalds' opinion on UEFI tied with lockdown
<https://www.phoronix.com/news/UEFI-Kernel-Lockdown-Concerns>`_.

Next Steps
----------

One thing that remains is automating the signing of systemd-boot on upgrade,
which is currently a manual process. I'm exploring dpkg triggers for achieving
this, and if I succeed, I will write a new post with details.

Acknowledgments
---------------

Special thanks to my anonymous colleague who provided invaluable assistance
throughout this process.
