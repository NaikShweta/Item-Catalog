from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from database_setup_project import Base, Catalog, Items, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# anti forgery token
from flask import session as login_session
import random
import string
import os

# Imports for GConnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create a state login token to prevent request forgery.
# store it in the session for later validation
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    # render login template
    return render_template("login.html", STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
     # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
     # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']    

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions




# DISCONNECT - Revoke a current user's token and reset their login_session

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('catalog'))
        #return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view catalog
@app.route('/catalog/JSON/')
def catalogJSON():
    catalogs = session.query(Catalog).all()
    return jsonify(catalogs = [catalog.serialize for catalog in catalogs])

# JSON APIs to view items in catalog
@app.route('/catalog/<int:catalog_id>/items/JSON/')
def itemsJSON(catalog_id):
    items = session.query(Items).filter_by(catalog_id=catalog_id).all()
    return jsonify(items = [item.serialize for item in items])


# display entire catalog
@app.route('/')
@app.route('/catalog/')
def catalog():
    catalogs = session.query(Catalog).all()
    if 'username' not in login_session:
        return render_template("publicCatalog.html", catalogs = catalogs)
    else:
        return render_template("catalog.html", catalogs = catalogs)



# Create New Entry in Catalog
@app.route('/')
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method=='POST':
        newCatalog = Catalog(name = request.form['name'])
        session.add(newCatalog)
        session.commit()
        return redirect(url_for('catalog'))
    else:
        return render_template("newCatalog.html")

# Edit Catalog Entry
@app.route('/catalog/<int:catalog_id>/edit/', methods=['GET', 'POST'])
def editCatalog(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedCatalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if request.method=='POST':
        if request.form['name']:
            editedCatalog.name = request.form['name']
            session.add(editedCatalog)
            session.commit()
            return redirect(url_for('catalog'))
    else:
        return render_template("editCatalog.html", catalog=editedCatalog)
                            
# Delete Catalog Entry
@app.route('/catalog/<int:catalog_id>/delete/', methods=['GET', 'POST'])
def deleteCatalog(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletedCatalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if request.method=='POST':
        session.delete(deletedCatalog)
        session.commit()
        return redirect(url_for('catalog'))
    else:
        return render_template("deleteCatalog.html", catalog=deletedCatalog)                   

# display all items
@app.route('/catalog/<int:catalog_id>/items/')
def showItems(catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    items = session.query(Items).filter_by(catalog_id = catalog_id).all()
    if 'username' not in login_session:
        return render_template("publicItems.html", catalog = catalog, items=items)
    else:
        return render_template("items.html", catalog = catalog, items = items)

# create new item
@app.route('/catalog/<int:catalog_id>/items/new/', methods=['GET', 'POST'])
def newItems(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if request.method=='POST':
        newItem = Items(name = request.form['name'], description = request.form['description'], catalog_id=catalog_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItems', catalog_id = catalog_id))
    else:
        return render_template("newItems.html", catalog=catalog)

# Edit items
@app.route('/catalog/<int:catalog_id>/items/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItems(catalog_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Items).filter_by(id=item_id).one()
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if request.method=='POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showItems', catalog_id=catalog_id))
    else:
        return render_template("editItems.html", item=editedItem, catalog=catalog)

# Delete Items
@app.route('/catalog/<int:catalog_id>/items/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItems(catalog_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletedItem = session.query(Items).filter_by(id=item_id).one()
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if request.method=='POST':
        session.delete(deletedItem)
        session.commit()
        return redirect(url_for('showItems', catalog_id=catalog_id))
    else:
        return render_template("deleteItems.html", item=deletedItem, catalog=catalog)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
