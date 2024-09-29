Signing the systemd-boot on Upgrade Using Dpkg Triggers
#######################################################

:date: 2024-09-29 13:08
:slug: sign_systemd_boot_trigger
:tags: systemd, dpkg, triggers, uefi, debian
:author: copyninja
:summary: This post discusses signing the systemd-boot EFI binary on upgrade using
          the dpkg trigger mechanism.

In my previous post on `enabling SecureBoot
<https://copyninja.in/blog/enable_secureboot_ukify.html>`_, I mentioned that one
pending improvement was signing the *systemd-boot* EFI binary with my keys on
every upgrade. In this post, we'll explore the implementation of this process using
dpkg triggers.

For an excellent introduction to dpkg triggers, refer to this `archived blog post
<https://web.archive.org/web/20111022012105/http://www.seanius.net/blog/2009/09/dpkg-triggers-howto/>`_.
The source code mentioned in that post can be downloaded from `alioth archive
<https://alioth-archive.debian.org/git/users/seanius/dpkg-triggers-example.git.tar.xz>`_.

From */usr/share/doc/dpkg/spec/triggers.txt*, triggers are described as follows:

    *A dpkg trigger is a facility that allows events caused by one package
    but of interest to another package to be recorded and aggregated, and
    processed later by the interested package. This feature simplifies
    various registration and system-update tasks and reduces duplication
    of processing.*

To implement this, we create a custom package with a single script that signs the
*systemd-boot* EFI binary using our key. The script is as simple as:

.. code-block:: sh

    #!/bin/bash

    set -e

    echo "Signing the new systemd-bootx64.efi"
    sbsign --key /etc/secureboot/db.key --cert /etc/secureboot/db.crt \
           /usr/lib/systemd/boot/efi/systemd-bootx64.efi

    echo "Invoking bootctl install to copy stuff"
    bootctl install

Invoking *bootctl install* is optional if we have enabled
*systemd-boot-update.service*, which will update the signed bootloader on the next
boot.

We need to have a *triggers* file under the *debian/* folder of the package, which
declares its interest in modifications to the path
*/usr/lib/systemd/boot/efi/systemd-bootx64.efi*. The trigger file looks like this:

.. code-block:: text

    # trigger 1 interest on systemd-bootx64.efi
    interest-noawait /usr/lib/systemd/boot/efi/systemd-bootx64.efi

You can read about various directives and their meanings that can be used in
the *triggers* file in the *deb-triggers* man page.

Once we build and install the package, this request is added to
*/var/lib/dpkg/triggers/File*. See the screenshot below after installation of
our package:

.. image:: {static}/images/trigger_install.png
   :alt: installed trigger
   :align: center

To test the functionality, I performed a re-installation of the *systemd-boot-efi*
package, which provides the EFI binary for *systemd-boot*, using the following command:

.. code-block:: sh

    sudo apt install --reinstall systemd-boot-efi

During installation, you can see the debug message being printed in the screenshot below:

.. image:: {static}/images/systemd_boot_sign_triggered.png
   :alt: systemd-boot-signer triggered
   :align: center

To test the *systemd-boot-update.service*, I commented out the *bootctl install* line
from the above script, performed a reinstallation, and restarted the
*systemd-boot-update.service*. Checking the log, I saw the following:

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

Indeed, the service attempted to copy the bootloader but did not do so because
there was no actual update to the binary; it was just a reinstallation trigger.

The complete code for this package can be found `here <https://github.com/copyninja/systemd-boot-signer>`_.

With this post the entire series on using  UKI to Secureboot with Debian comes
to an end. Happy hacking!.
