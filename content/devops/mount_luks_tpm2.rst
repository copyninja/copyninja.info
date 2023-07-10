Using LUKS-Encrypted USB Stick with TPM2 Integration
####################################################

:date: 2023-07-09 13:17
:slug: luks2_tpm_mount
:tags: systemd-cryptenroll, systemd, tpm2, luks2, mount
:author: copyninja
:summary: Experimenting with systemd-cryptenroll to mount luks2 encrypted usb
          device

I use LUKS encrypted USB stick for storing my GPG and SSH keys which acts as
backup as well as portable key setup when I'm working on different laptops. One
of thing about LUKS encrypted USB stick is you need to enter the password every
time you want to mount the device, either via Window Manager like KDE or via
`cryptsetup luksOpen`. Now a days laptop comes equipped with TPM2 module which
can be used for automatically decrypting the device and later it can be mounted.
In this post I'm going to explore *systemd-cryptenroll* to do this and then use
udev rules and bunch of script to automatically do the mounting of encrypted
USB.

First make sure the TPM2 is avaiable on your device. You can run following
command and will see output like below.

.. code-block:: shell

    ➜  blog git:(master) sudo journalctl -k --grep=tpm2
    [sudo] password for vasudev:
    Jul 08 18:57:32 bhairava kernel: ACPI: SSDT 0x00000000BBEFC000 0003C6 (v02 LENOVO Tpm2Tabl 00001000 INTL 20160422)
    Jul 08 18:57:32 bhairava kernel: ACPI: TPM2 0x00000000BBEFB000 000034 (v03 LENOVO TP-R0D   00000830 PTEC 00000002)
    Jul 08 18:57:32 bhairava kernel: ACPI: Reserving TPM2 table memory at [mem 0xbbefb000-0xbbefb033]
    Jul 08 18:57:32 bhairava systemd[1]: systemd 253.5-1 running in system mode (+PAM +AUDIT +SELINUX +APPARMOR +IMA +SMACK +SECCOMP +GCRYPT -GNUTLS +OPENSSL +ACL +BLKID +CURL +ELFUTILS +FIDO2 +IDN2 -IDN +IPTC +KMOD +LIBCRYPTSET>
    Jul 08 18:57:43 bhairava systemd[1]: systemd 253.5-1 running in system mode (+PAM +AUDIT +SELINUX +APPARMOR +IMA +SMACK +SECCOMP +GCRYPT -GNUTLS +OPENSSL +ACL +BLKID +CURL +ELFUTILS +FIDO2 +IDN2 -IDN +IPTC +KMOD +LIBCRYPTSET>
    Jul 08 18:57:43 bhairava systemd[1]: systemd-pcrmachine.service - TPM2 PCR Machine ID Measurement was skipped because of an unmet condition check (ConditionPathExists=/sys/firmware/efi/efivars/StubPcrKernelImage-4a67b082-0a4>
    Jul 08 18:57:43 bhairava systemd[1]: systemd-pcrfs-root.service - TPM2 PCR
    Root File System Measurement was skipped because of an unmet condition check
    (ConditionPathExists=/sys/firmware/efi/efivars/StubPcrKernelImage-4a67b0>

You can also use *systemd-cryptenroll* command to find if there is a TPM2 device
available on your laptop.

.. code-block:: shell

      blog git:(master) systemd-cryptenroll --tpm2-device=list
      PATH        DEVICE      DRIVER
      /dev/tpmrm0 MSFT0101:00 tpm_tis
      ➜  blog git:(master)

Now make sure you have connected your encrypted USB device. Note that
*systemd-cryptenroll* only works with *LUKS2* and not with *LUKS1*. I faced this
issue as my device was *LUKS1* encrypted and *systemd-cryptenroll* was refusing
to enroll the device complaining *LUKS2 superblock not found*.

You can verify if your device is using LUKS1 header or LUKS2 using *cryptsetup
luksDump <device>*. If its LUKS1 you will see header starting something like
below.

.. code-block:: shell

    LUKS header information for /dev/sdb1

    Version:        1
    Cipher name:    aes
    Cipher mode:    xts-plain64
    Hash spec:      sha256
    Payload offset: 4096

Converting *LUKS1* to *LUKS2* is pretty easy job but for safety make sure you
backup the header using *cryptsetup luksHeaderBackup* command. Once backed up
use following command to convert the header to *LUKS2*

.. code-block:: shell

    sudo cryptsetup convert --type luks2 /dev/sdb1

After conversion the header will looks something like below

.. code-block:: shell

    Version:        2
    Epoch:          4
    Metadata area:  16384 [bytes]
    Keyslots area:  2064384 [bytes]
    UUID:           000b2670-be4a-41b4-98eb-9adbd12a7616
    Label:          (no label)
    Subsystem:      (no subsystem)
    Flags:          (no flags)

Next step is to enroll the new luks key for the encrypted device which is to be
done using *systemd-cryptenroll*. Run the following command

.. code-block:: shell

  sudo systemd-cryptenroll --tpm2-device=/dev/tpmrm0 --tpm2-pcrs="0+7" /dev/sdb1

This will ask for existing key to unseal the device and adds a new random key,
adds it to the volume so it can be used to unlock it in addition to the existing
keys, and binds this new key to PCRs 0 and 7 (the system firmware and Secure
Boot state):

If there is only one TPM device on the box then one can use *--tpm2-device=auto*
to select the device automatically. To confirm that new key was enrolled, dump
the LUKS configuration and look for a systemd-tpm2 token entry, as well as an
additional entry in the Keyslots section

We can check the working of this using `/usr/lib/systemd/systemd-cryptsetup` as
follows. We can verify with lsblk if the device is unsealed or not using lsblk.

.. code-block:: shell

    sudo /usr/lib/systemd/systemd-cryptsetup attach GPG_USB "/dev/sdb1" - tpm2-device=auto

    ➜  ~ lsblk
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

Now that we solved first problem of unsealing the USB device using TPM2 instead
of entering the key manually, next part is to mount the device when its inserted
and removing mapping when device is removed. I did this using following udev
rules.

.. code-block:: text

   ACTION=="add", KERNEL=="sd*", ENV{DEVTYPE}=="partition", ENV{ID_BUS}=="usb" \
     #RUN+="/usr/local/bin/mount_enc_usb.sh '%E{DEVNAME}'"
     ENV{SYSTEMD_WANTS}="mount-gpg-usb@$env{DEVNAME}.service"
  ACTION=="remove", KERNEL=="sd*", ENV{DEVTYPE}=="partition", ENV{ID_BUS}=="usb" \
     RUN+="/usr/local/bin/umount_enc_usb.sh '%E{ID_FS_UUID}'"

When device is added I'm using systemd service to mount the device at particular
location. I did it first using `RUN` script but for some reason script was
exiting with return code `32`. I suspect this is because `systemd-cryptsetup`
takes some time return and udev is timing out by that time. Executing script
manually worked. So decided to use systemd service instead.

On removal though device is already gone the mapping is still left behind and
this will cause issue when device is re-inserted. So to remove the mapping I
added a script to close the mapping on device removal.

Below are the systemd service and script file

.. code-block:: shell

    #!/bin/bash
    # mount_enc_usb.sh
    set -x

    if [[ "$#" -ne 1 ]]; then
        echo "$(basename $0) <device>"
        exit 1
    fi

    device_uuid="$(blkid --output udev $1 | grep ID_FS_UUID= | cut -d= -f2)"
    if [[ "$device_uuid" == 000b2670-be4a-41b4-98eb-9adbd12a7616 ]]; then
        # We found our device lets trigger systemd-cryptsetup
        /usr/lib/systemd/systemd-cryptsetup attach GPG_USB "$1" - tpm2-device=auto
        [[ -d /media/vasudev/GPG_USB ]] || (mkdir -p /media/vasudev/GPG_USB/ && chown vasudev:vasudev /media/vasudev/GPG_USB)
        mount /dev/mapper/GPG_USB /media/vasudev/GPG_USB
    else
        echo "Not the inerested device. Ignoring"
        exit 0
    fi

.. code-block:: shell

    #!/bin/bash
    # umount_enc_usb.sh
    if [[ "$#" -ne 1 ]]; then
      echo "$(basename $0) <fsuuid>"
      exit 1
    fi

    if [[ "$1" == "000b2670-be4a-41b4-98eb-9adbd12a7616" ]]; then
      # Our device is removed lets close the luks mapping
      [[ -e /dev/mapper/GPG_USB ]] && cryptsetup luksClose /dev/mapper/GPG_USB
    else
      echo "Not our device"
      exit 0
    fi

.. code-block:: ini

    [Unit]
    Description=mount the encrypted usb device service

    [Service]
    Type=simple
    ExecStart=/usr/local/bin/mount_enc_usb.sh

With this setup plugging in the USB device unseals it and mounts it
automatically and on removal just closes the luks mapping.
