#=========
#Updates the status of the token from a shell script or another python script
#
#=========

import couchdb
import os,sys,time

def update_status(p_db,p_usr,p_pwd,tok_id,status):
    '''Updates the status field of the token with the string held in status
	and logs the time at which the status changed with the times field as a dictionary
	If the token is marked as done, the progress field is set as 1
    '''
    server = couchdb.Server(url="https://picas-lofar.grid.sara.nl:6984")
    server.resource.credentials = (p_usr,p_pwd)
    db = server[p_db]
    token=db[tok_id] 
    token['status']=status #TODO: create these fields if there's an IndexError
    token['times'][status]=time.time()
    if status=='done':
        try:
            token['progress']=1
        except KeyError:
            pass
    db.update([token]) 
    with open('pipeline_status','w') as stat_file:
        stat_file.write(status)

if __name__ == '__main__':
    update_status(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])

