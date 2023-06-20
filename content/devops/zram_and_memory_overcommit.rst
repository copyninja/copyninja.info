Notes: Experimenting with ZRAM and Memory Over commit
#####################################################

:date: 2023-06-16 14:55
:slug: zram_memory_overcommit
:tags: zram, vm, overcommit, debian
:author: copyninja
:summary: Notes on experiments with ZRAM and vm.overcommit_memory

Introduction
============

The ZRAM module in the Linux kernel creates a memory-backed block device that
stores its content in a compressed format. It offers users the choice of
compression algorithms such as lz4, zstd, or lzo. These algorithms differ in
compression ratio and speed, with zstd providing the best compression but being
slower, while lz4 offers higher speed but lower compression.

Using ZRAM as Swap
==================

One interesting use case for ZRAM is utilizing it as swap space in the system.
There are two utilities available for configuring ZRAM as swap: zram-tools and
systemd-zram-generator. However, Debian Bullseye lacks systemd-zram-generator,
making zram-tools the only option for Bullseye users. While it's possible to use
systemd-zram-generator by self-compiling or via cargo, I preferred using tools
available in the distribution repository due to my restricted environment.

Installation
============

The installation process is straightforward. Simply execute the following command:

.. code-block:: shell

   apt-get install zram-tools

Configuration
=============

The configuration involves modifying a simple shell script file
*/etc/default/zramswap* sourced by the `/usr/bin/zramswap` script. Here's an
example of the configuration I used:

.. code-block:: shell

   # Compression algorithm selection
   # Speed: lz4 > zstd > lzo
   # Compression: zstd > lzo > lz4
   # This is not inclusive of all the algorithms available in the latest kernels
   # See /sys/block/zram0/comp_algorithm (when the zram module is loaded) to check
   # the currently set and available algorithms for your kernel [1]
   # [1]  https://github.com/torvalds/linux/blob/master/Documentation/blockdev/zram.txt#L86
   ALGO=zstd

   # Specifies the amount of RAM that should be used for zram
   # based on a percentage of the total available memory
   # This takes precedence and overrides SIZE below
   PERCENT=30

   # Specifies a static amount of RAM that should be used for
   # the ZRAM devices, measured in MiB
   # SIZE=256000

   # Specifies the priority for the swap devices, see swapon(2)
   # for more details. A higher number indicates higher priority
   # This should probably be higher than hdd/ssd swaps.
   # PRIORITY=100

I chose zstd as the compression algorithm for its superior compression
capabilities. Additionally, I reserved 30% of memory as the size of the zram
device. After modifying the configuration, restart the `zramswap.service` to
activate the swap:

.. code-block:: shell

   systemctl restart zramswap.service

Using systemd-zram-generator
============================

For Debian Bookworm users, an alternative option is systemd-zram-generator.
Although zram-tools is still available in Debian Bookworm,
systemd-zram-generator offers a more integrated solution within the systemd
ecosystem. Below is an example of the translated configuration for
systemd-zram-generator, located at `/etc/systemd/zram-generator.conf`:

.. code-block:: conf

   # This config file enables a /dev/zram0 swap device with the following
   # properties:
   # * size: 50% of available RAM or 4GiB, whichever is less
   # * compression-algorithm: kernel default
   #
   # This device's properties can be modified by adding options under the
   # [zram0] section below. For example, to set a fixed size of 2GiB, set
   # `zram-size = 2GiB`.

   [zram0]
   zram-size = ceil(ram * 30/100)
   compression-algorithm = zstd
   swap-priority = 100
   fs-type = swap

After making the necessary changes, reload systemd and start the `systemd-zram-setup@zram0.service`:

.. code-block:: shell

   systemctl daemon-reload
   systemctl start systemd-zram-setup@zram0.service

The `systemd-zram-generator` creates the zram device by loading the kernel
module and then creates a `systemd.swap` unit to mount the zram device as swap.
In this case, the swap file is called `zram0.swap`.

Checking Compression and Details
================================

To verify the effectiveness of the swap configuration, you can use the `zramctl`
command, which is part of the `util-linux` package. Alternatively, the
`zramswap` utility provided by `zram-tools` can be used to obtain the same
output.

During my testing with synthetic memory load created using *stress-ng* *vm*
class I found that I can reach upto *40%* compression ratio.

Memory Overcommit
=================

Another use case I was looking for is allowing the launching of applications
that require more memory than what is available in the system. By default, the
Linux kernel attempts to estimate the amount of free memory left on the system
when user space requests more memory (`vm.overcommit_memory=0`). However, you
can change this behavior by modifying the sysctl value for
`vm.overcommit_memory` to `1`.

To demonstrate this, I ran a test using stress-ng to request more memory than
the system had available. As expected, the Linux kernel refused to allocate
memory, and the stress-ng process could not proceed.

.. code-block:: shell

   free -tg                                                                                                                                                                                         ──(Mon,Jun19)─┘
                   total        used        free      shared  buff/cache   available
    Mem:              31          12          11           3          11          18
    Swap:             10           2           8
    Total:            41          14          19

   sudo stress-ng --vm=1 --vm-bytes=50G -t 120                                                                                                                                                      ──(Mon,Jun19)─┘
    stress-ng: info:  [1496310] setting to a 120 second (2 mins, 0.00 secs) run per stressor
    stress-ng: info:  [1496310] dispatching hogs: 1 vm
    stress-ng: info:  [1496312] vm: gave up trying to mmap, no available memory, skipping stressor
    stress-ng: warn:  [1496310] vm: [1496311] aborted early, out of system resources
    stress-ng: info:  [1496310] vm:
    stress-ng: warn:  [1496310]         14 System Management Interrupts
    stress-ng: info:  [1496310] passed: 0
    stress-ng: info:  [1496310] failed: 0
    stress-ng: info:  [1496310] skipped: 1: vm (1)
    stress-ng: info:  [1496310] successful run completed in 10.04s

By setting `vm.overcommit_memory=1`, Linux will allocate memory in a more relaxed
manner, assuming an infinite amount of memory is available.

Conclusion
==========

ZRAM provides disks that allow for very fast I/O, and compression allows for a
significant amount of memory savings. ZRAM is not restricted to just swap usage;
it can be used as a normal block device with different file systems.

Using ZRAM as swap is beneficial because, unlike disk-based swap, it is faster,
and compression ensures that we use a smaller amount of RAM itself as swap
space.

Additionally, adjusting the memory overcommit settings can be beneficial for
scenarios that require launching memory-intensive applications.

*Note: When running stress tests or allocating excessive memory, be cautious
about the actual memory capacity of your system to prevent out-of-memory (OOM)
situations.*

Feel free to explore the capabilities of ZRAM and optimize your system's memory
management. Happy computing!

Reference
=========

1. `zram: Compressed RAM-based block device
   <https://www.kernel.org/doc/html/latest/admin-guide/blockdev/zram.html>`_
2. `Overcommit Accounting
   <https://www.kernel.org/doc/Documentation/vm/overcommit-accounting>`_
3. `Linux Overcommit Modes <https://www.baeldung.com/linux/overcommit-modes>`_
4. `zram: Arch Wiki <https://www.baeldung.com/linux/overcommit-modes>`_
5. `zram: Debian Wiki <https://wiki.debian.org/ZRam>`_
