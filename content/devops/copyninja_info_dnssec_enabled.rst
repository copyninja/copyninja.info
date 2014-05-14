Enabling DNSSEC for copyninja.info
##################################

:date: 2014-05-13 20:30
:slug: dnssec-copyninja-dot-info
:tags: dnssec, sysadmin, technology
:author: copyninja
:summary: Post describes how I moved copyninja.info domain name
	  records to DNSSEC.
		   
Recently I've been seeing lot of posts about DNSSEC on Internet and I
thought  I should configure my domain to be secured by DNSSEC.

**copyninja.info** domain is now secured with DNSSEC you can verify
this by `DNSSEC analyzer by Verisign
<http://dnssec-debugger.verisignlabs.com/copyninja.info>`_ and `DNSViz
<http://dnsviz.net/d/copyninja.info/dnssec/>`_ online tool or by
installing `DNSSEC validator addon <http://dnssec-validator.cz/>`_ for
your browser.

There are good amount of tutorials and guides available to enable
DNSSEC for your domain, still I want to note down steps I followed to
here for the record (of course it will be helpful for me if I forget
it ;-))

First step will be installing `bind9` and `dnssec-tools` package, if
you use aptitude installing `dnssec-tools` will pull down the `bind9`
unless you have configured aptitude to not install the **Recommends**.

Next setting up the zone file for your domain, for this first make a
copy of /etc/bind/db.local as /etc/bind/db.example.com, replace
example.com with your domain name. Now you need to add your zone
records to the zone file.

Next edit the /etc/bind/named.conf.local file and add following lines

::

   zone "example.com" {
       type master;
       file "/etc/bind/db.copyninja.info";
       allow-transfer {secondary;};
   };


Here replace secondary with your secondary DNS servers, if you don't
have one you can ommit this but its always recommended to have
secondary DNS servers for a zone, in cases when primary fails. After
this we need to enable DNSSEC on bind, this is done by editing the
file /etc/bind/named.conf.options. Add following lines into
**options** section.

::

   dnssec-validation yes;
   dnssec-enable yes;
   dnssec-lookaside auto;

A more explanation on this can be found on `Linux Journal article
<http://www.linuxjournal.com/content/dnssec-part-ii-implementation>`_.

Now its time to create DNSSEC keys and sign your zone, more about
different DNSSEC keys and records can be found in the `Linux Journal
Article on implementation
<http://www.linuxjournal.com/content/dnssec-part-i-concepts>`_. 

I used `zonesigner` utility from dnssec-tools which does job of
signing and including KSK and ZSK keys into bind configuration which
otherwise should be done manually. Here is the command line I used for
generating keys, thanks to `Jonas <http://dr.jones.dk>`_ for this.

.. code:: bash

   mkdir -p /etc/bind/keys
   zonesigner -algorithm RSASHA256 -keydirectory /etc/bind/keys\
	  -dsdir /etc/bind/keys -archivedir /etc/bind/keys/archive \
	  /etc/bind/db.example.com

Here we store our keys into /etc/bind/keys directory, and use
**RSASHA256** algorithm for key generation which is more stronger than
the default used RSASHA1 (atleast thats what Jonas told me). This will
create ZSK and KSK for the signing zone and creates a signed zone file
db.example.com.signed in same directory as original zone file. Now all
you need to do is replace the zone file from db.example.com to
db.example.com.signed in *file* directive with your `named.conf.local`
file.


   Note that this keys expire after 30 days so you need to resign your
   zone before 30 days. For resigning just run zonesigner from
   /etc/bind/keys. You can setup cron job to do this periodically.

.. code:: bash

   zonesigner -zone example.com /path/to/db.example.com


Our signed zone is ready but we are not done yet! For DNSSEC to work
others should trust your signed record for this you need to register
your public keys with registrar for your domain and this can be done
via your domain provider (in my case this is Gandi).

You need to check your domain name providers documentation on how to
do this. For Gandi users there is a nice `documentation
<http://wiki.gandi.net/en/domains/dnssec>`_.

Reference
---------

1. `Linux  Journal - DNSSEC concepts <http://www.linuxjournal.com/content/dnssec-part-i-concepts>`_
2. `Linux Journal - DNSSEC implementation
   <http://www.linux-journal.com/content/dnssec-part-ii-implementation>`_
3. `Signing your zone <https://www.dnssec-tools.org/wiki/index.php/Sign_Your_Zone>`_
