Biboumi - A XMPP - IRC Gateway
##############################

:date: 2018-03-11 10:49 +0530
:slug: xmpp-irc-gateway
:tags: xmpp, irc, gateway, mobile
:author: copyninja
:summary: A brief post explaining biboumi and its usage.

IRC is a communication mode (technically a communication protocol) used by many
Free Software projects for communication and collaboration. It is serving these
projects well even 30 years after its inception. Though I'm pretty much okay
with IRC I had a problem of not able to use IRC from the mobile phones. Main
problem is the inconsistent network connection, where IRC needs always to be
connected. This is where I came across *Biboumi*.

*Biboumi* by itself does not have anything to do with mobile phones, its just a
gateway which will allow you to connect with IRC channel as if it is a XMPP MUC
room from any XMPP client. Benefit of this is it allows to enjoy some of XMPP
feature in your IRC channel (not all but those which can be mapped).

I run *Biboumi* with my *ejabbered* instance and there by now I can connect to
some of the *Debian* IRC channel directly from my phone using *Conversations*
XMPP client for Android.

*Biboumi* is packaged for Debian, though I'm co-maintainer of the package most
hardwork is done by *Jonas Smedegaard* in keeping the package in shape. It is
also available for *stretch-backports* (though slightly outdated as its not
packaged by us for backports). Once you install the package, copy example
configuration file from `/usr/share/doc/biboumi/examples/example.conf` to
`/etc/biboumi/biboumi.cfg` and modify the values as needed. Below is my sample
file with password redacted.

.. code-block:: ini

   hostname=biboumi.localhost
   password=xxx
   db_name=/var/lib/biboumi/biboumi.sqlite
   #log_file=/var/log/biboumi/biboumi.log
   log_level=0
   admin=vasudev@copyninja.info
   port=8888
   realname_customization=true
   realname_from_jid=false

Explanation for all the key, values in the configuration file is available in
the man page (man biboumi).

Biboumi is configured as external component of the XMPP server. In
my case I'm using ejabberd to host my XMPP service. Below is the configuration
needed for allowing biboumi to connect with ejabberd.

.. code-block:: yaml

   listen:
  -
    port: 8888
    ip: "127.0.0.1"
    module: ejabberd_service
    acess: all
    hosts:
      "biboumi.localhost":
         password: xxx

`password` field in biboumi configuration should match password value in your
XMPP server configuration.

After doing above configuration reload ejabberd (or your XMPP server) and start
biboumi. Biboumi package provides systemd service file so you might need to
enable it first. That's it now you have an XMPP to IRC gateway ready.

You might notice that I'm using local host name for *hostname* key as well as
*ip* field in ejabberd configuration. This is because TLS support was added to
*biboumi* Debian package only after 7.2 release as botan 2.x was not available
till that point in Debian. Hence using proper domain name and making biboumi
listen to public will be not safe at least prior to Debian package version
7.2-2. Also making the biboumi service public means you will also need to handle
spam bots trying to connect from your service to IRC, which might get your VPS
banned from IRC.

Connection Semantics
====================

Once biboumi is configured and running you can now use XMPP client of your
choice (Gajim, Conversation etc.) to connect to IRC. To connect to OFTC from
your XMPP client you need to following address in *Group Chat* section

`%irc.oftc.net@biboumi.localhost`

Replace part after @ to what you have configured in *hostname* field in biboumi
configuration. To join a specific channel on a IRC server you need to join the
group conversation with following format

`#channel%irc.example.com@biboumi.localhost`

If your nick name is registered and you would want to identify yourself to IRC
server you can do that by joining in group conversation with NickServ using
following address

`nickserv%irc.example.org@biboumi.localhost`

Once connected you can send NickServ command directly in this virtual channel.
Like `identify password nick`. It is also possible to configure your XMPP
clients like Gajim to send `Ad-Hoc commands
<https://xmpp.org/extensions/xep-0050.html>`_ on connection to particular IRC
server for identifying your self with IRC servers. But this part I did not get
working in Gajim.

If you are running your own XMPP server then *biboumi* gives you best way to
connect to IRC from your mobile phones. And with applications like
*Conversation* running XMPP application won't be hard on your phone battery.

**Resources**
 - `Biboumi documentation
   <https://lab.louiz.org/louiz/biboumi/blob/master/doc/biboumi.1.rst#configuration>`_
 - `Conversations <https://conversations.im/>`_
 - `ejabberd documentation <https://docs.ejabberd.im/admin/configuration/>`_
