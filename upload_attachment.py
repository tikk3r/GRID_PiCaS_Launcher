import couchdb
import os,sys,time

def upload_attachment(tok_id,attachment,p_db,p_usr,p_pwd):
    server = couchdb.Server(url="https://picas-lofar.grid.sara.nl:6984")
    server.resource.credentials = (p_usr,p_pwd)
    db = server[p_db]
    token=db[tok_id]
    currdate=time.strftime("%d/%m/%Y_%H.%M.%S_")
    self.client.db.put_attachment(token,open(attachment,'rb'),currdate+attachment)
    db.update([token])


if __name__ == '__main__':
    try:
        dbn=os.environ['PICAS_DB']
        usr=os.environ['PICAS_USR']
        passw=os.environ['PICAS_USR_PWD']
        set_token_field(sys.argv[-3],sys.argv[-2],sys.argv[-1],dbn,usr,passw)
    except:
        set_token_field(sys.argv[5],sys.argv[6],sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
 
