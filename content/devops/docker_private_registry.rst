Docker Private Registry and Self Signed Certificates
####################################################

:date: 2018-04-14 19:47 +0530
:author: copyninja
:slug: docker-registry-selfsigned-cert
:tags: docker, container, openssl
:summary: Post describes additional steps that needs to be taken
          while generating a self signed certificates for docker private
          registry.

I was recently experimenting with hosting a private registry on an internal LAN
network for publishing docker private images. I found out that *docker-pull*
works only with TLS secured registry. There is possible to run insecure registry
by editing *daemon.json* file but its better to use self-signed certificates
instead.

Once I followed the step and started registry I tried to *docker-pull* and it
started complaining about certificate not having any valid names. But this same
certificate worked fine with browsers too, of course you need to add exception
but no other errors were encountered.

`Documentation <https://docs.docker.com/registry/insecure/>`_ for Docker does
not speaks any specific settings needs to be done prior to generating a
self-signed certificate so I was bit confused at beginning.A bit of searching
showed up following `issue <https://github.com/docker/for-linux/issues/248>`_
filed against docker and then later re-assigned against `*Golang*
<https://github.com/golang/go/issues/24293>`_ for its method of handling x509
certificate. It appears that with valid *Subject Alternative Name* Go crypto
library ignores the *Common Name*.

From thread on `Security Stack Exchange
<https://security.stackexchange.com/questions/74345/provide-subjectaltname-to-openssl-directly-on-command-line>`_
I found the command to create a self-signed certificate to contain self-signed
certificate. Command in excepted answer does not work until you add
*--extensions* option to it as mentioned in one of the comments. Full command is
as shown below.

.. code-block:: shell

   openssl req -new -sha256 -key domain.key \
                -subj "/C=US/ST=CA/O=Acme, Inc./CN=example.com" \
                -reqexts SAN -extensions SAN \
                -config \
   <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:example.com,DNS:www.example.com")) -out domain.crt


You would need to replace values in *-subj* and under *[SAN]* extension. Benefit
of this command is you need not modify the */etc/ssl/openssl.conf* file.

If you do not have a domain name for the registry and using IP address instead
consider replacing *[SAN]* section in above command to have *IP: <ip-address>*
instead of *DNS*.

Happy hacking.!
