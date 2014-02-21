Kontalk FLOSS alternative for Whatsapp and Co.
##############################################

:date: 2014-02-21 19:51
:slug: kontalk-messaging
:tags: smartphone,messaging,whatsapp,foss
:author: copyninja
:summary: FLOSS alternative for Whatsapp.

So *Whatsapp* has been acquired by Facebook and this news is still hot
and people are discussing it all over the twitterverse. So I took this
opportunity to stop using *Whatsapp* and removed it from my
phone. Possibly I could have deleted my account but who cares.

Anyway I've been searching for a secure and FLOSS alternative for
*Whatsapp* for quite some time now, few days ago I found about
*Telegram* but after reading `post
<http://blog.tincho.org/posts/Telegram/>`_ by Tincho on planet Debian,
I decided not to use it.  Recently while going through the talk list
for fossmeet.in I found link for `Kontalk <http://kontalk.org>`_ in a
privacy awareness talk `proposal
<http://funnel.fossmeet.in/2014/61-i-have-nothing-to-hide-i-dont-care-about-privacy>`_
by `Praveen <http://qa.debian.org/developer.php?login=praveen>`_ and
thought I should give it a try.  So below is my first feelings about
*Kontalk*.

Installation and Activation
===========================

Kontalk can be installed from `playstore
<https://play.google.com/store/apps/details?id=org.kontalk>`_ for
verification purpose it requests your phone number and country code
and request for verification. This should send a SMS with a code which
should be entered in the text box given and app is ready to use. There
is also a possibility to use pre-existing verification code (if you
got one from developer directly, read below for details).

I did see some glitches like I never got the SMS delivered to my phone
after 2 attempts and a days wait. Then I went ahead and reported a
`bug <https://code.google.com/p/kontalk/issues/detail?id=179>`_ and
the main developer was quick to respond. After a discussion it was
noticed that SMS was blocked by spam filters. He also mentioned its
tough to get SMS delivered to India. He was kind enough to provide me
with a verification code and I used the *Use existing code* option to
enter it and get *Kontalk* activated.

The SMS delivery inconsistency is still present for India (and may be
other nations too) some people get code immidiately others may be
after couple of days and some might not. Upstream is already working
on a possible `workaround
<https://code.google.com/p/kontalk/issues/detail?id=141>`_.

User Experience
===============

Now coming to usage part, the UI is neat and clean, I won't say super
polished as *Whatsapp* or other popular apps but its really *neat* and
easy to use. Some points which I like are

- Ability to hide presence, so others won't know you are online or
  offline. (unlike *Whatsapp* which advertises last seen)
- Encrypted messages and ability to optin or optout.
- Encrypted status messages! Only user with your phone number can see
  your status. (Cool isn't it).
- Manually requesting to find contacts who already uses
  kontalk!. Right it doesn't read your contact list without your
  permission you need to refresh to check who in your contacts is
  using Kontalk.
- Attach and smiley options in the top right corner of Chat window
  which allows easy accessing unlike keyboard - smiley switching of
  *Whatsapp*.
- No automatic download of media contents which is shared. Yes by
  default it doesn't download any picture or video automatically if
  you want to see something click on it and select download.
- Running your own server for Kontalk! Now thats something which is
  interesting for people who doesn't want to host their data on some
  other peoples infrastructure. Code for server is available at
  `xmppserver
  <https://code.google.com/p/kontalk/source/browse?repo=xmppserver>`_
  repo.

But there are some rough edges also but I'm sure this can be
improved. But some points which I noticed are

- Contact name disappears and only number is displayed. This is
  something which happened with one of my contact so I'm not really
  sure its a bug.
- My friend noticed all his existing contacts suddenly vanished when
  he refreshed contacts list. Again this is possible bugs and we are
  considering reporting it upstream.
- No group chats yet. I don't see a option to do that yet.
- Attachment at the moment is restricted only to pictures (and video?
  never tried) and uploading takes quite sometime and sometime hangs
  forever.

So I'm considering forwarding these to upstream and help them by
providing enough data so these can be fixed.

Technical Side
==============

All code for client server and protocol specs are available under
GPL-v3 at the `Kontalk project <https://code.google.com/p/kontalk>`_
site. Server software is written in Python and I guess uses XMPP (but
I've not cross verified). Server also uses MySQL as database. These
can be hosted on our own servers but possibly needs more than that
like SMS sending options etc.

Conclusion
==========

In my views *Kontalk* can become a great alternative for *Whatsapp*
and co from Free Software world and I encourage every one to give it a
try which will be the first step to help improving it.


 Disclaimer: I'm not a privacy or security expert so whatever I shared
 above are what I noticed and experts may see something different than
 this. In any case I welcome comments and suggestions.
