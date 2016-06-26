Integrating Cython extension with setuptools and unit testing
#############################################################

:date: 2016-06-26 19:54 +0530
:slug: cython_setuptools
:tags: python, cython, setuptools, pbr
:author: copyninja
:summary: This post describes how to integrate a cython extension with
	  setuptools.


I was reviewing changes for `indic-trans
<https://github.com/libindic/indic-trans>`_ as part of GSoC 2016. The
module is an improvisation for our original transliteration module
which was doing its job by substitution.

This new module uses machine learning of some sort and utilizes
*Cython*, *numpy* and *scipy*. Student had kept pre-compiled shared
library in the git tree to make sure it builds and passes the
test. But this was not correct way. I started looking at way to build
these files and remove it from the code base.

There is a `cython documentation
<http://docs.cython.org/src/quickstart/build.html>`_ for distutils but
none for setuptools. Probably it is similar to other Python extension
integration into setuptools, but this was first time for me so after a
bit of searching and trial and error below is what I did.

We need to use `Extensions` class from setuptools and give it path to
modules we want to build. In my case `beamsearch` and `viterbi` are 2
modules. So I added following lines to setup.py

.. code-block:: python

   from setuptools.extension import Extension
   from Cython.Build import cythonize

   extensions = [
    Extension(
        "indictrans._decode.beamsearch",
        [
            "indictrans/_decode/beamsearch.pyx"
        ],
        include_dirs=[numpy.get_include()]
    ),
    Extension(
        "indictrans._decode.viterbi",
        [
            "indictrans/_decode/viterbi.pyx"
        ],
        include_dirs=[numpy.get_include()]
    )

   ]

First argument to `Extensions` is the module name and second argument
is a list of files to be used in building the module. The additional
`inculde_dirs` argument is not normally necessary unless you are
working in virtualenv. In my system the build used to work without
this but it was failing in Travis CI, so added it to fix the CI
builds. OTOH it did work without this on Circle CI.

Next is provide this `extensions` to `ext_modules` argument to `setup`
as shown below

.. code-block:: python

   setup(
    setup_requires=['pbr'],
    pbr=True,
    ext_modules=cythonize(extensions)
   )

And for the reference here is full setup.py after modifications.

.. code-block:: python

   #!/usr/bin/env python

   from setuptools import setup
   from setuptools.extension import Extension
   from Cython.Build import cythonize

   import numpy


   extensions = [
     Extension(
        "indictrans._decode.beamsearch",
        [
            "indictrans/_decode/beamsearch.pyx"
        ],
        include_dirs=[numpy.get_include()]
     ),
     Extension(
        "indictrans._decode.viterbi",
        [
            "indictrans/_decode/viterbi.pyx"
        ],
        include_dirs=[numpy.get_include()]
     )
   ]

   setup(
     setup_requires=['pbr'],
     pbr=True,
     ext_modules=cythonize(extensions)
   )

So now we can build the extensions (shared library) using following
command.

.. code-block:: shell

   python setup.py build_ext

Another challenge I faced was missing extension when running test. We
use pbr in above project and testrepository with subunit for running
tests. Looks like it does not build extensions by default so I
modified the Makefile to build the extension in place before running
test. The `travis` target of my Makefile is as follows.

.. code-block:: make

   travis:
	[ ! -d .testrepository ] || \
		find .testrepository -name "times.dbm*" -delete
	python setup.py build_ext -i
	python setup.py test --coverage \
		--coverage-package-name=indictrans
	flake8 --max-complexity 10 indictrans

I had to build the extension in place using `-i` switch. This is
because other wise the tests won't find the
`indictrans._decode.beamsearch` and `indictrans._decode.viterbi
modules`. What basically `-i` switch does is after building shared
library symlinks it to the module directory, in ourcase
`indictrans._decode`

The test for existence of .testrepository folder is over come `this
bug  <https://bugs.launchpad.net/testrepository/+bug/1229445>`_ in
testrepository which results in test failure when running tests using
`tox`.
