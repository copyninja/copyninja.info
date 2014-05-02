Note to Self: How to use url_for in Flask application
#####################################################

:date: 2014-05-02 11:50
:slug: using-url-for-in-flask
:tags: python, programming, flask, webapp, notetoself
:author: copyninja
:summary: Just a note to self on how to use url_for in Flask
	  application and jinja2 template system.       


`url_for` is normally used to avoid hard coding of URL in Flask based
webapps. I've been using it in SILPA `port
<https://github.com/Project-SILPA/Silpa-Flask>`_ written using Flask
by. But this was written long back and written as POC to show for
Santhosh author of SILPA app which even managed to go into production
:-). Recently I started organizing the code and started using
`flask.Blueprint` which was previously written using
`flask.views.MethodView` class and here I started facing problem with
old templates. I'm just gonna explain what is the difference when
using url_for with `MethodView` and `Blueprint`.

Lets have some sample code for `MethodView` first, this code is from
`Flask` documentation.

.. code-block:: python

   from flask.views import MethodView

   class UserAPI(MethodView):

	  def get(self):
	      users = User.query.all()
              ...

	  def post(self):
	      user = User.from_form_data(request.form)
              ...

   app.add_url_rule('/users/', view_func=UserAPI.as_view('users'))


Here we have a view which is derived from `MethodView` which has logic
on how to handle the requests. We use `add_url_rule` to register rule
to handle `/users/` url end point and we pass the class as view
function which is done by `as_view` class method and we can refer this
method in our Jinja2 templates using name `users`. So a statement like

.. code-block:: python

   url_for('users')


in our templates will be converted to `/users/` URL when page is
rendered to client by Flask.

Now when I replaced the `MethodView` in favor of `Blueprint` I started
getting up `werkzeug.routing.BuildError` thrown on my face and I had
no clue why!. Yeah I know I'm bad at reading documentation but even
after reading documentation I was still thinking that

.. code-block:: python

   url_for('/')

should return me a proper URL and I was wondering why its
failing. Finally after re-reading documentation for `url_for` it was
becoming clear to me, `url_for` definition looks like below

.. code-block:: python

    flask.url_for(endpoint, **values)

Here `endpoint` is actually a function which is supposed to be serving
the URL and `**values` is the arguments for this function. The URL in
question should be defined in python code using decorator. In my case
following is the new function serving the web pages for SILPA.

.. code-block:: python

   bp = Blueprint('frontend', __name__)


   @bp.route(_BASE_URL, defaults={'page': 'index.html'})
   @bp.route(_BASE_URL + '<page>')
   def serve_pages(page):
	  if page == "index.html":
	     return render_template('index.html', title='SILPA',
                                  main_page=_BASE_URL,
                                  modules=_modulename_to_display)
	  elif page == "License":
	     return render_template('license.html', title='SILPA License',
                                   main_page=_BASE_URL,
                                   modules=_modulename_to_display)
	  elif page == "Credits":
              return render_template('credits.html', title='Credits',
                                   main_page=_BASE_URL,
                                   modules=_modulename_to_display)
	  elif page == "Contact":
              return render_template('contact.html', title='Contact SILPA Team',
                                   main_page=_BASE_URL,
                                   modules=_modulename_to_display)
	  else:
              # modules requested!.
              if page in _display_module_map:
                  return render_template(_display_module_map[page] + '.html',
                                       title=page, main_page=_BASE_URL,
                                       modules=_modulename_to_display)
	      else:
	          # Did we encounter something which is not registered by us?
		  return abort(404)


You can ignore function code but just note the decorators, here I'm
registering the function `serve_pages` with `page` as argument for URL
patterns `/` and `/<page>`, `_BASE_URL` here is mount point of
application it can be just `/` or `/mountpoint` depending on that URL
registered changes. Now I need to modify code for all `url_for` in my
template to look like below

.. code-block:: python

   url_for('.serve_pages', page='/License') # for /License
   url_for('.serve_pages') # which will turn in to /index.html

The `.` in front of function is for referring current Blueprint, in my
case the Flask will consider it as `frontend.serve_pages` as function
name and generates appropriate URL at run time.

So my fault was misunderstanding `endpoint` argument as URL endpoint
but where as its actually function name supposed to serve the
page. But when using MethodViews I can simply convert class to a
function with my preferred name just like `UserAPI.as_view('/')` so
`url_for('/')` just works.
