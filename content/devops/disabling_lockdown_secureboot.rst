Disabling Lockdown Mode with Secure Boot on Distro Kernel
#########################################################
:date: 2024-09-26 22:13
:slug: disable_lockdown_on_distro_kernel
:tags: debian, systemd, secureboot, lockdown
:author: copyninja
:summary: This post discusses a method to disable kernel lockdown mode on a
          distribution kernel when Secure Boot is enabled.

In my `previous post <https://copyninja.in/blog/enable_secureboot_ukify.html>`_,
I mentioned that Lockdown mode is activated when Secure Boot is enabled. One way
to override this was to use a self-compiled upstream kernel. However, sometimes
we might want to use the distribution kernel itself. This post explains how to
disable lockdown mode while keeping Secure Boot enabled with a distribution
kernel.

Understanding Secure Boot Detection
===================================

To begin, we need to understand how the kernel detects if Secure Boot is
enabled. This is done by the *efi_get_secureboot* function, as shown in the
image below:

.. image:: {static}/images/secureboot_code.png
   :alt: Secure Boot status check
   :align: center

Disabling Kernel Lockdown
=========================

The kernel code uses the value of MokSBStateRT to identify the Secure Boot state,
assuming that Secure Boot can only be enabled via shim. This assumption holds true
when using the Microsoft certificate for signature validation (as Microsoft currently
only signs shim). However, if we're using our own keys, we don't need shim and can
sign the bootloader ourselves. In this case, the Secure Boot state of the system
doesn't need to be tied to the MokSBStateRT variable.

To disable kernel lockdown, we need to set the UEFI runtime variable
*MokSBStateRT*. This essentially tricks the kernel into thinking Secure Boot is
disabled when it's actually enabled. This is achieved using a UEFI
*initializing* driver.

The code for this was written by an anonymous colleague who also assisted me
with various configuration guidance for setting up UKI and Secure Boot on my
system. The code is available `here
<https://codeberg.org/scarletstorm/lockdown-disable/src/branch/main>`_.

Implementation
==============

Detailed instructions for compiling and deploying the code are provided in the
repository, so I won't repeat them here.

Results
=======

I've tested this method with the default distribution kernel on my Debian
unstable system, and it successfully disables lockdown while maintaining Secure
Boot integrity. See the screenshot below for confirmation:

.. image:: {static}/images/distro_kernel_lockdown.png
   :alt: Distribution kernel lockdown disabled
   :align: center
