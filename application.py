from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from flask import session as login_session, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Cuisine, Item

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import random
import string

app = Flask(__name__)

engine = create_engine('sqlite:///worldcuisines.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "World Cuisines"


# *************************************
# Login Page
# *************************************
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# *************************************
# Google Sign In Connect method
# *************************************
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserId(login_session['email'])
    print ('current user id: %s' % user_id)
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = 'Login Success'
    print "done!"
    return output


# Google Sign out method
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s' % access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token='
    url += login_session['access_token']
    print url
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
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.',
                       400)
        )
        response.headers['Content-Type'] = 'application/json'
        return response


# *************************************
# Show All Cuisines
# Viewable by all - Does not require login
# *************************************
@app.route('/')
@app.route('/cuisines/')
def showCuisines():
    session = DBSession()
    cuisines = session.query(Cuisine).all()
    return render_template('index.html', cuisines=cuisines)


# *************************************
# Add a new cuisine to database
# *************************************
@app.route('/cuisines/new', methods=('GET', 'POST'))
def addNewCuisine():
    if 'username' not in login_session:
        return redirect('/login')
    session = DBSession()
    if request.method == 'POST':
        newCuisine = Cuisine(
            name=request.form['name'],
            description=request.form['description'],
            imageUrl=request.form['imageUrl'],
            created_by=getUserId(login_session['email'])
        )
        session.add(newCuisine)
        session.commit()
        flash('New Menu Item Created!')
        return redirect(url_for('showCuisines'))
    else:
        return render_template('newcuisine.html')


# *************************************
# View a cuisine & its items
# Viewable by all - Does not require login
# *************************************
@app.route('/cuisines/<string:cuisine_name>/')
def viewCuisine(cuisine_name):
    session = DBSession()
    try:
        cuisine = session.query(Cuisine).filter_by(name=cuisine_name).one()
        print cuisine.id
        items = session.query(Item).filter_by(cuisine_id=cuisine.id).all()
        print items
        return render_template('infoview.html', cuisine=cuisine, items=items)
    except Exception as e:
        print e
        return render_template('errorpage.html')


# *************************************
# View an item from a cuisine
# Viewable by all - Does not require login
# Editing Deleteing requires user to be creator
# *************************************
@app.route('/cuisines/<string:cuisine_name>/item/<int:item_id>/')
def viewItem(cuisine_name, item_id):
    session = DBSession()
    try:
        cuisine = session.query(Cuisine).filter_by(name=cuisine_name).one()
        item = session.query(Item).filter_by(id=item_id).one()
        created_by = session.query(User).filter_by(id=item.created_by).one()
        if 'username' not in login_session:
            return render_template(
                'iteminfoview.html',
                cuisine=cuisine,
                item=item,
                created_by=created_by
            )
        else:
            return render_template(
                'iteminfoview.html',
                cuisine=cuisine,
                item=item,
                creator=getUserId(login_session['email']),
                created_by=created_by
            )
    except Exception as e:
        print e
        return render_template('errorpage.html')


# *************************************
# Add Item to Cuisine
# *************************************
@app.route('/cuisines/<string:cuisine_name>/item/new', methods=['GET', 'POST'])
def addNewItem(cuisine_name):
    if 'username' not in login_session:
        return redirect('/login')
    session = DBSession()
    cuisine = session.query(Cuisine).filter_by(name=cuisine_name).one()
    if request.method == 'POST':
        newItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            imageUrl=request.form['imageUrl'],
            created_by=getUserId(login_session['email']),
            cuisine_id=cuisine.id
        )
        session.add(newItem)
        session.commit()
        flash('New Menu Item Created!')
        return redirect(url_for('showCuisines'))
    else:
        return render_template('newitem.html', cuisine_name=cuisine_name)


# *************************************
# Edit Item in Cuisine
# *************************************
@app.route('/cuisines/<string:cuisine_name>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(cuisine_name, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = DBSession()
    try:
        itemToEdit = session.query(Item).filter_by(id=item_id).one()

        if (getUserId(login_session['email']) != itemToEdit.created_by):
            print 'Unauthorized User'
            return redirect('/')

        if request.method == 'POST':
            if request.form['name']:
                itemToEdit.name = request.form['name']
            if request.form['description']:
                itemToEdit.description = request.form['description']
            if request.form['imageUrl']:
                itemToEdit.imageUrl = request.form['imageUrl']
            session.commit()
            return redirect(url_for('showCuisines'))
        else:
            return render_template('edititem.html', itemToEdit=itemToEdit)
    except Exception as e:
        print e
        return render_template('errorpage.html')


# *************************************
# Delete item from Cuisine
# *************************************
@app.route('/cuisines/<string:cuisine_name>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(cuisine_name, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    session = DBSession()
    try:
        itemToDelete = session.query(Item).filter_by(id=item_id).one()

        if (getUserId(login_session['email']) != itemToDelete.created_by):
            print 'Unauthorized User'
            return redirect('/')

        if request.method == 'POST':
            session.delete(itemToDelete)
            session.commit()
            return redirect(url_for('showCuisines'))
        else:
            return render_template(
                'deleteitem.html',
                itemToDelete=itemToDelete
            )
    except Exception:
        return render_template('errorpage.html')


# *************************************
# Get User Information
# *************************************
def getUserId(email):
    try:
        session = DBSession()
        user = session.query(User).filter_by(
            email=login_session['email']
        ).one()
        return user.id
    except Exception:
        return None


def getUserInfo(user_id):
    session = DBSession()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user


def createUser(login_session):
    session = DBSession()
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        profileImage=login_session['picture']
    )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# *************************************
# JSON APIs
# *************************************
@app.route('/cuisines/JSON')
def cuisinesJSON():
    session = DBSession()
    cuisines = session.query(Cuisine).all()
    return jsonify(result=[i.serialize for i in cuisines])


@app.route('/cuisines/<string:cuisine_name>/items/JSON')
def itemJSON(cuisine_name):
    session = DBSession()
    cuisine = session.query(Cuisine).filter_by(name=cuisine_name).one()
    items = session.query(Item).filter_by(cuisine_id=cuisine.id).all()
    return jsonify(result=[i.serialize for i in items])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
