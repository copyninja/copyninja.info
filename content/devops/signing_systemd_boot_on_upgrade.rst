Signing the systemd-boot on upgrade using Dpkg Triggers
#######################################################

:date: 2024-09-29 13:08
:slug: sign_systemd_boot_trigger
:tags: systemd, dpkg, triggers, uefi, debian
:author: copyninja
:summary: Post talks about signing the systemd-boot efi binary on upgrade using
          dpkg trigger mechanism.

In my previous post on `enabling secureboot
<https://copyninja.in/blog/enable_secureboot_ukify.html>`_, I had mentioned one
improvement pending was signing the *systemd-boot* efi binary with my keys on
every upgrade. So in this post we will explore the implementation of this using
dpkg triggers.

Here is the best introduction on `dpkg triggers
<https://web.archive.org/web/20111022012105/http://www.seanius.net/blog/2009/09/dpkg-triggers-howto/>`_.
The source code mentioned in the post can be downloaded from `here
<https://alioth-archive.debian.org/git/users/seanius/dpkg-triggers-example.git.tar.xz>`_.

From the */usr/share/doc/dpkg/spec/triggers.txt*, the triggers are described as
below

 *A dpkg trigger is a facility that allows events caused by one package
 but of interest to another package to be recorded and aggregated, and
 processed later by the interested package.  This feature simplifies
 various registration and system-update tasks and reduces duplication
 of processing.*

For using this we create a custom package with single script which actually
signs the *systemd-boot* efi using our key. The code for script is as simple as
below.

.. code-block:: sh

    #!/bin/bash

    set -e

    echo "Signing the new systemd-bootx64.efi"
    sbsign --key /etc/secureboot/db.key --cert /etc/secureboot/db.crt \
            /usr/lib/systemd/boot/efi/systemd-bootx64.efi

    echo "Invoking bootctl install to copy stuff"
    bootctl install

Invocation of *bootctl install* is optional if we have enabled
*systemd-boot-update.service* which will update the signed boot loader on next
boot.

We need to have a *triggers* file under *debian/* folder of the package which
declares its interest in the modification of path
*/usr/lib/systemd/boot/efi/systemd-bootx64.efi*. The trigger file looks like
below

.. code-block:: text

    # trigger 1 interest on systemd-bootx64.efi
    interest-noawait /usr/lib/systemd/boot/efi/systemd-bootx64.efi

You can read about various directives and their meanings, that can be used in
*triggers* file under man page *deb-triggers*

Once we build the package and install it this request is added to
*/var/lib/dpkg/triggers/Files*. See the screenshot below post installation of
our package.

.. image:: {static}/images/trigger_install.png
           :alt: installed trigger
           :align: center

Just to test the working I did a re-install of *systemd-boot-efi* package which
provides toe efi binary for *systemd-boot* using following command.

.. code-block:: sh

    sudo apt install --reinstall systemd-boot-efi

On installation you can see the debug message being printed in the below
screenshot.

.. image:: {static}/images/systemd_boot_sign_triggered.png
           :alt: systemd-boot-signer triggered
           :align: center

Just for testing the *systemd-boot-update.service* I commented out *bootctl
install* from above script and did a reinstallation and restarted the
*systemd-boot-update.service*. On checking log I saw following.

.. code-block:: text

    Sep 29 13:42:51 chamunda systemd[1]: Stopping systemd-boot-update.service - Automatic Boot Loader Update...
    Sep 29 13:42:51 chamunda systemd[1]: Starting systemd-boot-update.service - Automatic Boot Loader Update...
    Sep 29 13:42:51 chamunda bootctl[1801516]: Skipping "/efi/EFI/systemd/systemd-bootx64.efi", same boot loader version in place already.
    Sep 29 13:42:51 chamunda bootctl[1801516]: Skipping "/efi/EFI/BOOT/BOOTX64.EFI", same boot loader version in place already.
    Sep 29 13:42:51 chamunda bootctl[1801516]: Skipping "/efi/EFI/BOOT/BOOTX64.EFI", same boot loader version in place already.
    Sep 29 13:42:51 chamunda systemd[1]: Finished systemd-boot-update.service - Automatic Boot Loader Update.
    Sep 29 13:43:37 chamunda systemd[1]: systemd-boot-update.service: Deactivated successfully.
    Sep 29 13:43:37 chamunda systemd[1]: Stopped systemd-boot-update.service - Automatic Boot Loader Update.
    Sep 29 13:43:37 chamunda systemd[1]: Stopping systemd-boot-update.service - Automatic Boot Loader Update...

So indeed the service tried to copy the boot loader but did not do so because
really there was no update in the binary its just a reinstallation triggered.

The code for entire package can be found `here <https://github.com/copyninja/systemd-boot-signer>`_
