Stop messing with my settings Network Manager
#############################################

:date: 2014-07-20 00:39
:slug: networkmanager-wifi-issue
:tags: network-manager, ath9k, wifi
:author: copyninja
:summary: Network Manager toying with wifi card

I use a laptop with `Atheros` wifi card with `ath9k` driver. I use
`hostapd` to convert my laptop wifi into AP (Access point) so I can
share network with my `Nexus 7` and `Kindle`. This has been working
fine for quite some time till my recent update.

After recent system update (I use Debian Sid), I couldn't for some
reason convert my wifi into AP so my device can connect. I can't find
anything in log nor in hostapd debug messages which is useful to
trouble shoot the issue. Every time I start the laptop my wifi card
will be blocked by RF-KILL and I have manually unblock (both hard and
soft). The script which I use to convert my Wifi into AP is below

.. code-block:: sh
   #!/bin/bash

   #Initial wifi interface configuration
   ifconfig "$1" up 192.168.2.1 netmask 255.255.255.0
   sleep 2

   # start dhcp
   sudo systemctl restart dnsmasq.service

   iptables --flush
   iptables --table nat --flush
   iptables --delete-chain
   iptables -t nat -A POSTROUTING -o "$2" -j MASQUERADE
   iptables -A FORWARD -i "$1" -j ACCEPT
 
   sysctl -w net.ipv4.ip_forward=1

   #start hostapd
   hostapd /etc/hostapd/hostapd.conf  &> /dev/null &

I tried rebooting the laptop and for some time I managed to convert my
wifi into AP, I noticed at same time that Network Manager is not
started once laptop is booted, yeah this also started happening after
recent upgrade which I guess is the black magic of systemd. After some
time I noticed wifi has went down and now I can't bring it up because
its blocked by RF-KILL. After checking the syslog I noticed following
lines.

::

  Jul 18 23:09:30 rudra kernel: [ 1754.891060] IPv6: ADDRCONF(NETDEV_CHANGE): wlan0: link becomes ready
  Jul 18 23:09:30 rudra NetworkManager[5485]: <info> (mon.wlan0): using nl80211 for WiFi device control
  Jul 18 23:09:30 rudra NetworkManager[5485]: <info> (mon.wlan0): driver supports Access Point (AP) mode
  Jul 18 23:09:30 rudra NetworkManager[5485]: <info> (mon.wlan0): new 802.11 WiFi device (driver: 'ath9k' ifindex: 10)
  Jul 18 23:09:30 rudra NetworkManager[5485]: <info> (mon.wlan0): exported as /org/freedesktop/NetworkManager/Devices/8
  Jul 18 23:09:30 rudra NetworkManager[5485]: <info> (mon.wlan0): device state change: unmanaged -> unavailable (reason 'managed') [10 20 2]
  Jul 18 23:09:30 rudra NetworkManager[5485]: <info> (mon.wlan0): preparing device
  Jul 18 23:09:30 rudra NetworkManager[5485]: <info> devices added (path: /sys/devices/pci0000:00/0000:00:1c.1/0000:04:00.0/net/mon.wlan0, iface: mon.wlan0)
  Jul 18 23:09:30 rudra NetworkManager[5485]: <info> device added (path: /sys/devices/pci0000:00/0000:00:1c.1/0000:04:00.0/net/mon.wlan0, iface: mon.wlan0): no ifupdown configuration found.
  Jul 18 23:09:33 rudra ModemManager[891]: <warn>  Couldn't find support for device at '/sys/devices/pci0000:00/0000:00:1c.1/0000:04:00.0': not supported by any plugin

Well I couldn't figure out much but it looks like NetworkManager has
come up and after seeing interface `mon.wlan0`, a monitoring interface
created by `hostapd` to monitor the AP goes mad and tries to do
something with it. I've no clue what it is doing and don't have enough
patience to debug that. Probably some expert can give me hints on
this.

So as a last resort I purged the NetworkManager completely from the
system and settled back to good old `wicd` and rebooted the
system. After reboot wifi card is happy and is not blocked by RF-KILL
and now I can convert it AP and use it as long as I wish without any
problems. Wicd is not a great tool but its good enough to get the job
done and does only what is asked to it unlike the NetworkManager.

So in short

  NetworkManager please stop f***ing with my settings and stop acting
  oversmart.


