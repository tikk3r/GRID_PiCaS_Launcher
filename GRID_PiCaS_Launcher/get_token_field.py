from GRID_PiCaS_Launcher import couchdb
from GRID_PiCaS_Launcer.get_picas_credentials import picas_cred
import os,sys
 

def get_token_field(tok_id,fieldname,p_db,p_usr,p_pwd):
    server = couchdb.Server(url="https://picas-lofar.grid.surfsara.nl:6984")
    server.resource.credentials = (p_usr,p_pwd)
    db = server[p_db]
    token=db[tok_id]
    return  token[fieldname]


if __name__ == '__main__':
    if len(sys.argv==5):
        value=get_token_field(sys.argv[4],sys.argv[5],sys.argv[1],sys.argv[2],sys.argv[3])
        value=get_token_field(sys.argv[-2],sys.argv[-1],dbn,usr,passw)
    else:
        pc = picas_cred()
        db = picas_cred.database
        usr = picas_cred.user
        passw = picas_cred.password
        value=get_token_field(sys.argv[-2],sys.argv[-1],dbn,usr,passw)
    print(value)
 
