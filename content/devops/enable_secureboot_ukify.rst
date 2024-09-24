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
