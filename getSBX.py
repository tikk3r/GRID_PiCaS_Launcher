# ===================================================================================== #
# author: Natalie Danezi <anatoli.danezi@surfsara.nl>   --  SURFsara                #
# helpdesk: Grid Services <grid.support@surfsara.nl>    --  SURFsara                #
#                                                                                   #
# usage: python pilot.py [picas_db_name] [picas_username] [picas_pwd]            #
# description:                                                                      #
#    Connect to PiCaS server with [picas_username] [picas_pwd]                   #
#    Get the next token in todo View                            #
#    Fetch the token parameters                             #
#    Run the main job (master_step23_v3.sh) with the proper input arguments        #
#    Get sterr and stdout in the output field of the token                #
# ===================================================================================== #

#python imports
import sys,os
import time
import couchdb
import subprocess
import shutil

#picas imports
from picas.actors import RunActor
from picas.clients import CouchClient
from picas.iterators import BasicViewIterator
from picas.modifiers import BasicTokenModifier
from picas.executers import execute

from update_token_status import update_status
from set_token_field import set_token_field

from tok_to_bash import  export_tok_keys

class ExampleActor(RunActor):
    def __init__(self, iterator, modifier):
        self.iterator = iterator
        self.modifier = modifier
        self.client = iterator.client

    def process_token(self, key, token):
    # Print token information
        os.environ['PICAS_DB']=str(sys.argv[1])
        os.environ['PICAS_USR']=str(sys.argv[2])
        os.environ['PICAS_USR_PWD']=str(sys.argv[3])
        os.environ['TOKEN']=token['_id']
    
        if 'SBXloc' in token.keys():
            location=token['SBXloc']
        else:
            location="gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/sandbox/sandbox_"+str(sys.argv[2])+"_"+str(token['OBSID'])+".tar"
    
        print("Sandbox Location= "+location)
    
        ## TODO: If no globus-tools, use wget
        subprocess.call(["globus-url-copy", location, "sandbox.tar"])
        subprocess.call(["tar", "-xf", "sandbox.tar"])
        subprocess.call(["chmod","a+x","master.sh"])
    
        print "Working on token: " + token['_id']
    
        tok_att=token["_attachments"].keys()
        export_tok_keys('tokvar.cfg')
    
        ## Read tokvar values from token and write to bash variables if not already exist! Save attachments and export abs filename to variable
        set_token_field(tok_id=token['_id'],fieldname='status',value='launched',p_db=os.environ['PICAS_DB'],p_usr=os.environ['PICAS_USR'],p_pwd=os.environ['PICAS_USR_PWD'])
    
        #The launched script is simply master.sh with token and picas authen stored in env vars
        #master.sh takes the variables straight from the token. 
        command = "/usr/bin/time -v ./master.sh 2> logs_.err 1> logs_out"
        print command
        
        out = execute(command,shell=True)
        print 'exit status is ',out
        curdate=time.strftime("%d/%m/%Y_%H:%M:%S_")
        try:
           logsout = "logs_out"
           log_handle = open(logsout, 'rb')
           self.client.db.put_attachment(token,log_handle,curdate+logsout)
           logserr = "logs_.err"
           log_handle = open(logserr, 'rb')
           self.client.db.put_attachment(token,log_handle,curdate+logserr)
        except:
           pass

        return

        

def main():
    # setup connection to db
    db_name = sys.argv[1]
    client = CouchClient(url="https://picas-lofar.grid.sara.nl:6984", db=str(sys.argv[1]), username=str(sys.argv[2]), password=str(sys.argv[3]))
    # Create token modifier
    modifier = BasicTokenModifier()
    # Create iterator, point to the right todo view
    iterator = BasicViewIterator(client, sys.argv[4]+"/todo", modifier)
    # Create actor, takes one token from todo view
    actor = ExampleActor(iterator, modifier)
    # Start work!
    actor.run()

if __name__ == '__main__':
    main()
