import datetime
import socket
import os
import platform
import six
import subprocess
import time

WIN = platform.system() == "Windows"
if six.PY3: 
    bin2str = lambda x:x.decode()
        
else:
    bin2str=id

def get_ip_address(max_retry=5,sleep=5):
        for i in range(max_retry):
           try:
              return do_get_ip_address()
           except:
              pass
        raise Exception("Could not get ip address,Network Error")
     
def do_get_ip_address():
        """A hack to get the ipaddress of the computer 
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
                s.connect(("www.cmi.ac.in",80))
                return s.getsockname()[0]
        finally:
                s.close()

def humanize_bytes(bytes, precision=1):
    
    abbrevs = (
        (1<<50, 'PB'),
        (1<<40, 'TB'),
        (1<<30, 'GB'),
        (1<<20, 'MB'),
        (1<<10, 'kB'),
        (1, 'bytes')
    )
    if bytes == 1:
        return '1 byte'
    for factor, suffix in abbrevs:
        if bytes >= factor:
            break
    return '%.*f %s' % (precision, bytes / factor, suffix)

def ungettext(a,b,count):
    if count:
        return b
    return a

def ugettext(a):
    return a

def humanize_time(d, now=None):
    
    """
    Takes two datetime objects and returns the time between d and now
    as a nicely formatted string, e.g. "10 minutes".  If d occurs after now,
    then "0 minutes" is returned.

    Units used are years, months, weeks, days, hours, and minutes.
    Seconds and microseconds are ignored.  Up to two adjacent units will be
    displayed.  For example, "2 weeks, 3 days" and "1 year, 3 months" are
    possible outputs, but "2 weeks, 3 hours" and "1 year, 5 days" are not.

    Adapted from http://blog.natbat.co.uk/archive/2003/Jun/14/time_since
    """
    chunks = (
      (60 * 60 * 24 * 365, lambda n: ungettext('year', 'years', n)),
      (60 * 60 * 24 * 30, lambda n: ungettext('month', 'months', n)),
      (60 * 60 * 24 * 7, lambda n : ungettext('week', 'weeks', n)),
      (60 * 60 * 24, lambda n : ungettext('day', 'days', n)),
      (60 * 60, lambda n: ungettext('hour', 'hours', n)),
      (60, lambda n: ungettext('minute', 'minutes', n))
    )
    #If it is a timestamp convert it to datetime
    if isinstance(d,float):
        d=datetime.datetime.fromtimestamp(d)
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        if d.tzinfo:
            now = datetime.datetime.now(LocalTimezone(d))
        else:
            now = datetime.datetime.now()

    # ignore microsecond part of 'd' since we removed it from 'now'
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return '0 ' + ugettext('minutes')
    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break
    s = ugettext('%(number)d %(type)s') % {'number': count, 'type': name(count)}
    if i + 1 < len(chunks):
        # Now get the second item
        seconds2, name2 = chunks[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            s += ugettext(', %(number)d %(type)s') % {'number': count2, 'type': name2(count2)}
    return s

def pack(arg,sep=' '):
    """join the elements in arg with sep and convert to string"""
    return sep.join(map(str,arg))    

def r_unpack(buff,count,sep=' '):
    """Unpack count many items from the left seperated by :sep"""
    return buff.rsplit(sep,count-1)

def l_unpack(arg,count,sep=' '):
    return buff.lsplit(sep,count -1)
    
def seperate(string,sep=' '):
    res=[]
    word=''
    for s in string:
        if s==sep:
            if word:
                res.append(word)
            word = ''
        else:
            word += s
    if word: res.append(word)
    return res

def pick_unused_port(max_retry=7):
  while True:
     try:	
       s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       s.bind(('localhost', 0))
       addr, port = s.getsockname()
       s.close()
     except:
       if max_retry:
           max_retry = max_retry - 1
           time.sleep(10)
       else:
           raise Exception("Cannot connect to network")
     break 
  return port

########Code to check if pid is there in a cross platform way
# GetExitCodeProcess uses a special exit code to indicate that the process is
# still running.

if WIN: 
    def isAlive(pid):
        ps = subprocess.Popen(['tasklist','/NH','/FI',"PID eq %d" % pid], 
                              stdout=subprocess.PIPE)
        output = seperate(bin2str(ps.communicate()[0]),' ')
        if len(output) > 1 and output[1] == str(pid):
            return True
        return False
          
else:
    def isAlive(pid):
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True
 
 
