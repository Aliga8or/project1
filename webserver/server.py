#!/usr/bin/env python2.7

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASEURI = "postgresql://ns3001:3r369@104.196.175.120/postgres"
engine = create_engine(DATABASEURI)
size = 20

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
  print "Executing teardown_request !!!"
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


@app.route('/search', methods=['GET', 'POST'])
def search_recipe():
  print "Entered recipe"
  htmlStr = "<form name='searchForm' action='/search' method='POST'>"
  
  cmd = 'SELECT DISTINCT cuisine FROM recipe_create'
  cursor = g.conn.execute(text(cmd))
  htmlStr += "<div class='special'> Cuisine: <select name='cuisine'>"
  htmlStr += "<option value='NA'>----------</option>"
  for result in cursor:
	htmlStr += "<option value='"+str(result['cuisine'])+"'>"+str(result['cuisine'])+"</option>"
  htmlStr += "</select> </div>"
  
  cmd = 'SELECT DISTINCT category FROM recipe_create'
  cursor = g.conn.execute(text(cmd))
  htmlStr += "<div class='special'> Category: <select name='category'>"
  htmlStr += "<option value='NA'>----------</option>"
  for result in cursor:
	htmlStr += "<option value='"+str(result['category'])+"'>"+str(result['category'])+"</option>"
  htmlStr += "</select> </div>"
  
  cmd = 'SELECT * FROM ingredient'
  cursor = g.conn.execute(text(cmd))
  cache = [{'ing_id': row['ing_id'], 'name': row['name']} for row in cursor]
  htmlStr += "<div class='special'> Ingredients: " 
  
  htmlStr += "<select name='ing1'>"
  htmlStr += "<option value='NA'>----------</option>"
  for result in cache:
	htmlStr += "<option value='"+str(result['ing_id'])+"'>"+str(result['name'])+"</option>"
  htmlStr += "</select>"
  
  htmlStr += "<select name='ing2'>"
  htmlStr += "<option value='NA'>----------</option>"
  for result in cache:
	htmlStr += "<option value='"+str(result['ing_id'])+"'>"+str(result['name'])+"</option>"
  htmlStr += "</select>"
  
  htmlStr += "<select name='ing3'>"
  htmlStr += "<option value='NA'>----------</option>"
  for result in cache:
	htmlStr += "<option value='"+str(result['ing_id'])+"'>"+str(result['name'])+"</option>"
  htmlStr += "</select>"
  
  htmlStr += "</div>"
  
  cmd = 'SELECT * FROM tags'
  cursor = g.conn.execute(text(cmd))
  cache = [{'name': row['name']} for row in cursor]
  htmlStr += "<div class='special'> Tags: " 
  
  htmlStr += "<select name='tag1'>"
  htmlStr += "<option value='NA'>----------</option>"
  for result in cache:
	htmlStr += "<option value='"+str(result['name'])+"'>"+str(result['name'])+"</option>"
  htmlStr += "</select>"
  
  htmlStr += "<select name='tag2'>"
  htmlStr += "<option value='NA'>----------</option>"
  for result in cache:
	htmlStr += "<option value='"+str(result['name'])+"'>"+str(result['name'])+"</option>"
  htmlStr += "</select>"
  
  htmlStr += "<select name='tag3'>"
  htmlStr += "<option value='NA'>----------</option>"
  for result in cache:
	htmlStr += "<option value='"+str(result['name'])+"'>"+str(result['name'])+"</option>"
  htmlStr += "</select>"
  
  htmlStr += "</div>"
  
  htmlStr += "<div class='special'><button type='submit' name='submit' value='submit' style='background-color:inherit; border:0; cursor:pointer;' > \
				<img src='/static/img/search.png' width='"+str(size)+"' height='"+str(size)+"' /> \
			  </button></div>"
  
  htmlStr += "</form>"
		
  if request.method == 'POST':
	  print "Entered POST"
	  cmd = 'SELECT distinct rec.rid as rid, rec.name as rname FROM includes_ingredient as inc, recipe_create as rec, has_tag as htg WHERE '
	  cmd+= 'inc.rid=rec.rid and htg.rid=rec.rid '
	  #print cmd
	  
	  print request.form['cuisine']
	  if request.form['cuisine'] != 'NA':
		cmd+= "and rec.cuisine='"+str(request.form['cuisine'])+"' "
	  if request.form['category'] != 'NA':
		cmd+= "and rec.category='"+str(request.form['category'])+"' "
		
	  cmd+="and (1=0 "
	  ing_empty = 1
	  if request.form['ing1'] != 'NA':
		ing_empty=0
		cmd+= 'or inc.ing_id='+str(request.form['ing1'])+' '
	  if request.form['ing2'] != 'NA':
		ing_empty=0
		cmd+= 'or inc.ing_id='+str(request.form['ing2'])+' '
	  if request.form['ing3'] != 'NA':
		ing_empty=0
		cmd+= 'or inc.ing_id='+str(request.form['ing3'])+' '
	  if ing_empty==1:
		cmd+="or 1=1 "
		
	  cmd+=") "
	  cmd+="and (1=0 "
	  tag_empty = 1
	  if request.form['tag1'] != 'NA':
		tag_empty=0
		cmd+= "or htg.name='"+str(request.form['tag1'])+"' "
	  if request.form['tag2'] != 'NA':
		tag_empty=0
		cmd+= "or htg.name='"+str(request.form['tag2'])+"' "
	  if request.form['tag3'] != 'NA':
		tag_empty=0
		cmd+= "or htg.name='"+str(request.form['tag3'])+"' "
	  if tag_empty==1:
		cmd+="or 1=1 "

	  cmd+=") "
	  print cmd
	  cursor = g.conn.execute(text(cmd))
	  for result in cursor:
		htmlStr += "<div class='eList'><a href='/show_recipe?rid="+str(result['rid'])+"'>"+str(result['rname'])+"</a></div>"
		
	  cursor.close()
	  print "Exiting POST"
	  return render_template("search.html", htmlStr=htmlStr)
  print "Didn't enter GET, now exiting"
  return render_template("search.html", htmlStr=htmlStr)
  
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
  print "Entered Dashboard"
  htmlStr = ""
  if request.method == 'GET': #change to post after session implementation
	print "Entered GET"
	uid = 3 #get from session
	
	cmd = 'SELECT * FROM recipe_create WHERE uid=(:input_uid)'
	cursor = g.conn.execute(text(cmd), input_uid = uid)
	htmlStr += "<div class='special'> My Recipes: </div>"
	for result in cursor:
		htmlStr += "<div class='eList'>"+str(result['name'])+"</div>"
		
	cmd = 'SELECT rec.name as name FROM favourites_recipe as fav, recipe_create as rec WHERE fav.rid = rec.rid and fav.uid = (:input_uid)'
	cursor = g.conn.execute(text(cmd), input_uid = uid)
	htmlStr += "<div class='special'> Favorites: </div>"
	for result in cursor:
		htmlStr += "<div class='eList'>"+str(result['name'])+"</div>"
		
	cmd = 'SELECT rec.name as name, rate.rating as ratings FROM rates_recipe as rate, recipe_create as rec WHERE rate.rid = rec.rid and rate.uid =  (:input_uid)'
	cursor = g.conn.execute(text(cmd), input_uid = uid)
	htmlStr += "<div class='special'> My Ratings: </div>"
	for result in cursor:
		htmlStr += "<div class='eList'>"+"You rated "+str(result['name'])+" "+str(result['ratings'])+"/5"+"</div>"
		
	cmd = 'SELECT rcc.name as name FROM recommended_recipe as rcm, recipe_create as rcc WHERE rcm.rid = rcc.rid and rcm.uid =  (:input_uid)'
	cursor = g.conn.execute(text(cmd), input_uid = uid)
	htmlStr += "<div class='special'> Recommended Recipes for you: </div>"
	for result in cursor:
		htmlStr += "<div class='eList'>"+str(result['name'])+"</div>"
	
	cursor.close()
	
  print "Exiting Dashboard"
  return render_template("dashboard.html", htmlStr=htmlStr)

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
	cursor4 = g.conn.execute(text(cmd4), input_rid = rid)
	#recipe title
	htmlStr += "<div class='special'>Recipe:</div>"
	for result in cursor:
		htmlStr += "<div class='eList'>"+str(result['name'])+" ("+str(result['cuisine'])+", "+str(result['category'])+")</div>"
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


@app.route('/addrecipe', methods=['POST'])
def addrecipe():
  cmd1 = 'SELECT rid FROM recipe_create WHERE rid = (SELECT MAX(rid) from recipe_create)'
  cursor = g.conn.execute(text(cmd1))
  rid = 0
  for result in cursor:
    rid = int(result['rid'])+1 
  uid = 1 #get from session later
  rname = request.form['name']
  rcuis = request.form['cuisine']
  rcat = request.form['category']
  rinst = request.form['instructions']
  print name
  cmd = 'INSERT INTO recipe_create VALUES ((:rid1), (:uid1), (:cuisine), (:category), (:instr))'
  g.conn.execute(text(cmd), rid1 = rid, uid1 = uid, cuisine = rcuis, category = rcat, instr = rinst)
  return render_template("addingredients.html", rid=rid)


@app.route('/addingredients', methods=['POST'])
def addingredients():
  rid = request.form['rid']
  cmd2 = 'SELECT ing_id FROM ingredient WHERE ing_id = (SELECT MAX(ing_id) from ingredient)'
  cursor = g.conn.execute(text(cmd2))
  ing_id = 0
  for result in cursor:
    ing_id = int(result['ing_id'])+1 
  quant = request.form['quantity']
  units = request.form['units']
  name = request.form['name']
  category = request.form['ing_cat']
  cmd = 'INSERT INTO ingredient VALUES ((:rid1), (:name1), (:cat))'
  cmd1 = 'INSERT INTO includes_ingredient VALUES ((:iid), (:rid1), (:quant1), (:units1))'
  g.conn.execute(text(cmd), rid1 = rid, name1 = name, cat = category)
  g.conn.execute(text(cmd1), iid = ing_id, rid1 = rid, quant1 = quant, units1 = units)
  return render_template("addingredients.html", rid=rid)

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
