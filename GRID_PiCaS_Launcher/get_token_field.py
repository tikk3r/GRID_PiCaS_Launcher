from GRID_PiCaS_Launcher import couchdb
from GRID_PiCaS_Launcher.get_picas_credentials import PicasCred
import os,sys
 

def get_token_field(tok_id,fieldname, picas_cred):
    """Returns the field of a token from a database as authenticated by a
    picas_cred opject"""
    server = couchdb.Server(url="https://picas-lofar.grid.surfsara.nl:6984")
    server.resource.credentials = (picas_cred.user, picas_cred.password)
    db = server[picas_cred.database]
    token=db[tok_id]
    return  token[fieldname]


def main(*args):
    if len(args)==6:
        pc = PicasCred(usr=args[2], pwd=args[3], dbn=args[1])
        value=get_token_field(args[4], args[5], pc)
    else:
        pc = PicasCred()
        dbn = pc.database
        usr = pc.user
        passw = pc.password
        value=get_token_field(args[-2], args[-1], pc)
    print(value)
 
if __name__ == '__main__':
    main(sys.argv)
