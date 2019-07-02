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

import sys
print("!!!!!!!!!!!!!!!!!!!!!")
print("!!!!!!!!!!!!!!!!!!!!!")
print("If you're seeing this, you're using the default GRID_PiCaS_Launcher branch")
print("This is no longer the master branch or the (working) version 0.1")
print("If anything fails or acts weird, then place this line in your launcher script")
print("\'git checkout v0.1 \'")
print("!!!!!!!!!!!!!!!!!!!!!!")
print("!!!!!!!!!!!!!!!!!!!!!!")
#python imports
import sys,os
import time
from GRID_PiCaS_Launcher import couchdb
from GRID_PiCaS_Launcher.get_picas_credentials import PicasCred
import subprocess
import shutil
import glob
import warnings
import traceback
import logging

#picas imports
from GRID_PiCaS_Launcher.picas.actors import RunActor
from GRID_PiCaS_Launcher.picas.clients import CouchClient
from GRID_PiCaS_Launcher.picas.iterators import BasicViewIterator
from GRID_PiCaS_Launcher.picas.modifiers import BasicTokenModifier
from GRID_PiCaS_Launcher.picas.executers import execute

from GRID_PiCaS_Launcher.launcher_logging import logger

#token imports
from GRID_PiCaS_Launcher.update_token_status import update_status
from GRID_PiCaS_Launcher.set_token_field import set_token_field
from GRID_PiCaS_Launcher.upload_attachment import upload_attachment
from GRID_PiCaS_Launcher.tok_to_bash import export_dict_to_env
from GRID_PiCaS_Launcher.singularity import parse_singularity_link
from GRID_PiCaS_Launcher.singularity import parse_json_payload 
from GRID_PiCaS_Launcher.upload_results import GSIUploader
from GRID_PiCaS_Launcher.upload_results import uploader 

#from tok_to_bash import  export_tok_keys
from GRID_PiCaS_Launcher import sandbox
import pdb
from multiprocessing import Process
from GRID_PiCaS_Launcher import __file__

class ExampleActor(RunActor):
    def __init__(self, iterator, modifier):
        self.iterator = iterator
        self.modifier = modifier
        self.client = iterator.client

    def create_sandbox(self, json_payload=None):
        if not json_payload:
            json_payload = self.config
        if 'sandbox' not in json_payload.keys():
            logging.warn("No sandbox configuration")
            logging.warn("json_payload keys are {0}".format(json_payload.keys()))
            return
        sbx = sandbox.Sandbox(config_json=json_payload['sandbox'])
        sbx.build_sandbox(True)# Not needed

    def get_image(self,config=None):
        """get_image: Downloads the image in the cwd
        and sets the environment variable $SIMG to point to
        the local downloaded image. 

        :param config:Optional config JSON, if None, we use
        the ExampleActor.config member
        """
        if not config:
            config = self.config
        logging.info("getting image from {0}".format(config))
        simg_config = parse_json_payload(config)
        image_location = parse_singularity_link(simg_config['SIMG'],
                                                simg_config['SIMG_COMMIT'])
        os.environ['SIMG'] = image_location

    @staticmethod
    def get_variables_from_config(config, variables=None):
        if not variables:
            variables = {}
        if 'variables' in config.keys():
            logging.info("Getting variables from config file")
            _vars = config['variables']
            for var in _vars:
                logging.debug("Setting Environment variable {0} to {1}".format(var, _vars[var]))
                variables[var]=_vars[var]
        else:
            logging.warn("No Variables found in the token config. Nothing is put in the environment!")
            return {}
        return variables

    def download_sandbox(self, token):
        if 'SBXloc' in token.keys():
            location=token['SBXloc']
        else:
            return None
        sbx = sandbox.Sandbox(location=location)
        sbx.download_sandbox()

    def upload_logs(self, logs_dir):
        os.chdir(logs_dir)
        logsout = "logs_out"
        logserr = "logs_.err"
        if os.path.isfile(logsout):
            upload_attachment(token_id=self.token_name, attachment=logsout, picas_credentials=self.p_creds)
        if os.path.isfile(logserr):
            upload_attachment(token_id=self.token_name, attachment=logsout, picas_credentials=self.p_creds)

    def process_token(self, key, token):
    # Print token information
        variables = {}
        os.environ['TOKEN']=token['_id']
        self.p_creds = PicasCred()
        self.p_creds.user = self.user
        self.p_creds.password = self.password
        self.p_creds.database = self.database
        self.p_creds.put_picas_creds_in_env()

        self.token_name=token['_id']
        logging.info("Working on token {0} from databse {1} as user {2}".format(
            self.token_name, self.database, self.user))
        self.config = token['config.json']
        variables = self.get_variables_from_config(self.config, variables)
        if 'container' in self.config.keys() or 'singularity' in self.config.keys():
            set_token_field(token['_id'],'status','pulling_container',self.database,self.user,self.password)
            self.get_image()

        self.download_sandbox(token) ##Will be removed!
        set_token_field(token['_id'],'status','building_sandbox',self.database,self.user,self.password)
        p = Process(target=self.create_sandbox)
        p.start()
        logging.info("Creating Sandbox from config: {0}".format(self.config['sandbox']))
        p.join()
        with open(os.devnull, 'w') as FNULL:
            subprocess.call(["chmod","a+x","master.sh"], stdout=FNULL, stderr=subprocess.STDOUT)

        export_dict_to_env(self.client.db, variables, self.token_name, db_name=self.database)

        logging.info("Working on token: " + token['_id'])
        ## Read tokvar values from token and write to bash variables if not already exist! Save attachments and export abs filename to variable

        set_token_field(token['_id'],'status','launched',self.database,self.user,self.password)
        RUNDIR=os.getcwd() 

        #The launched script is simply master.sh with token and picas authen stored in env vars
        #master.sh takes the variables straight from the token. 
        command = "/usr/bin/time -v ./master.sh 2> logs_.err 1> logs_out"
        logging.info("executing "+command)
        
        out = execute(command,shell=True)
        logging.info('master.sh exit status is '+str(out))

        set_token_field(token['_id'],'output',out[0],self.database,self.user,self.password)
        if out[0]==0:
            set_token_field(token['_id'],'status','done',self.database,self.user,self.password)
            logging.info("Job exited OK")
        else:
            set_token_field(token['_id'],'status','error',self.database,self.user,self.password)
            logging.error("Job exited with status {}".format(out[0]))

        self.upload_logs(RUNDIR)

        #Just attaches all png files in the working directory to the token
        sols_search=subprocess.Popen(["find",".","-name","*.png","-o","-name","*.fits"],stdout=subprocess.PIPE)
        result=sols_search.communicate()[0]

        for png in result.split():
            if isinstance(png, bytes):
                png = png.decode()
            upload_attachment(token_id=token['_id'], attachment=png, picas_credentials=self.p_creds)
            os.remove(png) 
        self.client.modify_token(self.modifier.close(self.client.db[self.token_name]))
        with open("{0}/GRID_PiCaS_Launcher.log".format(__file__.split("__init__")[0])) as f:
            print(f.read())
        return 

        

def main(url="https://picas-lofar.grid.surfsara.nl:6984", db=None, username=None, password=None, view='todo'):
    """The main function locks a token from a CouchDB view and executes
    process_token on the token which builds sandbox and runs scripts
    """
    # setup connection to db
    client = CouchClient(url=url, db=db, username=username, password=password)
    # Create token modifier
    modifier = BasicTokenModifier()
    # Create iterator, point to the right todo view
    iterator = BasicViewIterator(client, sys.argv[-1]+"/"+view, modifier)
    # Create actor, takes one token from todo view
    actor = ExampleActor(iterator, modifier)
    actor.user = username
    actor.database = db
    actor.password = password
    # Start work!
    try:
        actor.run()
    except Exception as e:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        del exc_info
        print("Exception occured")
        print(str(e.args))
#        set_token_field(actor.token_name,'status','error',actor.database,actor.p_usr,actor.password)
        set_token_field(actor.token_name,'launcher_status',str(e.args),actor.database,actor.user,actor.password)
    finally:
        with open("{0}/GRID_PiCaS_Launcher.log".format(__file__.split("__init__")[0])) as f:
            print(f.read())

if __name__ == '__main__':
    """Entry point of the Launcher. 
    The options are either 1: database, 2:username 3: password and 4: picas_token_type

    or 1: picas_token_type. In this case, we get the picas credentials from ~/.picasrc
          or from the environment variables""" 
    if len(sys.argv) > 4:
        db = str(sys.argv[1])
        username = str(sys.argv[2])
        password = str(sys.argv[3])
    else:
        pc = PicasCred()
        db = pc.database
        username = pc.user
        password = pc.password
    main(db=db, username=username, password=password)
