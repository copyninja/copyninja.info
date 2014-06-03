Using WSME with Flask microframework
####################################

:date: 2014-06-03 20:15
:slug: wsme-with-flask
:tags: python, programming, wsme, rest
:author: copyninja
:summary: This is short guide on how to use wsme with Flask
          applications, writing this because I felt documentation is
          lacking.

After reading `Julien Danjou's <http://julien.danjou.info>`_ I found
out WSME (Web Service Made Easy) a Python framework which allows us to
easily create Web Services in Python. For `SILPA
<http://silpa.org.in>`_ we needed a REST like interface and I thought
of giving it try as WSME readily advertised the Flask integration, and
this post was born when I read the documentation for Flask
integration.

First of all Flask is a nice framework which will right way allow
development of REST api for simple purposes, but my requirement was
bit complicated where I had to expose function in a separate python
modules through SILPA. I think detailed requirement can be part of
another post, so let me explain how to use WSME with Flask app.

WSME integration with Flask is done via decorator function
`wsmeext.flask.signature` which expects you to provide it with
signature of function to expose. And `here
<http://wsme.readthedocs.org/en/latest/integrate.html#wsmeext.flask.signature>`_
is its documentation, basically signature of `signature` function is

.. code-block:: python

   wsmeext.flask.signature(return_type, *arg_types, **options)

Yeah thats all docs have sadly.

So basically exposing is the only thing WSME handles for us here,
routing and other stuffs need to be done by Flask itself. So lets
consider a example, simple function to add as shown below.

.. code-block:: python

   def add(a, b):
       return a + b

For providing REST like service, all you need below code.

.. code-block:: python

   from flask import Flask
   from wsmeext.flask import signature

   app = Flask(__name__)
   
   @app.route('/add')
   @signature(int, int, int)
   def add(a, b):
       return a + b

   if __name__ == '__main__':
	  app.run()

So first argument to `signature` is return type of function and rest
arguments are the argument to function to be exposed. Now you can
access the newly exposed service by visiting
*http://localhost:5000/add* but don't forget to pass the arguments
either via query string or through post. You can restrict methods of
access via Flask's `route`.

So what's the big deal of not having docs right?.. Well fun part began
when we use bit more complex return type like *dictionaries* or
*lists* . Below is modified code I'm using to demonstrate problem I
faced during using `dict` as return type.

.. code-block:: python

   from flask import Flask
   from wsmeext.flask import signature

   app = Flask(__name__)

   @app.route('/add')
   @signature(dict, int, int)
   def add(a, b):
       return {"result": a + b}

   if __name__ == '__main__':
       app.run()


Basically I'm returning a dictionary containing result now, for
demonstration purpose. When I run the application **boom** python
barked at me with following message.

.. code-block:: py3tb

   Traceback (most recent call last):
   File "wsme_dummy.py", line 7, in <module>
    @signature(dict, int, int)
   File "c:\Users\invakam2\.virtualenvs\wsmetest\lib\site-packages\wsmeext\flask.py", line 48, in decorator
    funcdef.resolve_types(wsme.types.registry)
   File "c:\Users\invakam2\.virtualenvs\wsmetest\lib\site-packages\wsme\api.py", line 109, in resolve_types
    self.return_type = registry.resolve_type(self.return_type)
   File "c:\Users\invakam2\.virtualenvs\wsmetest\lib\site-packages\wsme\types.py", line 739, in resolve_type
    type_ = self.register(type_)
   File "c:\Users\invakam2\.virtualenvs\wsmetest\lib\site-packages\wsme\types.py", line 668, in register
    class_._wsme_attributes = None
   TypeError: can't set attributes of built-in/extension type 'dict'


After going through code from files involved in above traces this is
what I found

1. `wsmeext.flask.signature` inturn uses `wsme.signature` which is
   just alias of `wsme.api.signature`.
2. Link in documentation in sentence *See @signature for parameter
   documentation* is broken and should actually link to
   `wsme.signature` in docs.
3. `wsme.signature` actually calls `resolve_type` to check on types of
   return and arguments. This function checks if types are instance of
   `dict` or `list` in such cases it creates instances of
   `wsme.type.DictType` and `wsme.type.ArrayType` respectively with
   values from the argument.
4. When I just passed built-in type `dict` the control went to else
   part which just passed the type to `wsme.type.Register.registry`
   function which tries to set the attribute `_wsme_attribute` which
   actually raises `TypeError` as we can't set attribute for built-in
   types.

So by inspecting code of `wsme.type.Registry.resolve_type` and
`wsme.type.Registry.register` its clear that what signature expects
when arguments or return type is dictionary/list is instance of
dictionary/list with `type` of value in it. May be sentence is bit
vague but I'm not sure how to put it more clearly, as an example in
our case add function returns dictioanry with key as string and value
as int, so return type argument for signature will be `{str:
int}`. Similarly if you return array with int values it will be
`[int]`.

With above understanding our add function now looks like below.

.. code:: python

   @signature({str: int}, int, int)
   def add(a, b):
      return {'result': a + b}


and now code worked just fine!. What I couldn't figure out here is
there is no way to have `tuple` as return value or argument, but I
guess that is not big deal.

So immidiate task for me after finding this is fix the link in
documentation to point to `wsme.signature` and probably put some note
some where in documentation about above finding.
