from GRID_PiCaS_Launcher import couchdb
from GRID_PiCaS_Launcher.get_picas_credentials import PicasCred
import os,sys
 

def get_token_field(tok_id,fieldname,p_db,p_usr,p_pwd):
    server = couchdb.Server(url="https://picas-lofar.grid.surfsara.nl:6984")
    server.resource.credentials = (p_usr,p_pwd)
    db = server[p_db]
    token=db[tok_id]
    return  token[fieldname]


def main(*args):
    if len(args)==6:
        value=get_token_field(args[4],args[5],args[1],args[2],args[3])
    else:
        pc = PicasCred()
        dbn = pc.database
        usr = pc.user
        passw = pc.password
        value=get_token_field(args[-2],args[-1],dbn,usr,passw)
    print(value)
 
if __name__ == '__main__':
    main(sys.argv)
