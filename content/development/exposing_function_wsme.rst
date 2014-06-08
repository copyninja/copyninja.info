Exposing function in python module using entry_points, WSME in a Flask webapp
#############################################################################

:date: 2014-06-07 18:10
:slug: entry_point_wsme.rst
:tags: python, programming, wsme, rest, setuptools	  
:author: copyninja
:summary: In this post I try to explain how to expose a function in a
          python module as REST service using WSME from an Flask
	  application using setuptools entry_points feature.

The heading might be ambiguous, but I couldn't figure out better
heading so let me start by explaining what I'm trying to solve here.

Problem
-------

I have a python module which contains a function which I want to
expose as a REST web service in a Flask application. I use WSME for
Flask application, which actually needs signature of function in
question and problem comes to picture because function to be exposed
is foreign to Flask application, it resides in separate python module.


Solution
--------

While reading `Julien Danjou's <http://julien.danjou.info/>`_ *Hackers
Guide To Python* book I came across the setuptools `entry_points`
concept which can be used to extend existing feature of a tool like
plug-ins. So here I'm going to use this `entry_points` feature from
setuptools to provide function in the module which can expose the
signature of function[s] to be exposed through REST. Of course this
means I need to modify module in question to write entry_points and
function for giving out signature of function to be exposed.

I will explain this with small example. I have a dummy module which
provides a add function and a function which exposes the add functions
signature.

.. code-block:: python

   
   def add(a, b):
       return a + b

   def expose_rest_func():
       return [add, int, int, int]

This is stored in `dummy/__init__.py` file. I use `pbr` tool to
package my python module. Below is content of `setup.cfg` file.

.. code-block:: python

   [metadata]
   name = dummy
   author = Vasudev Kamath
   author-email = kamathvasudev@gmail.com
   summary = Dummy module for testing purpose
   version = 0.1
   license = MIT
   description-file =
     README.rst
   requires-python = >= 2.7

   [files]
   packages =
     dummy

   [entry_points] =
   myapp.api.rest =
     rest = dummy:expose_rest_func


The special thing in above file is `entry_points` section, which
defines function to be hooked into entry_point. In our case
entry_point `myapp.api.rest` is used by our Flask application to
interact with modules which expose them. The function which will be
got accessing the entry_point is `expose_rest_func` which gives the
function to be exposed its arg types and return types as a list.

If we are looking at only supporting python3 it was sufficient to know
function name only and use `function annotations
<http://legacy.python.org/dev/peps/pep-3107>`_ in function
definition. Since I want to support both python2 and python3 this is
out of question.

Now, just run the following command in virtualenv to get the module
installed.

.. code-block:: shell-session

   PBR_VERSION=0.1 python setup.py sdist
   pip install dist/dummy_module-0.1.tar.gz

Now if you want to see if the module is exposing entry_point or not
just use `entry_point_inspector` tool after installing you will get a
command called `epi` if you run it as follows you should note the
dummy_module in its output

.. code-block:: shell-session

   epi group list
   +-----------------------------+
   | Name                        |
   +-----------------------------+
   | cliff.formatter.completion  |
   | cliff.formatter.list        |
   | cliff.formatter.show        |
   | console_scripts             |
   | distutils.commands          |
   | distutils.setup_keywords    |
   | egg_info.writers            |
   | epi.commands                |
   | flake8.extension            |
   | setuptools.file_finders     |
   | setuptools.installation     |
   | myapp.api.rest              |
   | stevedore.example.formatter |
   | stevedore.test.extension    |
   | wsme.protocols              |
   +-----------------------------+

So our entry_point is exposed now, we need to access it in our Flask
application and expose the function using WSME. It is done by below
code.

.. code-block:: python

   from wsmeext.flask import signature

   import flask
   import pkg_resources


   def main():
      app = flask.Flask(__name__)
      app.config['DEBUG'] = True
      for entrypoint in pkg_resources.iter_entry_points('myapp.api.rest'):
          # Ugly but fix is only supporting python3
          func_signature = entrypoint.load()()
          app.route('/' + func_signature[0].__name__, methods=['POST'])(
              signature(func_signature[-1],
                  *func_signature[1:-1])(func_signature[0]))
      app.run()

   if __name__ == '__main__':
       main()

entry_point `myapp.api.rest` are iterated using the pkg_resources
package provided by setuptools, when I load the entry_point I get back
the function to be used which is called in same place to get function
signature. Then I'm calling Flask and WSME decorator functions (yeah
instead of decorating I'm using them directly over function to be
exposed).

The code looks bit ugly at the place where I'm accessing list using
slices but I can't help it due to limitation of python2 with python3
there is new packing and unpacking stuff which makes code look bit
more cooler see below.

.. code-block:: python

   from wsmeext.flask import signature

   import flask
   import pkg_resources


   def main():
       app = flask.Flask(__name__)
       app.config['DEBUG'] = True
       for entrypoint in pkg_resources.iter_entry_points('silpa.api.rest'):
           func, *args, rettype = entrypoint.load()()
           app.route('/' + func.__name__, methods=['POST'])(
           signature(rettype, *args)(func_signature[0]))
       app.run()

   if __name__ == '__main__':
       main()

You can access the service at `http://localhost:5000/add` depending on
`Accept` header of HTTP you will get either XML or JSON response. If
you access it from browser you will get XML response.

Usecase
-------

Now if you are wondering what is the reason behind this experience,
this is for `SILPA Project <http://silpa.org.in>`_. I'm trying to
implement REST service for all Indic language computing module. Since
all these module are independent of SILPA which is a Flask web app I
had to find a way to achieve this, and this is what I came up with.

Conclusion
----------

I'm not sure if there is any other approaches to achieve this, if
there I would love to hear about them. You can write your comments and
suggestion over `email <http://scr.im/vasudev>`_
