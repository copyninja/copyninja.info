Aptly, Systemd and dput: Debian Repository with incoming mechanism
##################################################################

:date: 2020-06-07 12:49 +0530
:slug: aptly-systemd-dput
:tags: debian-repo, aptly, systemd
:author: copyninja
:status: draft
:summary: Post describes about setting up a Debian Repository using aptly and
          using systemd with dput to trigger incoming mechanism

It has been more than a year from my last blog post. Its been a busy year and
life has its own ways to keep you busy. So here I'm again after a year to write
something I solved a couple of days back.

Problem
=======

Setup a APT repository server where one can upload their packages and it gets
published.

Though statement is simple it needed following things

1. apt repository setup
2. process uploaded package and update published repository.


1. APT Repository Setup
-----------------------

My first selection for this was reprepro which works well but has one short
coming, it does not support multiple version of same package. For my use
case I need repository to have multiple versions of same package. A patch has
been proposed for reprepro in `#570623 <https://bugs.debian.org/570623>`_ but
has not been merged and there is no activity for quite some time. I tried to
build it but without success. As I did not have much time to investigate and did
not want to adopt the patch before it officially got accepted by upstream I
ruled it out.

I tried mini-dinstall next. mini-dinstall does support having multiple version
of same package but the catch is repo can't be mirrored using debmirror. This
was again  a use case and there is a very old bug `#360529
<https://bugs.debian.org/360529>`_ which was never fixed. So I ruled out
mini-dinstall as well.

So finally without much options left I came to aptly. aptly is a great tool but
is not been actively maintained by the author from December 2019. But with no
other options I thought of giving it a try.

aptly stores the repository and data store locally under *~/.aptly/* folder.
To allow outside word to access the repository it needs to be first published.
Aptly provides 3 endpoints for publishing

1. *S3* (AWS)
2. *Swift* (Openstack)
3. Filesystem: local storage on box where aptly is running

These endpoints can be configured in the config file which can be either in
*~/.aptly.conf* or */etc/aptly.conf*. A JSON file. A sample file with filesystem
endpoint configuration is as follows.

.. code-block:: json

           {
             "rootDir": "$HOME/.aptly",
             "downloadConcurrency": 4,
             "downloadSpeedLimit": 0,
             "architectures": [],
             "dependencyFollowSuggests": false,
             "dependencyFollowRecommends": false,
             "dependencyFollowAllVariants": false,
             "dependencyFollowSource": false,
             "dependencyVerboseResolve": false,
             "gpgDisableSign": false,
             "gpgDisableVerify": false,
             "gpgProvider": "gpg",
             "downloadSourcePackages": false,
             "skipLegacyPool": true,
             "ppaDistributorID": "ubuntu",
             "ppaCodename": "",
             "skipContentsPublishing": false,
             "FileSystemPublishEndpoints": {
               "test1": {
                 "rootDir": "/opt/srv1/aptly_public",
                 "linkMethod": "symlink"
               },
               "test2": {
                 "rootDir": "/opt/srv2/aptly_public",
                 "linkMethod": "copy",
                 "verifyMethod": "md5"
               },
               "test3": {
                 "rootDir": "/opt/srv3/aptly_public",
                 "linkMethod": "hardlink"
               }
             }
           }

Each endpoint is given a name in this case *test1, test2 and test3*. And they
can export it to different location and using different methods. More details
about all these can be found in `aptly documentation
<https://www.aptly.info/doc/feature/filesystem/>`_. If you decide all repository
will be supporting a list of architecture that can be added to configuration
file. In my case I decided to go with per repository based architecture which
will be give more flexibility.

One more thing I noticed was aptly packaged in Debian does not work with gnupg2
and you need to have gnupg1 around and re-import all keys to gnupg1 as well so
it is recognized. I see that 1.4 version of aptly is prepared in salsa but not
yet uploaded. So I decided to download the aptly from the upstream repo and use
it instead.

aptly provides various way to publish repository. Its preferred way is to take a
snapshot of the repository and publish the snapshot. But in my case I simply
decided to publish the repository and update the published repo whenever new
package is uploaded.
