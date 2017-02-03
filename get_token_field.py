import couchdb
import os,sys
 

def get_token_field(tok_id,fieldname,p_db,p_usr,p_pwd):
    server = couchdb.Server(url="https://picas-lofar.grid.sara.nl:6984")
    server.resource.credentials = (p_usr,p_pwd)
    db = server[p_db]
    token=db[tok_id]
    return  token[fieldname]


if __name__ == '__main__':
    try:
        dbn=os.environ['PICAS_DB']
        usr=os.environ['PICAS_USR']
        passw=os.environ['PICAS_USR_PWD']
        value=get_token_field(sys.argv[-2],sys.argv[-1],dbn,usr,passw)
    except:
       value=get_token_field(sys.argv[4],sys.argv[5],sys.argv[1],sys.argv[2],sys.argv[3])
    print value
 
