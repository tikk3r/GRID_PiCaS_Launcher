#!/bin/env python 
import sys,os
from get_token_field import get_token_field

try:
    import yaml
except ImportError:
    sys.path.append('compat')
    import yaml

def export_tok_keys(cfgfile='tokvar.cfg'):
    tokvar=yaml.load(open(cfgfile,'rb'))
    db=os.environ['PICAS_DB']
    un=os.environ['PICAS_USR']
    pwd=os.environ['PICAS_USR_PWD']
    for key in tokvar:
        if isinstance(tokvar[key],basestring):
            picas_val=get_token_field(os.environ['TOKEN'],key,db,un,pwd)
            os.environ[tokvar[key].split('$')[1]]=picas_val
        elif key=='_attachments':
            pass


if __name__ == '__main__':
    export_tok_keys('tokvar.cfg')
