Using LUKS-Encrypted USB Stick with TPM2 Integration
####################################################

:date: 2023-07-09 13:17
:slug: luks2_tpm_mount
:tags: systemd-cryptenroll, systemd, tpm2, luks2, mount
:author: copyninja
:summary: Experimenting with systemd-cryptenroll to mount luks2 encrypted usb
          device

I use a LUKS-encrypted USB stick to store my GPG and SSH keys, which acts as a
backup and portable key setup when working on different laptops. One
inconvenience with LUKS-encrypted USB sticks is that you need to enter the
password every time you want to mount the device, either through a Window
Manager like KDE or using the `cryptsetup luksOpen` command. Fortunately, many
laptops nowadays come equipped with TPM2 modules, which can be utilized to
automatically decrypt the device and subsequently mount it. In this post, we'll
explore the usage of *systemd-cryptenroll* for this purpose, along with udev
rules and a set of scripts to automate the mounting of the encrypted USB.

First, ensure that your device has a TPM2 module. You can run the following
command to check:

.. code-block:: shell

   sudo journalctl -k --grep=tpm2

The output should resemble the following:

.. code-block:: shell

   Jul 08 18:57:32 bhairava kernel: ACPI: SSDT 0x00000000BBEFC000 0003C6 (v02
   LENOVO Tpm2Tabl 00001000 INTL 20160422) Jul 08 18:57:32 bhairava kernel:
   ACPI: TPM2 0x00000000BBEFB000 000034 (v03 LENOVO TP-R0D 00000830
   PTEC 00000002) Jul 08 18:57:32 bhairava kernel: ACPI: Reserving TPM2 table
   memory at [mem 0xbbefb000-0xbbefb033]

You can also use the `systemd-cryptenroll` command to check for the availability
of a TPM2 device on your laptop:

.. code-block:: shell

   systemd-cryptenroll --tpm2-device=list


The output will be something like following:

.. code-block:: shell

      blog git:(master) systemd-cryptenroll --tpm2-device=list
      PATH        DEVICE      DRIVER
      /dev/tpmrm0 MSFT0101:00 tpm_tis
      ➜  blog git:(master)

Next, ensure that you have connected your encrypted USB device. Note that
`systemd-cryptenroll` only works with LUKS2 and not LUKS1. If your device is
LUKS1-encrypted, you may encounter an error while enrolling the device,
complaining about the LUKS2 superblock not found.

To determine if your device uses a LUKS1 header or LUKS2, use the `cryptsetup
luksDump <device>` command. If it is LUKS1, the header will begin with:

.. code-block:: shell

    LUKS header information for /dev/sdb1

    Version:        1
    Cipher name:    aes
    Cipher mode:    xts-plain64
    Hash spec:      sha256
    Payload offset: 4096

Converting from LUKS1 to LUKS2 is a simple process, but for safety, ensure that
you backup the header using the `cryptsetup luksHeaderBackup` command. Once
backed up, use the following command to convert the header to LUKS2:

.. code-block:: shell

    sudo cryptsetup convert --type luks2 /dev/sdb1

After conversion, the header will look like this:

.. code-block:: shell

    Version:        2
    Epoch:          4
    Metadata area:  16384 [bytes]
    Keyslots area:  2064384 [bytes]
    UUID:           000b2670-be4a-41b4-98eb-9adbd12a7616
    Label:          (no label)
    Subsystem:      (no subsystem)
    Flags:          (no flags)

The next step is to enroll the new LUKS key for the encrypted device using
`systemd-cryptenroll`. Run the following command:

.. code-block:: shell

  sudo systemd-cryptenroll --tpm2-device=/dev/tpmrm0 --tpm2-pcrs="0+7" /dev/sdb1

This command will prompt you to provide the existing key to unseal the device.
It will then add a new random key to the volume, allowing it to be unlocked in
addition to the existing keys. Additionally, it will bind this new key to PCRs 0
and 7, representing the system firmware and Secure Boot state.

If there is only one TPM device on the system, you can use `--tpm2-device=auto`
to automatically select the device. To confirm that the new key has been
enrolled, you can dump the LUKS configuration and look for a `systemd-tpm2`
token entry, as well as an additional entry in the Keyslots section.

To test the setup, you can use the `/usr/lib/systemd/systemd-cryptsetup` command. Additionally, you can check if the device is unsealed by using `lsblk`:

.. code-block:: shell

   sudo /usr/lib/systemd/systemd-cryptsetup attach GPG_USB "/dev/sdb1" - tpm2-device=auto

   lsblk

The `lsblk` command should display the unsealed and mounted device, like this:

.. code-block:: shell

   NAME        MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINTS
   sda           8:0    0 223.6G  0 disk
   ├─sda1        8:1    0   976M  0 part  /boot/efi
   └─sda2        8:2    0 222.6G  0 part
     └─root    254:0    0 222.6G  0 crypt /
   sdb           8:16   1   7.5G  0 disk
   └─sdb1        8:17   1   7.5G  0 part
     └─GPG_USB 254:1    0   7.5G  0 crypt /media/vasudev/GPG_USB

Auto Mounting the device
========================

Now that we have solved the initial problem of unsealing the USB device using
TPM2 instead of manually entering the key, the next step is to automatically
mount the device upon insertion and remove the mapping when the device is
removed. This can be achieved using the following udev rules:

.. code-block:: text

   ACTION=="add", KERNEL=="sd*", ENV{DEVTYPE}=="partition", ENV{ID_BUS}=="usb", ENV{SYSTEMD_WANTS}="mount-gpg-usb@$env{DEVNAME}.service"
   ACTION=="remove", KERNEL=="sd*", ENV{DEVTYPE}=="partition", ENV{ID_BUS}=="usb", RUN+="/usr/local/bin/umount_enc_usb.sh '%E{ID_FS_UUID}'"

When a device is added, a systemd service is triggered to mount the device at a
specific location. Initially, I used a script with the `RUN` directive, but it
resulted in an exit code of `32`. This might be due to `systemd-cryptsetup`
taking some time to return, causing udev to time out. To address this, I opted
to use a systemd service instead.

For device removal, even though the physical device is no longer present, the
mapping may still remain, causing issues upon reinsertion. To resolve this, I
created a script to close the luks mapping upon device removal.

Below are the systemd service and script files:

**mount_enc_usb.sh:**

.. code-block:: bash

   #!/bin/bash
   set -x

   if [[ "$#" -ne 1 ]]; then
       echo "$(basename $0) <device>"
       exit 1
   fi

   device_uuid="$(blkid --output udev $1 | grep ID_FS_UUID= | cut -d= -f2)"
   if [[ "$device_uuid" == 000b2670-be4a-41b4-98eb-9adbd12a7616 ]]; then
       # Found our device, let's trigger systemd-cryptsetup
       /usr/lib/systemd/systemd-cryptsetup attach GPG_USB "$1" - tpm2-device=auto
       [[ -d /media/vasudev/GPG_USB ]] || (mkdir -p /media/vasudev/GPG_USB/ && chown vasudev:vasudev /media/vasudev/GPG_USB)
       mount /dev/mapper/GPG_USB /media/vasudev/GPG_USB
   else
       echo "Not the interested device. Ignoring."
       exit 0
   fi

**umount_enc_usb.sh:**

.. code-block:: bash

   #!/bin/bash
   if [[ "$#" -ne 1 ]]; then
     echo "$(basename $0) <fsuuid>"
     exit 1
   fi

   if [[ "$1" == "000b2670-be4a-41b4-98eb-9adbd12a7616" ]]; then
     # Our device is removed, let's close the luks mapping
     [[ -e /dev/mapper/GPG_USB ]] && cryptsetup luksClose /dev/mapper/GPG_USB
   else
     echo "Not our device."
     exit 0
   fi

**mount-gpg-usb@.service:**

.. code-block:: ini

   [Unit]
   Description=Mount the encrypted USB device service

   [Service]
   Type=simple
   ExecStart=/usr/local/bin/mount_enc_usb.sh

With this setup, plugging in the USB device will automatically unseal and mount
it, and upon removal, the luks mapping will be closed.

.. note:: This can be even done for LUKS2 encrypted root disk but will need some
          tweaking in initramfs.

References
==========

1. `Trusted Platform Module Arch Wiki
   <https://wiki.archlinux.org/title/Trusted_Platform_Module>`_
2. `systemd-cryptenroll issue with LUKS1
   <https://www.reddit.com/r/openSUSE/comments/oydwuz/unable_to_use_systemdcryptenroll/>`_
3. `Execute shell script when USB Device is plugged
   <https://www.baeldung.com/linux/shell-run-script-usb-plugged>`_
