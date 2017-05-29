#!/bin/env python 
import sys,os
import couchdb
from get_token_field import get_token_field

try:
    import yaml
except ImportError:
    sys.path.append('compat')
    sys.path.append('compat/yaml')
    import yaml

def get_attachment(db,token, filename, savename=None):
    try:
        attach = db.get_attachment(token, filename).read()
    except AttributeError:
        print("error getting attachment")
        return ""
    if "/" in filename:
        savename = filename.replace("/", "_")
    if not savename:
        savename = filename
    with open(savename, 'w') as f:
        for line in attach:
            f.write(line)
    return os.path.abspath(filename)


def export_tok_keys(cfgfile='tokvar.cfg',token=None):
    tokvar=yaml.load(open(cfgfile,'rb'))
    dbn=os.environ['PICAS_DB']
    un=os.environ['PICAS_USR']
    pwd=os.environ['PICAS_USR_PWD']
    server = couchdb.Server("https://picas-lofar.grid.sara.nl:6984")
    server.resource.credentials = (un, pwd)
    db = server[dbn]
    for key in tokvar:
        if isinstance(tokvar[key],str):
            picas_val=str(get_token_field(token['_id'],key,dbn,un,pwd))
            os.environ[tokvar[key].split('$')[1]]=picas_val
        elif key=='_attachments':
            for att_file in tokvar['_attachments']:
                get_attachment(db,token,att_file,savename=att_file) 
                if '$' in tokvar['_attachments'][att_file]:
                    os.environ[tokvar['_attachments'][att_file].split('$')[1]]=att_file

if __name__ == '__main__':
    export_tok_keys(cfgfile='tokvar.cfg')
