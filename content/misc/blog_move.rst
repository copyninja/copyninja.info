Moving weblog from Jekyll to Pelican
####################################

:date: 2014-02-02 8:55
:slug: blog-move
:tags: jekyll,pelican,blog
:author: copyninja
:summary: Re-creating blog using Pelican	  


Its been a while and I was not actively blogging. I wanted to start
blogging again but I was for some reason not happy with *Jekyll*
static site generator which was powering my previous site. So I took
this chance to explore other static site generators and redesign my
blog.

I explored a bit of Pelican, Nikola and Frog. I didn't feel
comfortable with *Nikola*. *Frog* is a static site generator written
using `*Racket* <http://racket-lang.org/>`_ and since I'm learning
Scheme using racket I was leaning towards using it but at the last
moment I decided to settle with *Pelican*. The main reason for not
using *Frog* was that I just wanted to get my site up rather than
waiting for me to complete learning racket and use Frog.

My feeling about Pelican is that its a nice tool and is simple and
gives all basic things like generating RSS/ATOM feeds and nice theming
support. In case of Jekyll I had to write custom page for creating RSS
feed and had pain in creating my first theme (yeah I'm not a
designer). But now things might have changed in Jekyll land but anyway
I don't care anymore.

New design uses `pelican-bootstrap3
<https://github.com/DandyDev/pelican-bootstrap3>`_ theme and there is
no comment facility available. If you want to comment or suggesting
things on my post consider writing mail to me :-).

So what happened to older entries? Moving the old entries from Jekyll
format to Pelican was real PITA so I just renamed my old site to
`blog-archive <http://blog-archive.copyninja.info>`_. So this is a
from scratch site and will contain only new entries. So how do you
like my new blog design? :-)
