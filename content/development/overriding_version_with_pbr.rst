Overriding version information from setup.py with pbr
#####################################################

:date: 2017-07-16 20:53 +0530
:slug: override-version-pbr
:tags: python, pbr, zfec
:author: copyninja
:summary: Post to explain a workaround I did to override version information
          detected by pbr for zfec upstream.

I recently raised a `pull request <https://github.com/tahoe-lafs/zfec/pull/5>`_
on zfec for converting its python packaging from pure `setup.py` to `pbr` based.
Today I got review from *Brian Warner* and one of the issue mentioned was
`python setup.py --version` is not giving same output as previous version of
`setup.py`.

Previous version used `versioneer
<https://github.com/warner/python-versioneer>`_ which extracts version
information needed from VCS tags. Versioneer also provides flexibility of
specifying type of VCS used, style of version, tag prefix (for VCS) etc. `pbr`
also does extract version information from git tag but it expects git tag to be
of format *tags/refs/x.y.z* format but *zfec* used a `zfec-` prefix to tag
(example *zfec-1.4.24*) and *pbr* does not process this. End result, I get a
version in format *0.0.devNN* where *NN* is number of commits in the repository
from its inception.

Me and Brian spent few hours trying to figure out a way to tell pbr that we
would like to override version information it auto deduces, but there was none
other than putting version string in `PBR_VERSION` environment variable. That
documentation was contributed by me `3 years back to pbr project.
<https://github.com/openstack-dev/pbr/commit/007f4ee2abf818b4b18b6e8347da1d4eb2e0ad9c>`_

So finally I used `versioneer` to create a version string and put it in the
environment variable *PBR_VERSION*.

.. code-block:: python

   import os
   import versioneer

   os.environ['PBR_VERSION'] = versioneer.get_version()

   ...
   setup(
       setup_requires=['pbr'],
       pbr=True,
       ext_modules=extensions
   )

And added below snippet to *setup.cfg* which is how versioneer can be configured
with various information including tag prefixes.

.. code-block:: ini

   [versioneer]
   VCS = git
   style = pep440
   versionfile_source = zfec/_version.py
   versionfile_build = zfec/_version.py
   tag_prefix = zfec-
   parentdir_prefix = zfec-

Though this work around gets the work done, it does not feel correct to set
environment variable to change the logic of other part of same program. If you
guys know the better way do let me know!. Also probably I should consider filing
an feature request against `pbr` to provide a way to pass tag prefix for version
calculation logic.
