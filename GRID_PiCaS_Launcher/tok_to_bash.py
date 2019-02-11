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
        warnings.warn("environmental variable '{0}' not in Uppercase! This may lead to errors".format(name))
    if name in os.environ.keys():
        print("!!!WARNING, Environment variable {0} already is set to {1}".format(name, os.environ[name]))
    if name in os.environ.keys() and not overwrite:
        print("!!!Will not overwrite environment variable {0}".format(name))
        return
    os.environ[name] = value

def export_dict_to_env(db, variable_dictionary, token_id):
    for head in variable_dictionary:
        if head  == "_token_keys":
            for var in variable_dictionary["_token_keys"]:
                try:
                    picas_val=str(get_token_field(token_id,
                        variable_dictionary["_token_keys"][var], dbn, un, pwd))
                except KeyError:
                    warnings.warn("WARNING: Picas Variable Missing: "+var)
                    continue
                if var[0] == "$":
                    variable = var[1:]
                else:
                    variable = var
                export_variable(variable, picas_val)
        elif head == '_attachments':
            for att_file in variable_dictionary['_attachments']:
                picas_att_name = variable_dictionary['_attachments'][att_file]
                token = db[token_id]
                get_attachment(db,token,picas_att_name,
                        savename=picas_att_name) #TODO: Add savename as an option
                export_variable(att_file, picas_att_name)



def export_tok_keys(cfgfile='tokvar.json',token=None):
    dbn=os.environ['PICAS_DB']
    un=os.environ['PICAS_USR']
    pwd=os.environ['PICAS_USR_PWD']
    try:
        with open(cfgfile,'r') as _f:
            tokvar=json.load(_f)
    except Exception as e:
        set_token_field(token['_id'],'output',-2,dbn,un,pwd)
        raise Exception("tokvar read error {0}".format(str(e)))

    server = couchdb.Server("https://picas-lofar.grid.surfsara.nl:6984")
    server.resource.credentials = (un, pwd)
    db = server[dbn]
    export_dict_to_env(db, tokvar, token['_id'])


if __name__ == '__main__':
    export_tok_keys(cfgfile='tokvar.json')
