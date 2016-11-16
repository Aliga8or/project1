#!/usr/bin/env python2.7

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, session, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = "hakuna_matata"

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


@app.route('/', methods = ['GET', 'POST'])
def index():
	htmlStr = "<form name='loginForm' action='/' method='POST'>"
	htmlStr += "<div class='eList'>Username: <input type='text' name='username'></div>"
	htmlStr += "<div class='eList'>Password: <input type='text' name='password'></div>"
	htmlStr += "<div class='special'><button type='submit' name='submit' value='submit' style='background-color:inherit; border:0; cursor:pointer;' > \
				<img src='/static/img/search.png' width='"+str(size)+"' height='"+str(size)+"' /> \
			  </button></div>"
	htmlStr += "</form>"
			  
	if request.method == 'POST':
		uname = request.form['username']
		pwd = request.form['password']

		cmd = 'SELECT * FROM users WHERE username=(:username)'
		cursor = g.conn.execute(text(cmd), username=uname)
		result = cursor.fetchone()
		if cursor.rowcount == 0:
			htmlStr+="<div class='errList'>User not registered !!!</div>"
		elif result['password'] != pwd:
			htmlStr+="<div class='errList'>Password is incorrect !!!</div>"
		else:
			session['uid'] = result['uid']
			session['name'] = result['name']
			session['username'] = uname
			return redirect('/dashboard')

	return render_template('index.html', htmlStr=htmlStr);
	
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
  if 'name' in session:
	name = session['name']
  else:
	return redirect('/')
  print "Logging out "+name
  session.pop('username', None)
  session.pop('name', None)
  session.pop('uid', None)
  return redirect('/')
  
@app.route('/addrestaurant', methods = ['GET', 'POST'])
def addrestaurant():
  print "Entered addrestaurant"
  if 'uid' in session:
	uid = session['uid']
	name = session['name']
  else:
	return redirect('/')
	
  htmlStr = "<div class='logBar'>Hi, "+name+" !!!</div>"
  
  htmlStr += "<form name='resForm' action='/addrestaurant' method='POST'>"
  htmlStr += "<div class='eList'>Restaurant Name: <input type='text' name='resname'></div>"
  htmlStr += "<div class='eList'>Restaurant Location: <input type='text' name='resloc'></div>"
  
  cmd = 'SELECT * FROM recipe_create'
  cursor = g.conn.execute(text(cmd))
  htmlStr += "<div class='eList'> Dish prepared: <select name='rec_id'>"
  htmlStr += "<option value='NA'>----------</option>"
  for result in cursor:
	htmlStr += "<option value='"+str(result['rid'])+"'>"+str(result['name'])+"</option>"
  htmlStr += "</select> </div>"
  
  htmlStr += "<div class='special'><button type='submit' name='submit' value='submit' style='background-color:inherit; border:0; cursor:pointer;' > \
				<img src='/static/img/search.png' width='"+str(size)+"' height='"+str(size)+"' /> \
			  </button></div>"
  
  htmlStr += "</form>"
  
  if request.method == 'POST':
	print "Enter POST"
	if request.form['resname'] != "":
		print "Restaurant name: "+request.form['resname']
		cmd = 'SELECT MAX(res_id) as max_id from restaurant_add'
		cursor = g.conn.execute(text(cmd))
		result = cursor.fetchone()
		res_id = int(result['max_id']) + 1
		
		cmd = 'INSERT INTO restaurant_add VALUES ((:id), (:userid), (:name), (:loc))'
		cursor = g.conn.execute(text(cmd), id = res_id, userid = int(uid), name = request.form['resname'], loc = request.form['resloc'])
		
		if request.form['rec_id'] != 'NA':
			cmd = 'INSERT INTO prepares_recipe VALUES ((:rec_id), (:restaurant_id))'
			cursor = g.conn.execute(text(cmd), rec_id = int(request.form['rec_id']), restaurant_id = res_id)
		htmlStr+="<div class='special'>Restaurant added successfully</div>"
	else:
		htmlStr+="<div class='errList'>Restaurant name is empty</div>"
		
  return render_template("restaurant.html", htmlStr=htmlStr)

@app.route('/search', methods=['GET', 'POST'])
def search_recipe():
  print "Entered recipe"
  if 'uid' in session:
	uid = session['uid']
	name = session['name']
  else:
	return redirect('/')
	
  htmlStr = "<div class='logBar'>Hi, "+name+" !!!</div>"
  
  htmlStr += "<form name='searchForm' action='/search' method='POST'>"
  
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
		htmlStr += "<div class='eList'><a href='/show_recipe?rid="+str(result['rid'])+"'>"+result['rname'].encode('utf-8')+"</a></div>"
		
	  cursor.close()
	  print "Exiting POST"
	  return render_template("search.html", htmlStr=htmlStr)
  print "Didn't enter GET, now exiting"
  return render_template("search.html", htmlStr=htmlStr)
  
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
  print "Entered Dashboard"
  if 'uid' in session:
	uid = session['uid']
	name = session['name']
  else:
	return redirect('/')
	
  htmlStr = "<div class='logBar'>Hi, "+name+" !!!</div>"
  
  if request.method == 'GET': #change to post after session implementation
	print "Entered GET"
	#uid = 3 #get from session
	
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
	
	htmlStr += "<div class='special'>Top 3 Contributors:</div>"
	cmd = 'SELECT u.name, COUNT(r.rid) as Recipes_Posted FROM users as u, recipe_create as r WHERE u.uid=r.uid GROUP BY u.name ORDER BY Recipes_Posted DESC LIMIT 3'
	cursor = g.conn.execute(text(cmd))
	for result in cursor:
		htmlStr += "<div class='eList'>"+str(result['name'])+"</div>"
	htmlStr += "<div class='special'>3 Top Rated Recipes:</div>"
	cmd = 'SELECT r.name as recipe, SUM(CAST(x.rating as float))/COUNT(CAST(x.rating as float)) as score FROM recipe_create as r, rates_recipe as x WHERE r.rid=x.rid GROUP BY r.name ORDER BY score DESC LIMIT 3'
	cursor = g.conn.execute(text(cmd))
	for result in cursor:
		htmlStr += "<div class='eList'>"+str(result['recipe'])+"</div>"

	cursor.close()
	
  print "Exiting Dashboard"
  return render_template("dashboard.html", htmlStr=htmlStr)

@app.route('/show_recipe', methods=['GET'])
def show_recipe():
  print "Entered show recipe"
  if 'uid' in session:
	uid = session['uid']
	name = session['name']
  else:
	return redirect('/')
	
  htmlStr = "<div class='logBar'>Hi, "+name+" !!!</div>"
  
  if request.method == 'GET': 
	print "Entered GET"
	rid = int(request.args.get('rid'))
	print "rid:"+str(rid)
	
	cmd = 'SELECT * FROM recipe_create WHERE rid=(:input_rid)'
	cmd1 = 'SELECT ing.name, inc.quantity, inc.units FROM ingredient as ing, includes_ingredient as inc WHERE inc.rid=(:input_rid) AND inc.ing_id=ing.ing_id'
	cmd2 = 'SELECT * FROM has_tag WHERE has_tag.rid = (:input_rid)'
	cmd3 = 'SELECT u.name, c.content, c.post_time FROM comment_make as c, users as u WHERE c.rid=(:input_rid) AND c.uid = u.uid'
	cmd4 = 'SELECT r.name, r.rid FROM recipe_create as r, similar_recipes as s WHERE s.rid1 = (:input_rid) AND s.rid2=r.rid'

	cursor = g.conn.execute(text(cmd), input_rid = rid)
	cursor1 = g.conn.execute(text(cmd1), input_rid = rid)
	cursor2 = g.conn.execute(text(cmd2), input_rid = rid)
	cursor3 = g.conn.execute(text(cmd3), input_rid = rid)
	cursor4 = g.conn.execute(text(cmd4), input_rid = rid)
	cache = [{'name': row['name'], 'cuisine': row['cuisine'], 'category': row['category'], 'instructions': row['instructions']} for row in cursor]

	#recipe title
	htmlStr += "<div class='special'>Recipe:</div>"
	for result in cache:
		#print str(result['name'])
		htmlStr += "<div class='eList'>"+str(result['name'])+" ("+str(result['cuisine'])+", "+str(result['category'])+")</div>"
	#ingredients
	htmlStr += "<div class='special'>Ingredients:</div>"
	for result in cursor1:
		htmlStr += "<div class='eList'>"+str(result['quantity'])+" "+str(result['units'])+" "+str(result['name'])+"</div>"
	#instructions
	htmlStr += "<div class='special'>Instructions:</div>"
	for result in cache:

		htmlStr += "<div class='eList'>"+result['instructions'].encode('utf-8')+"</div>"
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
		htmlStr += "<div class='eList'><a href='/show_recipe?rid="+str(result['rid'])+"'>"+str(result['name'])+"</a></div>"

  cursor.close()
  cursor1.close()
  cursor2.close()
  cursor3.close()
  cursor4.close()
  print "Exiting show recipe"
  return render_template("show_recipe.html", htmlStr=htmlStr)


@app.route('/addrecipe', methods=['GET', 'POST'])
def addrecipe():
  if 'uid' in session:
	uid = session['uid']
	name = session['name']
  else:
	return redirect('/')
	
  #htmlStr = "<div class='logBar'>Hi, "+name+" !!!</div>"
  error=""
  if request.method == 'POST':
	  if request.form['rec_name'] != "":
	  	cmd1 = 'SELECT rid FROM recipe_create WHERE rid = (SELECT MAX(rid) from recipe_create)'
	  	cursor = g.conn.execute(text(cmd1))
	  	rid = 0
	  	for result in cursor:
			rid = int(result['rid'])+1 
		rname = request.form['rec_name']
		rcuis = request.form['cuisine']
		rcat = request.form['category']
		rinst = request.form['instructions']
		print name
		cmd = 'INSERT INTO recipe_create VALUES ((:rid1), (:uid1), (:rec_name), (:cuisine), (:category), (:instr))'
	  	g.conn.execute(text(cmd), rid1 = rid, uid1 = uid, rec_name = rname, cuisine = rcuis, category = rcat, instr = rinst)
	  	cursor.close()
	  	return redirect('/addingredients?rid='+str(rid))
	  else:
	  	error = "You cannot add a recipe with no title"
	  	return render_template('create_recipe.html', name=name, error=error)
  return render_template('create_recipe.html', name=name)


@app.route('/addingredients', methods=['GET', 'POST'])
def addingredients():
  if 'uid' in session:
	uid = session['uid']
	name = session['name']
  else:
	return redirect('/')
	
  #htmlStr = "<div class='logBar'>Hi, "+name+" !!!</div>"
  
  htmlStr = ""

  rid = int(request.args.get('rid'))
  cmd = 'SELECT * FROM ingredient'
  cursor = g.conn.execute(text(cmd))
  cache = [{'ing_id': row['ing_id'], 'name': row['name']} for row in cursor]
  
  htmlStr += "Ingredient Name: " 
  
  htmlStr += "<select name='ing_id'>"
  htmlStr += "<option value='NA'>----------</option>"
  for result in cache:
	htmlStr += "<option value='"+str(result['ing_id'])+"'>"+str(result['name'])+"</option>"
  htmlStr += "</select> <br>"
  
  if request.method == 'POST':
  	rid = request.form['rid']
  	ing_id = request.form['ing_id']
  	quant = request.form['quantity']
  	units = request.form['units']
  	cmd1 = 'INSERT INTO includes_ingredient VALUES ((:iid), (:rid1), (:quant1), (:units1))'
  	g.conn.execute(text(cmd1), iid = ing_id, rid1 = rid, quant1 = quant, units1 = units)
  
  cursor.close()
  return render_template("addingredients.html", rid=rid, name=name, htmlStr = htmlStr)



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
