from flask import Flask
from flask import render_template, redirect, url_for, request, abort

from random import sample
from pymongo import Connection

import os
import string

dbhost = os.environ['OPENSHIFT_NOSQL_DB_HOST']
dbport = os.environ['OPENSHIFT_NOSQL_DB_PORT']
dbuser = os.environ['OPENSHIFT_NOSQL_DB_USERNAME']
dbpass = os.environ['OPENSHIFT_NOSQL_DB_PASSWORD']

app = Flask(__name__)
title = "My Shopping List"

@app.route('/')
def index():
 return render_template('index.html', title=title, listid='Welcome')

@app.route('/create')
def create():
 mongo = Connection(dbhost, dbport)
 db = mongo.msl
 db.auth(dbuser, dbpass)
 lists = db.lists
 list = {}
 listid = "".join(sample(string.lowercase + string.digits, 6))
 list["listid"] = listid
 mongo.end_request()
 return redirect('/view/' + listid)

@app.route('/delete/<listid>')
def delete(listid):
 mongo = Connection(dbhost, dbport)
 db = mongo.msl
 db.auth(dbuser, dbpass)
 lists = db.lists
 lists.remove({"listid": listid})
 return redirect('/')

@app.route('/open', methods=['POST', 'GET'])
def open():
 if request.method == 'POST':
  listid = request.form['listid']
  db = mongo.msl
  lists = db.lists
  if lists.find({"listid": listid}).count() > 0:
   return redirect('/view/' + listid)
  else:
   abort(404)
 return render_template('open.html', title=title, listid='Open')

@app.route('/view/<listid>', methods=['POST', 'GET'])
def view(listid):
 if request.method == 'POST':
  listitem = request.form['listitem']
  add_to_list(listid, listitem)
 mongo = Connection(dbhost, dbport)
 db = mongo.msl
 db.auth(dbuser, dbpass)
 lists = db.lists
 entry = lists.find_one({"listid": listid})
 mongo.end_request()
 entries = entry['text'] if entry else ''
 return render_template('list.html', title=title, listid=listid, entries=entries)

@app.route('/clean/<listid>', methods=['POST'])
def clean(listid):
 if request.method == 'POST':
  remove_from_list(listid, request.form.keys())
 return redirect('/view/' + listid)

@app.errorhandler(404)
def page_not_found(error):
 return render_template('404.html', title=title, listid='Error'), 404

def add_to_list(listid, listitem):
 mongo = Connection(dbhost, dbport)
 db = mongo.msl
 db.auth(dbusr, dbpass)
 lists = db.lists
 lists.update({"listid":listid}, {"$push": {"text":listitem}}, upsert=True) 
 mongo.end_request()

def remove_from_list(listid, listitems):
 mongo = Connection(dhost, dbport)
 db = mongo.msl
 db.aut(dbuser, dbpass)
 lists = db.lists
 lists.update({"listid":listid}, {"$pullAll": {"text":listitems}}) 
 mongo.end_request()

if __name__ == '__main__':
 app.run(debug = True, host = '0.0.0.0')
