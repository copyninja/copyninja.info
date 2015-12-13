Mount ordering and automount options in systemd
###############################################

:date: 2015-12-13 15:13
:slug: systemd_automount_entry
:tags: systemd, fstab, automount
:author: copyninja
:summary: Brief notes on systemd.mount and systemd.autmount features.

Just to give a brief recap of why I'm writing this post, I've to
describe a brief encounter I had with systemd which rendered my system
unbootable. I first felt its systemd's problem but later figured out
it was my mistake. So below is brief story divided into 2 sections
*Problem* and *Solution*. Here *Problem* describes issue I faced with
systemd and *Solution* discusses the *.mount* and *.automount* suffix
files used by systemd.

Problem
=======

I have several local bin folders and I don't want to modify *PATH*
environment variable adding every other folder path. I first started
using *aufs* as alternative to symlinks or modifying *PATH*
variable. Recently I learnt about much more light weight union fs which is
in kernel, *overlayfs*. And Google led me to Arch wiki article which
showed me a fstab entry like below

.. code-block:: fstab

   overlay	  /usr/local/bin	overlay	noauto,x-systemd.automount,lowerdir=/home/vasudev/Documents/utilities/bin,upperdir=/home/vasudev/Documents/utilities/jonas-bin,workdir=/home/vasudev/Documents/utilities/bin-overlay	0	0

And after adding this entry, on next reboot systemd is not able to
mount my LVM home and swap partition. It does however mount root
partition. It gives me emergency target but login never returns. So
without any alternative I had to reinstall the system. But funnily
enough I started encountering the same issue (yeah after I had added
above entry into fstab). Yeah that time I never thought that its
culprit. My friend Ritesh finally got my system booting after the
weird x-systemd.automount option. I never investigated further that
time on why this problem occurred.

Solution
========

After re-encounter with similar problem and some other project I read
the manual on *systemd.mount*, *systemd-fstab-generator* and
*systemd.automount* and I had some understanding of what really went
wrong in my case above.

So now let us see what really is happening. All the above happened
because, *systemd translates the /etc/fstab into .mount units at run
time using systemd-fstab-generator*. Every entry in fstab translates
into a file named after the mount point. The */* in the path of the
mount point is replaced by a *-*. So */* mount point is named as
*-.mount* and */home* is named as *home.mount* and */boot* becomes
*boot.mount*. All these files can be seen in directory
*/run/systemd/generator*. And all these mount points are needed by
*local-fs.target* , if any of these mount points fail,
*local-fs.target* fails. And if *local-fs.target* fails it will invoke
*emergency.target*.

*systemd-fstab-generator* manual suggests the ordering information in
*/etc/fstab* is discarded. That means if you have union mounts, bind
mounts or fuse mounts in the fstab which is normally at end of fstab
and uses path from /home or some other device mount points it will
fail to get mounted. This happens because *systemd-fstab-generator*
didn't  consider the ordering in fstab. This is what happened in my
case my *overlay* mount point which is *usr-local-bin.mount* was some
how happened to be tried before *home.mount* because there is no
explicit dependency like *Requires=* or *After=* was declared. When
systemd tried to mount it the path required under /home were not
really present hence failed which in return invoked *emergency.target*
as *usr-local-bin.mount* is *Requires=* dependency for
*local-fs.target*.

Now what I didn't understand is why *emregency.target* never gave me
the root shell after entering login information. I feel that this part
is unrelated to the problem I described above and is some other bug.

To over come this what we can do is provided *systemd-fstab-generator*
some information on dependency of each mount point. *systemd.mount*
manual page suggests several such options. One which I used in my case
is *x-systemd.requires* which should be placed in options column of
fstab and specify the mount point which is needed before it has to be
mounted. So my overlay fs entry translates to something like below

.. code-block:: fstab

   overlay	  /usr/local/bin	overlay	noauto,x-systemd.requires=/home,x-systemd.automount,lowerdir=/home/vasudev/Documents/utilities/bin,upperdir=/home/vasudev/Documents/utilities/jonas-bin,workdir=/home/vasudev/Documents/utilities/bin-overlay	0	0

There is another special option called *x-systemd.automount* this will
make systemd-fstab-generator to create a *.automount* file for this
mount point. What does *systemd.automount* do? It achieves on-demand
file mounting and parallelized file system mounting. Something similar
to *systemd.socket* the file system will be mounted when you access
the mount point for first time.

So now if you try to see dependency of usr-local-bin.mount you will
see following.

.. code-block:: shell

   systemctl show -p After usr-local-bin.mount
   After=-.mount systemd-journald.socket local-fs-pre.target system.slice usr-local-bin.automount

This means now *usr-local-bin.mount* depends on
*usr-local-bin.automount*. And let us see what usr-local-bin.automount
needs.

.. code-block:: shell

   systemctl show -p Requires usr-local-bin.automount
   Requires=-.mount home.mount

   systemctl show -p After usr-local-bin.automount
   After=-.mount home.mount

So clearly *usr-local-bin.automount* is activated after *-.mount* and
*home.mount* is activated. Similar can be done for any bind mounts or
fuse mounts which require other mount points before it can be
mounted. Also note that *x-systemd.autmount* is not mandatory option
for declaring dependencies, I used it just to make sure
*/usr/local/bin* is mounted only when its really needed.


Conclusion
===========

A lot of traditional way has been changed by systemd. I never
understood why my system failed to boot in first place this happened
because I was not really aware of how systemd works and was trying to
debug the problem with traditional approach. So there is really a
learning curve involved for every sysadmin out there who is going to
use systemd. Most of them will read documentation before hand but
others like me will learn after having a situation like above. :-).

So systemd interfering into /etc/fstab is good?. I don't know but
since systemd parallelizes  the boot procedure something like this is
really needed. Is there a way to make systemd not touch
/etc/fstab?. Yes there is you need to pass *fstab=0* option in kernel
command line and systemd-fstab-generator doesn't create any .mount or
.swap files from your /etc/fstab.

**!NB Also it looks like x-systemd.requires option was introduced
recently and is not available in systemd <= 215 which is default in
Jessie. So how do you declare dependencies in Jessie system?. I don't
have any answer!. I did read that x-systemd.automount which is
available in those versions of systemd can be used, but I'm yet to
experiment this. If it succeeds I will write a post on it.**
