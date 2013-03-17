import subprocess
LOCATE = "/usr/bin/locate.findutils"

def find(query,paths,ignore_case=True,max_res=None):
    
    args=[LOCATE]
    
    if ignore_case:
        args.append("-i")
    if max_res:
        args.extend(["-l","%d"%max_res])
    args.append("-b")#Added
    args.extend(["-d",":".join(paths)])
    args.append(query) #args.extend(query.split())
    req=subprocess.Popen(args,bufsize=-1,
                              stdout=subprocess.PIPE,
                              universal_newlines=True)
    return req.communicate()[0].splitlines()    
