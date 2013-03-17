#!/usr/bin/env python
from __future__ import with_statement

import os.path as op
import os
import sys

import traceback
import tools
import bottle
import frcode
import posixpath as pp
import requests
import time
import threading
import tempfile
import logging
import io
import config as cfg
import re

try:
    from urllib.parse import unquote_plus,quote_plus
except ImportError:
    from urllib import unquote_plus,quote_plus

"""

#Required fields  -- imported from config

SHARED_DIRS = dict(Dir1-Nick-Name=Dir1-Path,Dir2-Nick-Name=Dir2-Path)

USERNAME = 'username'  

PASSWORD = 'password'

UPDATE_PATH = 'http://www.cmi.ac.in:8000/update' #The path to post the update request to

PUBLIC_ROOT='./LOCAL' #The location to find the html,css,js files in

SIZE_THRESHOLD=10240    #Do not sync any file of size less than SIZE_THRESHOLD

SYNC_DELTA=30   #The interval in seconds between subsequents Syncs

PORT=9000     #The port on which the local server will run on

SHARE_HIDDEN = False # SYNC the hidden files or folders

"""
def allow(real_path):
    """Takes a physical_path and checks if it should be visible"""
    dirs = tools.seperate(real_path,os.sep)
    return cfg.SHARE_HIDDEN or all(map(lambda x:not x.startswith("."),
                                            tools.seperate(real_path,os.sep)))
    
# A helper function to do the server work
def process_logical_path(path):
    """Take the logical path for the shared dirs in :path,
    Handle appropriate errors if the path does not represent anything,
    Return None if the path points to the shared root else the real path 
    pointed to by the path"""
    
    dirs=tools.seperate(pp.normpath(path),sep="/")
    
    if dirs == []: # That means it is "/"
        return None
    
    #Check if it contains any hidden folder or file
    
    if dirs[0] not in cfg.SHARED_DIRS:
        bottle.abort(404,"No such Directory "+dirs[0])
    
    path = op.join(cfg.SHARED_DIRS[dirs[0]],*dirs[1:])
    
    if dirs[1:] and not allow(op.join(*dirs[1:])) :
        bottle.abort(404,"No such File or Directory "+dirs[0])

    if not op.normpath(path).startswith(cfg.SHARED_DIRS[dirs[0]]):
        bottle.abort(403,"Access Denied")
    
    if not os.access( path, os.R_OK ):
        bottle.abort( 403, "You do not have permission to list this path" )
    
    return path

def do_list_dir(real_path_to_dir):
    files,folders=[],[]
    for name in os.listdir(real_path_to_dir):
        if allow(name):
           if op.isdir(op.join(real_path_to_dir,name)):
                folders.append(name)
           else:
                files.append(name)
    return files,folders
                     
server = bottle.Bottle()

@server.route("/static/<filename:path>")
def serve_static(filename):
    return bottle.static_file(filename,root=cfg.PUBLIC_ROOT)

@server.route("/")
@bottle.view('index')
def index():
    raw = bottle.request.GET.get('path','/')
    logical_path = unquote_plus(raw)
    real_path = process_logical_path(logical_path)
    if real_path == None:
        return dict(root="/",owner=cfg.USERNAME)
    if op.isdir(real_path):
        return dict(root=logical_path,owner=cfg.USERNAME)             
    else:
        bottle.redirect("/download/"+raw)
        
@server.route('/download/<path:path>')
def download(path):
     path = unquote_plus(path)
     real_path=process_logical_path(path)
     
     if real_path:
        if op.isdir(real_path):
            
            r=['<html><body>']
            files,folders = do_list_dir(real_path)
            
            for f in folders:
                r.append('<a href="/download/%s">%s/</a>'%
                            (pp.join(path,f), f )
                         )   
            for f in files:
                r.append('<a href="/download/%s">%s</a>'%
                            ( pp.join(path,f), f )
                         )
            
            return "<br>".join(r)
        
        else:
            dirs = tools.seperate(path,"/")
                
            return bottle.static_file(
                                    op.join(*dirs[1:]),
                                    root=cfg.SHARED_DIRS[dirs[0]],
                                    download=True )
     
     bottle.abort(404,"No Such File")
         
@server.route('/listdir',method="POST")
def list_dir():
    logical_path = unquote_plus(bottle.request.POST['path'])
    if not logical_path: logical_path = "/"
    
    real_path = process_logical_path(logical_path)
    r=['<ul class="jqueryFileTree" style="display: none;">']
   
    if real_path == None:
        for f in cfg.SHARED_DIRS:
            ff = pp.join(logical_path,f)
            r.append('<li class="directory collapsed"><a href="/download/%s"\
                 rel="%s/">%s</a></li>'%(ff.lstrip("/"),ff,f))    
    else:
        files,folders = do_list_dir(real_path)
        
        for f in folders:
            ff=pp.join(logical_path,f)
            r.append('<li class="directory collapsed">\
                       <a href="/download/%s" rel="%s/">%s</a></li>'
                                %(ff.lstrip('/'),ff,f))    

        for f in files:
            ff=pp.join(logical_path,f)
            s = tools.humanize_bytes(op.getsize(op.join(real_path,f)))
            e = op.splitext(f)[1][1:]
            r.append('<li class="file ext_%s"><a href="/download/%s" rel="%s" title="Size : %s">\
                        %s</a></li>'%(e,ff.lstrip('/'),ff,s,f))
                     
    r.append('</ul>')
    return '\n'.join(r)  
       

    
class Updater(threading.Thread):
    def __init__(self,  shared_dirs ,
                        refresh_delta,
                        username,
                        password,
                        address,
                        update_path,
                        threshold_size = 0,
                        logger = None,
                        last_sync_time = 0,
                        max_mem = 102400 ):
                       
        self.shared_dirs = shared_dirs
        self.delta = refresh_delta
        self.username = username
        self.password = password
        self.address = address
        self.update_path = update_path
        
        self.threshold_size = threshold_size
        self.logger = logger
        self.last_sync_time = last_sync_time     
        self.max_mem = max_mem
    
        threading.Thread.__init__(self)
        self.stop = threading.Event()
        
    def run(self):
                self.logger.info("Updater Starting ..")
                tmp1,tmp2=io.BytesIO(),io.BytesIO()
                prev = tmp1
                next = tmp2
                try:
                    while True:
                        if self.stop.isSet():
                            self.logger.info("Exiting as stop flag is set ..")
                            return
                    
                        next.truncate(0)
                        next.seek(0)
                    
                        frcode.compress(self.list_files(),next)
                    
                    
                        next.seek(0)
                        prev.seek(0)
                    
                        equal = True
                        while equal:
                            c=next.read(1024)
                            if not c:
                                break
                            equal = c == prev.read(1024)
                        
                        next.seek(0)
                        
                        self.logger.debug("Posting with"+(" out" if equal else "" +"data") )
                        try:    
                            if not equal:
                                do_post(self.update_path,
                                    self.username,
                                    self.password,
                                    self.address,
                                    next)
                                next,prev = prev,next                               
                        
                            else:
                                do_post(self.update_path,
                                    self.username,
                                    self.password,
                                    self.address)
                        except:
                                self.logger.warn("Error:%s"%sys.exc_info()[1])
                                self.logger.debug(traceback.print_exception(*sys.exc_info()))
                        self.stop.wait(self.delta)
                except:
                    self.logger.exception("Unaccounted error occured, exiting..")
                        
    def shutdown(self):
            self.logger.info("Updater shutdown called")
            self.stop.set()
                
    def list_files(self):
            for d in sorted(self.shared_dirs):
                prefix = pp.join("/",d)
                
                l = len(self.shared_dirs[d].rstrip(r'\/'))
                
                for dirpath,dirs,files in os.walk(self.shared_dirs[d]):
                
                    if not cfg.SHARE_HIDDEN:
                        files = [f for f in files if not f[0] == '.']
                        dirs[:] = [d for d in dirs if not d[0] == '.']
                    
                    dirs.sort(key=str.lower)
                                
                    dir_prefix=pp.join(prefix,
                            *tools.seperate(dirpath[l:],os.sep))
                    
                    if os.access(dirpath,os.R_OK): 
                        yield (dir_prefix.rstrip('\/')+"/")
                    
                    for f in files:
                            f_path = op.join(dirpath,f)
                            try:
                                if ( op.getsize(f_path) > self.threshold_size and
                                os.access(f_path,os.R_OK) ):
                                    yield  pp.join(dir_prefix,f)
                            except OSError:
                                self.logger.exception("Error occured while reading"+f_path)
                                                             
def do_post(url,username,password,address,dataFile=None):
        r = requests.post(url,
                    data=dict(username=username,password=password,address=address),
                    files=dict( data=dataFile ) if dataFile else None)
        r.raise_for_status()

def main(logger):
        
        if cfg.PORT == 0:
            cfg.PORT = tools.pick_unused_port()
            
        MY_ADDR = "http://%s:%s"%(tools.get_ip_address(),cfg.PORT)
        
        t=Updater(cfg.SHARED_DIRS,
              cfg.SYNC_DELTA,
              cfg.USERNAME,
              cfg.PASSWORD,
              MY_ADDR,
              cfg.UPDATE_PATH,
              cfg.SIZE_THRESHOLD,
              logger=logger)
    
        t.setDaemon(1)
        t.start()
        
        bottle.TEMPLATE_PATH=[cfg.PUBLIC_ROOT]
        bottle._stderr = lambda x:logger.warn(x)
        bottle._stdout = lambda x:logger.info(x)
        bottle.run(server,host='0.0.0.0',
                   server=bottle.CherryPyServer,
                   port=cfg.PORT)
        t.shutdown()
        t.join()
if __name__ == '__main__':
        logging.basicConfig(level=logging.INFO)
        main(logging.root)
