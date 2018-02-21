#!/bin/env python 
import sys,os
from GRID_PiCaS_Launcher  import couchdb
from get_token_field import get_token_field
from set_token_field import set_token_field

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
        sys.stderr.write("error getting attachment")
        return ""
    if "/" in filename:
        savename = filename.replace("/", "_")
    if not savename:
        savename = filename
    with open(savename, 'w') as f:
        for line in attach:
            f.write(str(line))
    return os.path.abspath(filename)


def export_tok_keys(cfgfile='tokvar.cfg',token=None):
    dbn=os.environ['PICAS_DB']
    un=os.environ['PICAS_USR']
    pwd=os.environ['PICAS_USR_PWD']
    try:
        tokvar=yaml.load(open(cfgfile,'rb'))
    except:
        set_token_field(token['_id'],'output',-2,dbn,un,pwd)
        raise Exception("tokvar missing")

    server = couchdb.Server("https://picas-lofar.grid.sara.nl:6984")
    server.resource.credentials = (un, pwd)
    db = server[dbn]
    for key in tokvar:
        if isinstance(tokvar[key],str):
            try:
                picas_val=str(get_token_field(token['_id'],key,dbn,un,pwd))
            except KeyError:
                sys.stderr.write("WARNING: Picas Variable Missing:"+key)
                picas_val=""
            os.environ[tokvar[key].split('$')[1]]=picas_val
        elif key=='_attachments':
            for att_file in tokvar['_attachments']:
                get_attachment(db,token,att_file,savename=att_file) 
                if '$' in tokvar['_attachments'][att_file]:
                    os.environ[tokvar['_attachments'][att_file].split('$')[1]]=att_file

if __name__ == '__main__':
    export_tok_keys(cfgfile='tokvar.cfg')
