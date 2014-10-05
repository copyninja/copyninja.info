Note to Self: LVM Shrink Resize HowTo
#####################################

:date: 2014-10-05 12:00
:slug: lvm-shrink-resize
:tags: lvm, debian-installer, partition, debian	      
:author: copyninja
:summary: Post is a note to self describing LVM shrink and resize of
          partition
       
Recently I had to reinstall a system at office with Debian Wheezy and
I thought I should use this opportunity to experiment with LVM. Yeah
I've not used LVM till date, even though I'm using Linux for more than
5 years now. I know many DD friends who use LVM with LUKS encryption
and I always wanted to experiment, but since my laptop is only thing
I've and its currently perfectly in shape I didn't dare to experiment
it there. This reinstall was golden opportunity for me to experiment
and learn something new.

I used Wheezy CD ISO downloaded using *jigdo* for installation. Now I
will just go bit off topic and want to share the USB stick
preparation. I have to say this because I had not done installation
for quite a while now. Last I did was during Squeeze time so like
usual I blindly executed following command.

.. code-block:: shell

  cat debian-wheezy.iso > /dev/sdb
  
Surprisingly USB stick didn't boot! I was getting **Corrupt or missing
ISO.bin**. So next I tried using `dd` for preparing.

.. code-block:: shell

  dd if=debian-wheezy.iso of=/dev/sdb
  
Surprisingly this also didn't work and I get same error message as
above. This is when I went back to debian manual and looked for
installation step and there I found new way!

.. code-block:: shell

  cp debian-wheezy.iso /dev/sdb
  
Look at destination, its a device and voilà this worked! This is
something new I learnt and I'm surprised how easy it is now to prepare
USB stick. But I still didn't get why first 2 methods failed!. If you
guys know please do share.

Now coming back to LVM. I used default LVM when disk partitioning was
asked, and I used guided partitioning method provided by
`debian-installer` and ended up with following layout

.. code-block:: shell

  $ lvs
    LV     VG        Attr     LSize  Pool Origin Data%  Move Log Copy%  Convert
  home   system-disk -wi-ao-- 62.34g
  root   system-disk -wi-ao--  9.31g
  swap_1 system-disk -wi-ao--  2.64g

So guided partitioning of `debian-installer` allocates 10G for root
and rest to home and swap. This is not a problem but when I started
installing required software, I could see root running out of space
quickly so I wanted to resize root and give it 10G more, for this I
need to reduce the home by 10G for which I need to first unmount the
home partition. Unmounting home from running system isn't possible so
I booted into recovery assuming I can unmount home there but I
couldn't. `lsof` didn't show any one using /home after searching a bit
I found `fuser` command and it looks like kernel is using /home which
is mounted by it.

.. code-block:: shell

  $ fuser -vm /home
                       USER        PID ACCESS COMMAND
  /home:               root     kernel mount /home
  
So it isn't possible to unmount /home in recovery mode also. Online
materials told me to use live-cd for doing this but I didn't have
patience to do that so I just went ahead commented /home mounting in
/etc/fstab and rebooted!. This time it worked and /home is not mounted
on recovery mode. Now comes the hard part resizing home, thanks to
`TLDP doc on reducing
<http://tldp.org/HOWTO/LVM-HOWTO/reducelv.html>`_ I coud do this with
following step

.. code-block:: shell

  # e2fsck -f /dev/volume-name/home
  # resize2fs /dev/volume-name/home 52G
  # lvreduce -L-10G /dev/volume-name/home
  
And now the next part live extending the root partition again thanks
to `TLDP doc on extending
<http://tldp.org/HOWTO/LVM-HOWTO/extendlv.html>`_ following command
did it.

.. code-block:: shell

  # lvextend -L+10G /dev/volume-name/root
  # resize2fs /dev/volumne-name/root
  
And now important part! **Uncomment /home line in /etc/fstab so it
will be mounted normally in next boot** and reboot! On login I can see
my partitions updated.

.. code-block:: shell

  # lvs
    LV     VG        Attr     LSize  Pool Origin Data%  Move Log Copy%  Convert
  home   system-disk -wi-ao-- 52.34g
  root   system-disk -wi-ao-- 19.31g
  swap_1 system-disk -wi-ao--  2.64g
  
I've started liking LVM more now! :)
