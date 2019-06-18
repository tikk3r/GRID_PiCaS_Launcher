from GRID_PiCaS_Launcher  import couchdb
import os,sys,time
from GRID_PiCaS_Launcher.picas.clients import CouchClient


def upload_attachment(token_id=tok_id, attachment=attachment,
                      picas_credentials=p_creds, name=None):
    server = couchdb.Server(url="https://picas-lofar.grid.surfsara.nl:6984")
    p_usr, p_pwd, p_db = (picas_credentials.user,
                          picas_credentials.password,
                          picas_credentials.database)
    server.resource.credentials = (p_usr,p_pwd)
    db = server[p_db]
    token=db[token_id]
    currdate=time.strftime("%d/%m/%Y_%H.%M.%S_")
    client = CouchClient(url="https://picas-lofar.grid.surfsara.nl:6984", db=p_db, username=p_usr, password=p_pwd)
    if not name:
        name=currdate+attachment
    else:
        name=attachment
    with open(attachment,'rb') as att:
        client.db.put_attachment(token,att,str(name))
    
if __name__ == '__main__':
    try:
        dbn=os.environ['PICAS_DB']
        usr=os.environ['PICAS_USR']
        passw=os.environ['PICAS_USR_PWD']
        set_token_field(sys.argv[-3],sys.argv[-2],sys.argv[-1],dbn,usr,passw)
    except:
        set_token_field(sys.argv[5],sys.argv[6],sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
 
