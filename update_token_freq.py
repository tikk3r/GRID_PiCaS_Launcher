#=========
#Updates the status of the token from a shell script or another python script
#
#=========

import couchdb
import os,sys,time

def update_frequency(p_db,p_usr,p_pwd,tok_id,status):
    """This function updates the token's frequency field with the 
	value provided to it. 
    """
    try:
        server = couchdb.Server(url="https://picas-lofar.grid.sara.nl:6984")
        server.resource.credentials = (p_usr,p_pwd)
        db = server[p_db]
    except couchdb.http.ServerError:
        time.sleep(2)
        update_status(p_db,p_usr,p_pwd,tok_id,status)

    token=db[tok_id] 
    if 'FREQ' in token.keys:
    	token['FREQ']=status
    db.update([token]) 

if __name__ == '__main__':
    """Updates the FREQ field of the token from the commandline.
	WARNING: Make sure you run with a vanilla python, will crash
	when run with the LOFAR python exe.  
    """
    ##TODO: Put the entire taql command here so the input is the MS 
    update_frequency(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])

