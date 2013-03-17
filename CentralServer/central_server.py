from __future__ import with_statement
import os.path as op
import os
import sys

base = op.dirname(op.abspath(__file__))
sys.path.insert(0,base)

import six
from bottle import *
from config import *

import search
import hashlib
import posixpath as pp
import shelve
import time
import frcode
import re
import tools
import time
import json
    
from six import print_,b,iterkeys
import logging


def prioritized_users(user_info):
    """Return the keys in user_info in the descending order of their last times
    """
    return sorted(user_info.keys(),key = lambda x:user_info[x]['time'],reverse=True)
    
def hashed(word):
    h=hashlib.md5()
    h.update(b(word))
    return h.hexdigest()

@route('/update',method='POST')
def do_update():
    username = request.forms['username']
    password = request.forms['password']
    address = request.forms['address']
    fileList = request.files.data
    
    fileName = op.join(op.expanduser('~'+username),PASS_FILE)
    
    try:
        assert hashed(password) == open(fileName,'r').read(36).strip()
    except:
        abort(401,"Authentication Failed")
    
    if fileList and fileList.file:
        with open(op.join(DATA_DIR,username),'wb') as fd:
           frcode.compress(
                map(lambda x:username+" "+x,frcode.decompress(fileList.file)),
                fd )
           # fd.write(fileList.file.read())    
    
    USERS_DB[username] = dict( time = time.time(),
                               address = address )
    USERS_DB.sync()                           
    return "Accepted\n"          

@route('/search')
def do_search():
    query = request.query.query.lower()
    max_results = MAX_SEARCH_RESULTS
    skip = int(request.query.get('skip',0))
    paths = []
    for username in prioritized_users(USERS_DB):
        paths.append(op.join(DATA_DIR,username))
    
    res=[]    
    for line in search.find(query,paths,max_res = max_results + skip)[skip:]:
        username,_,path=line.partition(' ')
        res.append((username,path))
    
    return json.dumps({ 'success':bool(res), 'data':res },encoding='latin-1')
                   
@route('/users')
def get_user_infos():
    now = time.time()
    res=[]
    for u in prioritized_users(USERS_DB):
        delta = time.time() - USERS_DB[u]['time']
        status = 'ONLINE' if delta <= ONLINE_THRESHOLD else 'OFFLINE'
        delta = tools.humanize_time(USERS_DB[u]['time'])
        res.append({'name':u,'status':status,'delta':delta, 'address':USERS_DB[u]['address']})
    
    response.content_type = 'application/json'
    return json.dumps(res)

@route('/')
@route('/static/<filename>')
def serve_static(filename="index.html"):
        return static_file(filename,root=PUBLIC_ROOT)             

def main():
    global USERS_DB
    db=op.join(DATA_DIR,USERS_FILE)
    USERS_DB=shelve.open(db)
    try:
        debug(True)
        run( host = '0.0.0.0',
             port = 8000,
	         server=CherryPyServer,	
             debug = True )
    finally:
        USERS_DB.close()

if __name__ == '__main__':
    main()        
