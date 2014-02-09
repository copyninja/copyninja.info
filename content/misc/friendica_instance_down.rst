Friendica instance on my VPS is down
#####################################

:date: 2014-02-08 20:31
:slug: friendica-instance-down
:tags: friendica, sysadmin, php, debian, sandboxing
:author: copyninja
:summary: Friendica instance on my vps went down.

I started running `Friendica <http://friendica.com>`_ instance on my
VPS. With help of `Jonas Smedegaard <http://dr.jones.dk>`_ I managed
to run Friendica in a uWSGI container. The site was running at
*samsargika.copyninja.info* and is no longer accessible.

Since VPS itself was running Debian Wheezy I couldn't run uWSGI with
PHP support on it. *(support for PHP in uWSGI landed after
Wheezy)*. But Jonas was kind enough for me to provide a backported
version.

Recently Wheezy got a security update for PHP and thats where all the
problem started. The backported *uwsgi-plugin-php* was not recompiled
to use security updated PHP and I couldn't upgrade the things. After
few days I noticed first freeze on my VPS and I had to reboot the VPS
to get it online again. The fact I noticed was uWSGI being killed due
to a OOM in syslog but I didn't explore much and consulted Jonas to
get a updated uWSGI. But that didn't happen as Jonas himself is facing
some problem with uWSGI builds. While again checking with aptitude for
upgrade I accidentally confirmed removal of *uwsgi-plugin-php* for
getting security updates :-/. But nothing happened to my running
service as upgrade of libs in Debian doesn't cause the restart of all
services which are using that lib *(desired effect is restart of
service but I don't know the side affects involved)*.

Second freeze happened yesterday and on the reboot *uwsgi-plugin-php*
was missing there by taking my Friendica instance down. More closer
investigation showed the same OOM but this time I noticed each OOM
occurred just after cronjob was running *poller.php* a script which is
actually causing all federation in Friendica. So it was clear there is
something wrong either in *poller.php* or in my setup which was making
it eat memory and freeze my VPS.

But I also found some stupidity I did during configuration which Jonas
also pointed me out.

1. *Installing cronjob inside crontab rather than cron.d*
2. *Installing poller.php crontab for root user :-/*

I basically violated the basic rule by running a unsafe script as root
user, good that script didn't do some crazy stuff. So even though my
instance went down I learnt my lessons


1. *Don't ever ever ever run a unsafe script as root that too through cron*
2. *Sandbox the unsafe script so it can be killed on time rather than
   it taking the whole system down.*
3. *PHP is not really secure, if it was secure there wouldn't be
   security updates and atleast my site would be still running :-D*

So I now need to wait till Jonas get me new shiny backported uWSGI
linked against new PHP on Wheezy and till that time I need to explore
on how I can sandbox the poller.php script.
