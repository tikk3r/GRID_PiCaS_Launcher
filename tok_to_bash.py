#!/bin/env python 
import sys,os
import Token
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
            t_type=get_token_field(os.environ['TOKEN'],'type',db,un,pwd)
            th=Token.Token_Handler(t_type=t_type,uname=un,pwd=pwd,dbn=db)
            for att_file in tokvar['_attachments']:
                th.get_attachment(os.environ['TOKEN'],att_file,savename=att_file) 
                if '$' in tokvar['_attachments'][att_file]:
                    os.environ[tokvar['_attachments'][att_file].split('$')[1]]=att_file

if __name__ == '__main__':
    export_tok_keys('tokvar.cfg')