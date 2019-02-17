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
        set_token_field(arguments[-3],arguments[-2],arguments[-1],pc.database, pc.user, pc.password)
    else:
        set_token_field(arguments[5],arguments[6],arguments[1],arguments[2],arguments[3],arguments[4])


if __name__ == '__main__':
    main(sys.argv)
