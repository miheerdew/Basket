#!/usr/bin/env python
import os
import sys
import os.path as op
import logging
import signal
import time
import atexit


def kill(pid):
    e = None
    while True:
        try:
            os.kill(pid,signal.SIGTERM)
        except:
            e = sys.exc_info()[1]
            break
        time.sleep(0.1)
    if e and tools.isAlive(pid):
        eg.msgbox("Unable to kill process ,reason : %s"%e.strerror)
        sys.exit()    

def main():
    global PIDFILE
    PIDFILE = op.join(base_dir,'PID')
    logging.basicConfig(filename=op.join(base_dir,'LOGFILE.txt'),
                        filemode = "w",
                        level=logging.DEBUG)
    try:
        pid = int(open(PIDFILE).read())
    except:
        pid = None
     
    if pid and tools.isAlive(pid):
        res=eg.buttonbox("Server is already running and its pid is %s.\n\
        What do you want to do ?"%pid,choices=("Stop","Restart","Nothing"))
        
        if res != "Nothing": 
            kill(pid)
        if res != "Restart":
            sys.exit()
    
    #Now we have to start the server
    @atexit.regester
    def delpid():
        os.remove(PIDFILE)
    try:
        with open(PIDFILE,'w') as fd:
            fd.write(str(os.getpid()))
        local_server.main()
    except:
        eg.exceptionbox(logging.root)        
        

if __name__ == '__main__':
    base_dir = op.dirname(op.abspath(__file__))
    sys.path.insert(0,(base_dir))

    import local_server
    import easygui as eg
    import tools

    main()          
