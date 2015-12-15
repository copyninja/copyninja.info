Persisting resource control options for systemd-nspawn containers
#################################################################

:date: 2015-12-15 20:30
:slug: persist_resource_control
:author: copyninja
:tags: systemd, systemd-nspawn, resource-control, containers
:summary: Steps to persist the resource control options for
	  systemd-nspawn containers.

In my previous `post on systemd-nspawn
<https://copyninja.info/blog/taming_systemd_nsapwn.html>`_ I
mentioned, I was unclear on how to persist resource control options
for a container.  Today I accidentally discovered how can the property
be persisted across boot without modifying service file or writing
custom service file for container. It is done using *systemctl
set-property*

To set *CPUAccounting* and *CPUShares* for a container we need to run
following command.

.. code-block:: shell

   systemctl set-property systemd-nspawn@container.service  CPUACCounting=1 CPUShares=200

This actually persists these settings at location,
*/etc/systemd/systemd-nspawn@container.service.d/* folder. So in our
case there will be 2 files created under above location by name
*50-CPUAccounting.conf* and *50-CPUShares.conf* with following
contents.

.. code-block:: ini

   # 50-CPUAccounting.conf
   [Service]
   CPUAccounting=yes

   # 50-CPUShares.conf
   [Service]
   CPUShares=200

Today when I discovered this folder and saw the file contents, I
became curious and started to wonder who created this folder. The look
at systemctl man page made showed me this.

       set-property NAME ASSIGNMENT...
           Set the specified unit properties at runtime where this is
           supported. This allows changing configuration parameter
           properties such as resource control settings at
           runtime. Not all properties may be changed at runtime, but
           many resource control settings (primarily those in
           systemd.resource-control(5)) may. The changes are applied
           instantly, and stored on disk for future boots,
           unless --runtime is passed, in which case the settings only
           apply until the next reboot. The syntax of the property
           assignment follows closely the syntax of assignments in
           unit files.

           Example: systemctl set-property foobar.service CPUShares=777

           Note that this command allows changing multiple properties
           at the same time, which is preferable over setting them
           individually. Like unit file configuration settings,
           assigning the empty list to list parameters will reset the
           list.

I did remember doing this for my container and hence it became clear
these files are actually written by *systemctl set-property*.

In case you don't want to persist the properties across boot you can
simply pass *--runtime* switch.

Basically this is not just for container, resource control can be thus
applied to any running service on the system. This is actually cool.
