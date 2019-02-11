#!/bin/env python 
import sys
import os
import warnings
import json
from GRID_PiCaS_Launcher  import couchdb
from GRID_PiCaS_Launcher.get_token_field import get_token_field
from GRID_PiCaS_Launcher.set_token_field import set_token_field


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


def export_variable(name, value, overwrite=True):
    if name.upper()!= name:
        warnings.warn("environmental variable '{}' not in Uppercase! This may lead to errors".format(name))
    if name in os.environ.keys():
        print("!!!WARNING, Environment variable {0} already is set to {1}".format(name, os.environ[name]))
    if name in os.environ.keys() and not overwrite:
        print("!!!Will not overwrite environment variable {0}".format(name))
        return
    os.environ[name] = value

def export_tok_keys(cfgfile='tokvar.cfg',token=None):
    dbn=os.environ['PICAS_DB']
    un=os.environ['PICAS_USR']
    pwd=os.environ['PICAS_USR_PWD']
    try:
        tokvar=json.load(open(cfgfile,'rb'))
    except:
        set_token_field(token['_id'],'output',-2,dbn,un,pwd)
        raise Exception("tokvar missing")

    server = couchdb.Server("https://picas-lofar.grid.surfsara.nl:6984")
    server.resource.credentials = (un, pwd)
    db = server[dbn]
    for key in tokvar:
        if isinstance(tokvar[key],str):
            try:
                picas_val=str(get_token_field(token['_id'],
                    tokvar[key],dbn,un,pwd))
            except KeyError:
                sys.stderr.write("WARNING: Picas Variable Missing:"+key)
                picas_val=""
            export_variable(key,picas_val)
        elif key=='_attachments':
            for att_file in tokvar['_attachments']:
                picas_att_name = tokvar['_attachments'][att_file]
                get_attachment(db,token,picas_att_name,
                        savename=picas_att_name) #TODO: Add savename as an option
                export_variable(att_file, picas_att_name)


if __name__ == '__main__':
    export_tok_keys(cfgfile='tokvar.cfg')
