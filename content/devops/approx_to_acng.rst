Switching from approx to apt-cacher-ng
######################################

:date: 2016-07-17 16:30 +0530
:slug: approx_to_acng
:tags: apt, approx, apt-cacher-ng, debian
:author: copyninja
:summary: Brief notes on my switch from approx to apt-cacher-ng

After a long ~5 years (from 2011) journey with approx I finally wanted
to switch to something new like apt-cacher-ng. And after a bit of
changes I finally managed to get apt-cacher-ng into my work flow.

Bit of History
==============

I should first give you a brief on how I started using approx. It all
started in MiniDebconf 2011 which I organized at my Alma-mater. I met
Jonas Smedegaard here and from him I learned about approx. Jonas has a
bunch of machines at his home and he was active user of approx and he
showed it to me while explaining the *Boxer* project. I was quite
impressed with approx. Back then I was using a 230kbps slow INTERNET
connection and I was also maintaining a couple of packages in
Debian. Updating the pbuilder chroots was time consuming task for me
as I had to download multiple times over slow net. And approx largely
solved this problem and I started using it.

5 years fast forward I now have quite fast INTERNET with good
FUP. (About 50GB a month), but I still tend to use approx which makes
building packages quite faster. I also use couple of containers on my
laptop which all use my laptop as approx cache.

Why switch?
===========

So why change to apt-cacher-ng?. Approx is a simple tool, it runs
mainly with inetd and sits between apt and the repository on
INTERNET. Where as apt-cacher-ng provides a lot of features. Below are
some listed from the apt-cacher-ng manual.

* use of TLS/SSL repositories (may be possible with approx but I'm notsure how to do it)
* Access control of who can access caching server
* Integration with debdelta (I've not tried, approx also supports
  debdelta)
* Avoiding use of apt-cacher-ng for some hosts
* Avoiding caching of some file types
* Partial mirroring for offline usage.
* Selection of ipv4 or ipv6 for connections.

The biggest change I see is the speed difference between approx and
apt-cacher-ng. I think this is mainly because apt-cacher-ng is threaded where as approx
runs using inetd.

I do not want all features of apt-cacher-ng at the moment, but who knows in
future I might need some features and hence I decided to switch to
apt-cacher-ng over approx.

Transition
==========

Transition from approx to apt-cacher-ng was smoother than I
expected. There are 2 approaches you can use one is explicit routing
another is transparent routing. I prefer transparent routing and I
only had to change my /etc/apt/sources.list to use the actual
repository URL.

.. code-block:: sources.list

   deb http://deb.debian.org/debian unstable main contrib non-free
   deb-src http://deb.debian.org/debian unstable main

   deb http://deb.debian.org/debian experimental main contrib non-free
   deb-src http://deb.debian.org/debian experimental main


After above change I had to add a *01proxy* configuration file to
*/etc/apt/apt.conf.d/* with following content.

.. code-block:: conf

   Acquire::http::Proxy "http://localhost:3142/"

I use explicit routing only when using apt-cacher-ng with pbuilder and
debootstrap. Following snippet shows explicit routing through */etc/apt/sources.list*.

.. code-block:: sources.list

   deb http://localhost:3142/deb.debian.org/debian unstable main

Usage with pbuilder and friends
-------------------------------

To use apt-cacher-ng with pbuilder you need to modify /etc/pbuilderrc
to contain following line

.. code-block:: sh

   MIRRORSITE=http://localhost:3142/deb.debian.org/debian


Usage with debootstrap
----------------------

To use apt-cacher-ng with debootstrap, pass MIRROR argument of
debootstrap as `http://localhost:3142/deb.debian.org/debian`.


Conclusion
==========

I've now completed full transition of my work flow to apt-cacher-ng
and purged approx and its cache.

.. role:: strike
   :class: strike

.. container:: strike

   Though it works fine I feel that there will be 2 caches created when
   you use transparent and explicit proxy using localhost:3142 URL. I'm
   sure it is possible to configure this to avoid duplication, but I've
   not yet figured it. If you know how to fix this do let me know.

Update
------   

Jonas told me that its not 2 caches but 2 routing one for transparent
routing and another for explicit routing. So I guess there is nothing
here to fix :-).
