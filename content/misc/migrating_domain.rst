Migrating my domain from copyninja.info to copyninja.in
#######################################################

:date: 2023-06-25 16:13
:slug: migrating_domain
:tags: domain, move, newdomain
:author: copyninja
:summary: Just an announcment about domain name move


After holding the domain *copyninja.info* for almost 15 years, I finally let it
expire and bought a new domain, *copyninja.in*. With this move, I also bid
goodbye to my VPS, which I had been using for over 12 years on DigitalOcean.
This particular VPS was initially set up with Debian Wheezy (7) and had been
upgraded over the years to successive Debian versions and finally was running
Debian Bullseye (11).

The main reason for the move was that the *.info* domain was becoming more
expensive every year, and the VPS, which I had upgraded to the $10 USD range,
cost around $12 USD per month with GST included. Since I wasn't really using the
VPS anymore and had recently even broken my DNS and mail server settings, I
decided it was the right time to reduce this additional cost.

Now I have a cheaper *.in* domain, and the VPS is on a minimal configuration at
DigitalOcean, costing $5 USD per month (which becomes almost $7 USD with GST).
Currently, I only run a blog and mail server on this VPS. I will assess if I
really need to keep running the mail server for some more time. If not, I will
move the blog to a hosting service like GitHub Pages and completely get rid of
the VPS.

My email address has now changed, and the new mail can be obtained from this
`link <http://scr.im/newcopyninj>`. I have updated my GPG key and added the new
email as the new UID. I still need to revoke the old domain UID. The key has
already been updated in the Debian Keyring.
