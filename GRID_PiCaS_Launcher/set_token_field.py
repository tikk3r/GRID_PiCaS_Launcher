from GRID_PiCaS_Launcher import couchdb
from GRID_PiCaS_Launcher.get_picas_credentials import picas_cred
import os,sys,time

def set_token_field(tok_id,fieldname,value,p_db,p_usr,p_pwd):
    server = couchdb.Server(url="https://picas-lofar.grid.surfsara.nl:6984")
    server.resource.credentials = (p_usr,p_pwd)
    db = server[p_db]
    token=db[tok_id]
    token[fieldname]=value
    db.update([token])

def main(*arguments):
    arguments = arguments[0]
    if len(arguments)<=5:
        pc = picas_cred()
        database = pc.database
        username =  pc.user
        password =  pc.password
        token_id = arguments[-3]
        fieldname = arguments[-2]
        value = arguments[-1]
    else:
        token_id = arguments[0]
        fieldname = arguments[1]
        value = arguments[2]
        database = arguments[3]
        username = arguments[4]
        password = arguments[5]
    set_token_field(token_id, fieldname, value, database, username, password)


if __name__ == '__main__':
    main(sys.argv[1:])
