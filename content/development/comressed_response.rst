Gzipped response for CSS/JS with Apache and mod_uwsgi
#####################################################

:date: 2014-03-01 9:00
:slug: comressed-response
:tags: python, apache2, mod_uwsgi, mod_deflate	      
:author: copyninja
:summary: Apache started sending completely gziped response when using
	  with mod_uwsgi plugin. Post tries to find the problem cause.

So it may sound normal to receive compressed response for CSS/JS file
from Apache2 but what I faced is completely different behavior, here I
saw not just body of response but also header are getting compressed
and send to browser and browser was unable to interpret the response
there by leading page rendered without CSS and JS.

That was long story short, so let me explain in detail the case and
what I found out.

I have `hosted <http://silpa.org.in>`_ `SILPA
<https://github.com/Project-SILPA/Silpa-Flask>`_ on my VPS using
uWSGI. I had used till date using *libapache2-mod-proxy-uwsgi* plugin
for which uWSGI should be using network socket and in Apache2 config I
need *ProxyPass* directive pointing to *uwsgi://host:port* and
everything used to work out of box. There is a drawback for using
network socket in uWSGI that is limited amount of ports (65535) and
possible clash with other services if we use wrong port number,
additionally network sockets will be slower compared to the file
socket so yesterday I thought of changing it to file socket and
removed *socket* directive in the ini file for uWSGI application
container for SILPA and here is where all problems started. My updated
configuration can be seen in our `documentation page
<http://silpa.readthedocs.org/en/latest/installation.html#hosting-the-silpa-on-webserver>`_
that is if you are interested to look my configuration file :-).

Problem Reporting
-----------------

We got selected to Gsoc again this year and we have lot of students
jumping in our channel *#silpa* on *irc.freenode.net* and yesterday
night some students reported they are facing *500 internal server
error* and subsequently others mentioned there is no theme being
rendered. I checked and found everything was fine for me only to
notice that my browser was using cached content, and when I clear
cache there I go everything vanished, no theme no css no javascript
just plain html!!!.

Investigation
-------------

So I thought I should investigate this and fired up *firebug* on my
iceweasel to observe the network traffic. And below is what I observed
in firebug network console!.


.. image:: {filename}/images/no-response-css.png
   :alt: No response headers
   :align: center

So you can see no response header in the above image but there is a
response and below how is response content visible on firebug.

.. image:: {filename}/images/response-content.png
   :alt: gzipped response
   :align: center

Still weird part was when using wget/curl directly to get the CSS I
was getting correct reply and the file, which is puzzling.

So I went ahead opened the CSS url directly using browser and saved
the resulting file. When I used ``file`` command on it, output
suggested the saved file in gzip compressed!. I went ahead
uncompressed it and opened the file and inside it I found response
header and the response body! So what just happened? Did apache some
how manage to compress entire respone not just response body?

The more puzzling question was why did it work when I was using
*mod_proxy_uwsgi* and failed when I switched to *mod_uwsgi*. I had no
clue at this point why this behavior is coming up.

Possible Solution
-----------------

I was still not sure how to resolve this, and started searching in the
network but nothing was coming up in search result which can explain
me this. And finally I stumbled on a link which is `totally unrelated
<http://bit.ly/1eJdQe8>`_ but I saw the word *mod_deflate* in the
content and wandered on my system to see if its enabled. Yes
mod_deflate was enabled I just opened the conf file and saw
following.

.. code-block:: apacheconf

   <IfModule mod_deflate.c>
          # these are known to be safe with MSIE 6
          AddOutputFilterByType DEFLATE text/html text/plain text/xml

          # everything else may cause problems with MSIE 6
          AddOutputFilterByType DEFLATE text/css
          AddOutputFilterByType DEFLATE application/x-javascript application/javascript application/ecmascript
          AddOutputFilterByType DEFLATE application/rss+xml
   </IfModule>

Interesting so it suggests to compress css, javascript files etc. So I
thought possibly its compressing the result of *mod_uwsgi*, yeah possibly so
why not try disabling *mod_deflate* and check if it works well and
good if not I'm not gonna loose anything. So I disabled *mod_deflate*
and voila! Everything is working fine!

What might be the reason for this behavior?
-------------------------------------------

Well I'm not exactly sure but here is my assumption. The whole
behavior depends on internal implementation of **mod_uwsgi** and
**mod_proxy_uwsgi** module. To confirm this I switched back to use
**mod_proxy_uwsgi** module and enabled **mod_deflate** and observed
request response in **Firebug** network console and below is what I
observed.

.. image:: {filename}/images/response-content-uwsgi-proxy.png
   :alt: Response with mod_proxy_uwsgi
   :align: center

So response is still gziped but this time only response body was
gziped and Content-Encoding field was set properly which makes browser
to properly uncompress the response body and use it.

So it seems like there is a difference between mod_uwsgi and
mod_proxy_uwsgi implementation. mod_uwsgi was sending the response
along with response headers which was compressed by mod_deflate there
by rendering browser helpless to interpret the response. But
mod_proxy_uwsgi seems to be only sending the response content without
response body and this content was later compressed by mod_deflate and
proper response headers were set by apache before sending it to
browser.

So now whose fault is this? Is it the bug in mod_uwsgi or, mod_deflate
not being able to exclude response headers from compression? I've no
clue! If you have a clue and you want to share it with me, please
consider writing to me over email. My details are available in
`Contacts <http://copyninja.info/contact>`_
