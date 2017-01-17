import couchdb
import os,sys,time

def get_token_field(p_db,p_usr,p_pwd,tok_id,fieldname,value):
    server = couchdb.Server(url="https://picas-lofar.grid.sara.nl:6984")
    server.resource.credentials = (p_usr,p_pwd)
    db = server[p_db]
    token=db[tok_id]
    token[fieldname]=value
    db.update([token])


if __name__ == '__main__':
    get_token_field(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])
 
