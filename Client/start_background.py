import subprocess
import os
import os.path as op
import sys

base = op.dirname(op.abspath(__file__))
subprocess.Popen([sys.executable,op.join(base,"start.py")])
sys.exit()
