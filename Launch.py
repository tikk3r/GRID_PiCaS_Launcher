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
from GRID_PiCaS_Launcher import couchdb
import subprocess
import shutil
import glob

#picas imports
from GRID_PiCaS_Launcher.picas.actors import RunActor
from GRID_PiCaS_Launcher.picas.clients import CouchClient
from GRID_PiCaS_Launcher.picas.iterators import BasicViewIterator
from GRID_PiCaS_Launcher.picas.modifiers import BasicTokenModifier
from GRID_PiCaS_Launcher.picas.executers import execute

#token imports
from GRID_PiCaS_Launcher.update_token_status import update_status
from GRID_PiCaS_Launcher.set_token_field import set_token_field
from GRID_PiCaS_Launcher.upload_attachment import upload_attachment

#from tok_to_bash import  export_tok_keys

import pdb

class ExampleActor(RunActor):
    def __init__(self, iterator, modifier):
        self.iterator = iterator
        self.modifier = modifier
        self.client = iterator.client


    def download_sandbox(self,command,location):
        if os.path.isfile("sandbox.tar"): os.remove("sandbox.tar")
        if command=='globus-url-copy':
            subprocess.call([command, location, "sandbox.tar"])
        elif command=='wget':
            subprocess.call([command, location, "-O",'sandbox.tar'])
        if os.stat("sandbox.tar").st_size == 0: 
            set_token_field(self.token_name,'output',-2,self.p_db,self.p_usr,self.p_pwd)
            set_token_field(self.token_name,'done',time.time(),self.p_db,self.p_usr,self.p_pwd)
            raise Exception("Sandbox failed to download!")

    def process_token(self, key, token):
    # Print token information
        os.environ['PICAS_DB']=str(sys.argv[1])
        os.environ['PICAS_USR']=str(sys.argv[2])
        os.environ['PICAS_USR_PWD']=str(sys.argv[3])
        os.environ['TOKEN']=token['_id']
        from GRID_PiCaS_Launcher.tok_to_bash import  export_tok_keys

        self.p_db=os.environ['PICAS_DB']
        self.p_usr=os.environ['PICAS_USR']
        self.p_pwd=os.environ['PICAS_USR_PWD']
        self.token_name=token['_id'] 
        if 'SBXloc' in token.keys():
            location=token['SBXloc']
        else:
            location="gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/sandbox/sandbox_"+str(sys.argv[2])+"_"+str(token['OBSID'])+".tar"
    
        print("Sandbox Location= "+str(location))
    
        rc = subprocess.call(['which', 'globus-url-copy'])

        if rc == 0:
            if 'gsiftp' not in location and 'strw' not in location:
                location='gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/sandbox/'+location
            self.download_sandbox('globus-url-copy',location)
        else:
            if 'strw' in location :
                location='/'.join(location.split('/')[-2:])
                location='ftp://ftp.strw.leidenuniv.nl/pub/apmechev/sandbox/'+location
                self.download_sandbox('wget',location)
            else:
                self.download_sandbox('globus-url-copy',location)

        subprocess.call(["tar", "-xf", "sandbox.tar"])
        subprocess.call(["chmod","a+x","master.sh"])
    
        print("Working on token: " + token['_id'])
        export_tok_keys('tokvar.cfg',token)
    
        ## Read tokvar values from token and write to bash variables if not already exist! Save attachments and export abs filename to variable

        set_token_field(token['_id'],'status','launched',self.p_db,self.p_usr,self.p_pwd)
        RUNDIR=os.getcwd() 

        #The launched script is simply master.sh with token and picas authen stored in env vars
        #master.sh takes the variables straight from the token. 
        command = "/usr/bin/time -v ./master.sh 2> logs_.err 1> logs_out"
        print("executing "+command)
        
        out = execute(command,shell=True)
        print('exit status is '+str(out))
        set_token_field(token['_id'],'output',out[0],self.p_db,self.p_usr,self.p_pwd)
        if out[0]==0:
            set_token_field(token['_id'],'status','done',self.p_db,self.p_usr,self.p_pwd)
        else:
            set_token_field(token['_id'],'status','error',self.p_db,self.p_usr,self.p_pwd)
        
        os.chdir(RUNDIR)
        try:
           logsout = "logs_out"
           upload_attachment(token['_id'],logsout,self.p_db,self.p_usr,self.p_pwd)
           logserr = "logs_.err"
           upload_attachment(token['_id'],logserr,self.p_db,self.p_usr,self.p_pwd)
        except:
           pass

        #Just attaches all png files in the working directory to the token
        sols_search=subprocess.Popen(["find",".","-name","*.png","-o","-name","*.fits"],stdout=subprocess.PIPE)
        result=sols_search.communicate()[0]

        for png in result.split():
            upload_attachment(token['_id'],png,self.p_db,self.p_usr,self.p_pwd,name=png)
            #            try:
#                upload_attachment(token['_id'],png,p_db,p_usr,p_pwd,name=png)
#               time.sleep(2)
#            except:
#                print("error attaching "+str(png))
        #try reuploading the last png (for some reason last png corrupts>)
        #self.client.db.put_attachment(token,open(os.path.basename(png),'r'),os.path.split(png)[1])
        # Attach logs in token
#        for tmpdir in glob.glob('tmp.*'):
#            shutil.rmtree(tmpdir)
        self.client.modify_token(self.modifier.close(self.client.db[self.token_name]))
        return

        

def main():
    # setup connection to db
    db_name = sys.argv[1]
    client = CouchClient(url="https://picas-lofar.grid.surfsara.nl:6984", db=str(sys.argv[1]), username=str(sys.argv[2]), password=str(sys.argv[3]))
    # Create token modifier
    modifier = BasicTokenModifier()
    # Create iterator, point to the right todo view
    iterator = BasicViewIterator(client, sys.argv[4]+"/todo", modifier)
    # Create actor, takes one token from todo view
    actor = ExampleActor(iterator, modifier)
    # Start work!
    try:
        actor.run()
    except Exception as e:
        print(str(e.args))
#        set_token_field(actor.token_name,'status','error',actor.p_db,actor.p_usr,actor.p_pwd)
        set_token_field(actor.token_name,'launcher_status',str(e.args),actor.p_db,actor.p_usr,actor.p_pwd)


if __name__ == '__main__':
    main()
