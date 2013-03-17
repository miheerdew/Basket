import os
import os.path as op

base = op.dirname(op.abspath(__file__))
PASS_FILE = '.password_hash'
USERS_FILE='USER_TABLE'
DATA_DIR = op.join(base,'CENTRAL/DATA')
PUBLIC_ROOT = op.join(base,'CENTRAL')
BUFF_SIZE = 1024*4
MAX_SEARCH_RESULTS= 20
ONLINE_THRESHOLD= 300

