from GRID_PiCaS_Launcher import couchdb
from GRID_PiCaS_Launcher.get_picas_credentials import PicasCred
import os, sys, time


def set_token_field(tok_id, fieldname, value, pcreds):
    """Sets the fields of a token to a specified value, 
    authentication is done through a picas_creds object"""
    server = couchdb.Server(url="https://picas-lofar.grid.surfsara.nl:6984")
    server.resource.credentials = (pcreds.user, pcreds.password)
    db = server[pcreds.database]
    token = db[tok_id]
    token[fieldname] = value
    db.update([token])


def main(*arguments):
    if isinstance(arguments[0], list):
        arguments = arguments[0]
    if len(arguments) <= 5:
        pc = PicasCred()
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
        pc = PicasCred(usr=username, pwd=password, dbn=database)
    set_token_field(token_id, fieldname, value, pc)


if __name__ == "__main__":
    main(sys.argv[1:])
