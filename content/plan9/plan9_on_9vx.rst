Running Plan9 using 9vx - using vx32 sandboxing library
#######################################################

:date: 2015-02-21 12:32
:slug: plan9_on_9vx_linux
:tags: plan9, debian, 9vx
:author: copyninja
:summary: Running Plan9 using 9vx, a vx32 sandboxing library.


Now a days I'm more and more attracted towards Plan9, an Operating
System meant to be the successor of UNIX and created by same people
who created original UNIX. I'm always baffled by the simplicity of
Plan9. Sadly Plan9 never took off for whatever reasons.

I've been for a while trying to run Plan9, I ran Plan9 on Raspberry Pi
model B using 9pi, but I couldn't experiment with it more due to some
restrictions in my home setup.

I installed original Plan9 4th Edition from Bell labs (now part of
Alcatel-Lucent), I will write about it in on different post. But
running virtual machine on my system is again PITA as system is
already old (3 and half year). I came across the `9vx
<http://swtch.com/9vx/>`_ which is port of Plan9 for FreeBSD, Linux
and Mac OSX by Russ Cox.

I downloaded original 9vx version 0.9.12 from Russ's page linked
above. The archive contains a Plan9 rootfs along with precompiled 9vx
binaries for Linux, FreeBSD and Mac OS X. I ran the Linux binary but
it crashed.

.. code-block:: sh

   ./9vx.Linux -u glenda

I was seeing some illegal instruction error in dmesg. I didn't bother
to do more investigation.

A bit of googling showed me Arch Linux's `wiki page on 9vx
<https://wiki.archlinux.org/index.php/9vx>`_. I got errors trying to
compile the original vx32 from `rsc's repository
<https://bitbucket.org/rsc/vx32>`_ but later saw that AUR 9vx package
is built from different repository forked from rsc's found `here
<https://bitbucket.org/rminnich/vx32>`_.

I cloned the repository to local and compiled it, I don't really
remember if I had installed any additional packages. But if you get
error you will know what additional thing is required. After
compilation the 9vx binary is found inside `src/9vx/9vx`. I used this
newly compiled 9vx to run the the rootfs I downloaded from Russ's
website.

.. code-block:: sh

   9vx -u glenda -r /path/to/extracted/9vx-0.9.12/


This launches Plan9 and allows you to work inside Plan9. The good part
is its not resource hungry and still looks like you have a VM running
with Plan9 on it.

But there seems to be a better way to do this directly from plan9 iso
from bell labs. It can be found on `9fans list
<http://9fans.net/archive/2010/10/14>`_. Now I'm going to try that out
too :-). And in next post I will share my experience of using Plan9 on
Qemu.
