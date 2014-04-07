Loading Python modules/plug-ins at runtime
##########################################

:date: 2014-04-07 21:55
:slug: dynamic-module-loading
:tags: python, modules, import, programming, importlib
:author: copyninja
:summary: Post describes about loading arbitrary python files or
          modules during runtime.

Some times it is desired to load arbitrary python files or pre-
installed python modules during application run time.I had encountered
2 such usecases, one is in `SILPA application <http://silpa.org.in>`_
and other is `dictionary-bot
<https://github.com/copyninja/dictionary-bot>`_ which I was
refactoring recently.

Case 1: Loading installed python module
---------------------------------------

In case of SILPA I need to load pre-installed modules and here is the
`old code
<https://github.com/Project-SILPA/Silpa-Flask/blob/master/core/modulehelper.py#L24>`_
, that is a bit hacky code I copied from Active State Python
recipies. I found a bit better way to do it using `importlib` module
as shown below.

.. code-block:: python

   from __future__ import print_function
   import sys
   import importlib

   def load_module(modulename):
       mod = None
       try:
           mod = importlib.import_module(modulename)
       except ImportError:
           print("Failed to load {module}".format(module=modulename),
		        file=sys.stderr)
       return mod

Here `importlib` itself takes care of checking if modulename is
already loaded by checking `sys.modules[modulename]`, if loaded it
returns that value, otherwise it loads the module and sets it to
`sys.modules[modulename]` before returning module itself.


Case 2: Loading python files from arbitrary location
----------------------------------------------------

In case of dictionary bot my requirement was bit different, I had some
python files lying around in a directory, which I wanted to plug into
the bot during run time and use them depending on some conditions. So
basic structure which I was looking was as follows.


.. raw:: html

   <pre>
	 pluginloader.py
	 plugins
	 |
	 |__ aplugin.py
	 |
	 |__ bplugin.py
   </pre>  

`pluginloader.py` is the file which needs to load python files under
`plugins` directory. This was again done using `importlib` module as
shown below.

.. code-block:: python

   import os
   import sys
   import re
   import importlib

   def load_plugins():
       pysearchre = re.compile('.py$', re.IGNORECASE)
       pluginfiles = filter(pysearchre.search,
                              os.listdir(os.path.join(os.path.dirname(__file__),
                                                    'plugins')))
       form_module = lambda fp: '.' + os.path.splitext(fp)[0]
       plugins = map(form_module, pluginfiles)
       # import parent module / namespace
       importlib.import_module('plugins')
       modules = []
       for plugin in plugins:
		if not plugin.startswith('__'):
		    modules.append(importlib.import_module(plugin, package="plugins"))

       return modules

Above code first searches for all python file under specified
directory and creates a relative module name from it. For eg. file
`aplugin.py` will become `.aplugin`. Before loading modules itself we
will load the parent module in our case `plugins`, this is because
**relative imports in python expects parent module to be already
loaded**. Finally for relative imports to work with
`importlib.import_module` we need to specify parent module name in
`package` argument. Note that we ignore files begining with *__*, or
specifically we don't want to import __init__.py, this will be done
when we import parent module.

The above code was inspired from a `answer on StackOverflow
<https://stackoverflow.com/a/3381582>`_, which uses `imp` module, I
avoided `imp` because its been deprecated from *Python 3.4* in favor
of `importlib` module.
