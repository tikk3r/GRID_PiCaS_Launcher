from GRID_PiCaS_Launcher import couchdb
import os, sys, time
from GRID_PiCaS_Launcher.picas.clients import CouchClient
from GRID_PiCaS_Launcher.get_picas_credentials import PicasCred


def upload_attachment(
    token_id="null", attachment="", picas_credentials=None, name=None
):
    server = couchdb.Server(url="https://picas-lofar.grid.surfsara.nl:6984")
    p_usr, p_pwd, p_db = (
        picas_credentials.user,
        picas_credentials.password,
        picas_credentials.database,
    )
    server.resource.credentials = (p_usr, p_pwd)
    db = server[p_db]
    token = db[token_id]
    currdate = time.strftime("%d/%m/%Y_%H.%M.%S_")
    client = CouchClient(
        url="https://picas-lofar.grid.surfsara.nl:6984",
        db=p_db,
        username=p_usr,
        password=p_pwd,
    )
    if not name:
        name = currdate + attachment
    else:
        name = attachment
    with open(attachment, "rb") as att:
        client.db.put_attachment(token, att, str(name))


if __name__ == "__main__":
    try:
        pc = PicasCred()
        upload_attachment(sys.argv[5], sys.argv[6], pc)
    except:
        pc = PicasCred(dbn=sys.argv[1], usr=sys.argv[2], pwd=sys.argv[3])
        set_token_field(sys.argv[5], sys.argv[6], pc)
