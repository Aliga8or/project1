#!/usr/bin/env python2.7

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASEURI = "postgresql://ns3001:3r369@104.196.175.120/postgres"
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #

  cursor = g.conn.execute("SELECT name FROM users")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #

  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html")

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the function name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("anotherfile.html")


@app.route('/recipe', methods=['GET', 'POST'])
def recipe():
  print "Entered recipe"
  if request.method == 'POST':
	  print "Entered POST"
	  tag = request.form['tag']
	  ingredient = request.form['ingredient']
	  cmd = 'SELECT rec.name FROM Ingredient as ing, Includes_ingredient as inc, recipe_create as rec WHERE ing.ing_id = inc.ing_id and inc.rid = rec.rid and ing.name = (:ingredients)'
	  cursor = g.conn.execute(text(cmd), ingredients = ingredient)
	  rows = []
	  for result in cursor:
		rows.append(result['name'])
	  cursor.close()
	  context = dict(data = rows)
	  print "Exiting POST"
	  return render_template("recipe.html", **context)
  print "Didn't enter GET, now exiting"
  return render_template("recipe.html")

@app.route('/show_recipe', methods=['GET'])
def show_recipe():
  print "Entered show recipe"
  htmlStr = ""
  if request.method == 'GET': 
	print "Entered GET"
	rid = 3 #get from session
	
	cmd = 'SELECT * FROM recipe_create WHERE rid=(:input_rid)'
	cmd1 = 'SELECT ing.name, inc.quantity, inc.units FROM ingredient as ing, includes_ingredient as inc WHERE inc.rid=(:input_rid) AND inc.ing_id=ing.ing_id'
	cmd2 = 'SELECT * FROM has_tag WHERE has_tag.rid = (:input_rid)'
	cmd3 = 'SELECT u.name, c.content, c.post_time FROM comment_make as c, users as u WHERE c.rid=(:input_rid) AND c.uid = u.uid'
	cmd4 = 'SELECT r.name FROM recipe_create as r, similar_recipes as s WHERE s.rid1 = (:input_rid) AND s.rid2=r.rid'

	cursor = g.conn.execute(text(cmd), input_rid = rid)
	cursor1 = g.conn.execute(text(cmd1), input_rid = rid)
	cursor2 = g.conn.execute(text(cmd2), input_rid = rid)
	cursor3 = g.conn.execute(text(cmd3), input_rid = rid)
	cursor4 =
	#recipe title
	htmlStr += "<div class='special'>Recipe:</div>"
	for result in cursor:
		htmlStr += "<div class='eList'>"+str(result['name'])+"</div>"
	#ingredients
	htmlStr += "<div class='special'>Ingredients:</div>"
	for result in cursor1:
		htmlStr += "<div class='eList'>"+str(result['quantity'])+" "+str(result['units'])+" "+str(result['name'])+"</div>"
	#tags
	htmlStr += "<div class='special'>Tags:</div>"
	for result in cursor2:
		htmlStr += "<div class='eList'>"+str(result['name'])+"</div>"
	#comments
	htmlStr += "<div class='special'>Comments:</div>"
	for result in cursor3:
		htmlStr += "<div class='eList'>("+str(result['post_time'])+") User "+str(result['name'])+" says: "+str(result['content'])+"</div>"
	#similar recipes
	htmlStr += "<div class='special'>Recipes Similar to This:</div>"
	for result in cursor4:
		htmlStr += "<div class='eList'>"+str(result['name'])+"</div>"

  print "Exiting show recipe"
  return render_template("show_recipe.html", htmlStr=htmlStr)

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
