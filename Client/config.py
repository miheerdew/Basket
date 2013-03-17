#!/usr/bin/env python
import shelve
import os
import os.path as op
import atexit

base_dir = op.dirname(op.abspath(__file__))
config_file = op.join(base_dir,"configdb")

def set_entity(db,keys,hidden = False):
    askbox = eg.multpasswordbox if hidden else eg.multenterbox 
    title = "Configuration Edit"
    defaults = []
    for k in keys:
        K = k.upper()
        defaults.append(str(db[K]) if K in db else '')
    msg = "Enter the following details"
    fieldVals = defaults    
    while True:
        fieldVals=askbox(msg,title=title,
                         fields=list(map(lambda x:x.replace('_',' '),keys)),
                         values=fieldVals)
        msg = ''
        if fieldVals is None:
            return False
        for i in fieldVals:
            if i.strip() == "":
                msg += "'%s' is a required field\n\n" % i   
        if msg == "":
            break
    for i in range(len(keys)):
            db[keys[i].upper()] = fieldVals[i]
    return True

def get_dir(default=None):
    while True:
        dir = eg.diropenbox("Select a new directory",default)
        if dir is None:
            return False
        dir = dir.strip()
        if dir:
            while True:
                name=eg.enterbox('Give a name to the shared directory: %s'%dir,
                        '',op.basename(dir.rstrip(r'\/')) )
                if name == "":
                    continue
                break
            
            if name is None:
                continue
            return (name,dir)       
                
                                    
def set_shared_dirs(db):
    msg="""Welcome, In this window you will Add/Edit the folders to Share.
The folders you have already shared are shown below
     
To add a new directory to the shared list
    *select "__Add Directory__" 
    *click on "OK"

To remove a already shared from the shared list 
    *select the Shared Directory
    **click on "OK"

When you are done making changes click on "Done"
    """
    shared = {}
    add_new = "__Add Directory__"
    title = "Shared Directories"
    if 'SHARED_DIRS' in db:
         shared = db['SHARED_DIRS']
    while True:
         choice=eg.choicebox(msg,title,choices=list(shared.keys())+[add_new],okButton="OK",cancelButton="DONE")                                            
         if choice is None:
            break
         
         if choice == add_new:
            res = get_dir()
            if not res:
                continue
            shared[res[0]] = res[1]
         else:
            del shared[choice]
    db['SHARED_DIRS'] = shared        
                                    
def set_config(db):
    set_entity(db,["Username","Password"],True)
    set_shared_dirs(db)
    if eg.ynbox("Do You want to change some advance settings?"):
        set_entity(db,["Update_Path",
                   "Public_Root",
                   "Size_threshold",
                   "Sync_Delta",
                   "Port",
                   "Share_Hidden"])     

NAMES="""\
USERNAME
PASSWORD
SHARED_DIRS
UPDATE_PATH
PUBLIC_ROOT
SIZE_THRESHOLD i
SYNC_DELTA i 
SHARE_HIDDEN b
PORT i"""

if __name__ == '__main__':
    import sys
    base_dir = op.dirname(op.abspath(__file__))
    sys.path.insert(0,base_dir) 

    import easygui as eg
    configdb = shelve.open(config_file,'c')
    try:
        set_config(configdb)
    except:
        eg.exceptionbox()
    finally:
        configdb.close()
else:
    db = shelve.open(config_file,'r')
    for line in NAMES.splitlines():
          res = line.strip().split(" ")
          res =[ r.strip() for r in res if r.strip() != "" ]  
          if len(res) == 2:
            name,type_ = res
          else:
            name = line.strip()
            type_ = None
     
          if name not in db:
            raise Exception("The config file is incomplete,\n\
                           '%s' key is not found.\n\
                           Run config.py to setup the config file"%name)
            exit()
          if type_ is None:  
            globals()[name]=db[name]
          elif type_ == "i":
            globals()[name]=int(db[name])
          elif type_ == "b":
            globals()[name] = db[name].upper() == "TRUE"
    db.close()        
    PUBLIC_ROOT = op.join(base_dir,PUBLIC_ROOT) # If public root is relative resolve it wrt base
            
