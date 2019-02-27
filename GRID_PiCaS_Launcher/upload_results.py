from GRID_PiCaS_Launcher  import couchdb
import os
import sys
import time
import tarfile
import subprocess
from GRID_PiCaS_Launcher.picas.clients import CouchClient

from datetime import datetime                                                                                                               
import json
import pdb

if '__enter__' not in dir(tarfile.TarFile): #Patch for python2.6
    class tarfile(tarfile.TarFile):
        def __enter__(self):
            return self
        def __exit__(self,type, value, traceback):
            if type is None:
                    self.close()



def get_date(json_data):
    """Crom a dictionary context, gets the granularity with which to mask the date"""
    upload = json_data

    if not upload or not upload.get('add_date'):
        return ""
    
    if upload.get('date_granularity') == 'hour':
        mask = "%Y-%m-%d_%H:00"
    elif upload.get('date_granularity') == 'minute':
        mask = "%Y-%m-%d_%H:%M"
    elif upload.get('date_granularity') == 'month':
        mask = "%Y-%m"
    elif upload.get('date_granularity') == 'week':
        mask = "%Y-W%V"
    else:
        mask = "%Y-%m-%d"

    now=datetime.now()
    formatted_date = now.strftime(mask)
    return formatted_date

def replace_env_vars(s, variables=None):
    if not variables:
        return s
    for variable in variables:
        s = s.replace("${0}".format(variable), #keeps the $VARIABLE if not in env
                      os.environ.get(variable,"${0}".format(variable)))
    return s

class UploadError(Exception):
    def __init__(self, message, errors):
        self.return_code = -1
        message = "{0}, Exit code {1}".format(message, self.return_code)
        super(UploadError, self).__init__(message)

class GSIUploadError(UploadError):
    """Generic Upload Error using GSITools"""
    def __init__(self, message, return_code, errors=""):
        self.return_code = return_code
        super(GSIUploadError, self).__init__(message, errors)

class FileExistsError(UploadError):
    pass

def upload_gsi(src_file, dest_location, uploader=None, pattern=None):
    """uses an uploader class to upload results from src file
    to the dest location 

    """
    if not uploader:
        return
    if not pattern:
        uploader.upload(src_file, dest_location+"/"+src_file)
    else:
        formatted_filename = format_file(src_file, pattern)
        uploader.upload(src_file, dest_location+"/"+formatted_filename)


class uploader(object):
    def __init__(self, context):
        self.context = self._get_context(context)
        self._suffix = '.tar'
        self._date = get_date(self.context)
        self._path= "{0}/{1}".format(self.context['location'], self.context['template'])
        self._path = self._path.replace("$DATE", self._date)
        if "$" in self._path:
            if 'variables' in context and '_token_keys' in context['variables']:
                self._path = replace_env_vars(self._path, context['variables']['_token_keys'])
            else:
                warnings.warn("No variables found")

    @staticmethod   
    def _get_context(context):
        if isinstance(context,str):
            if os.path.exists(context):
                tmp_ctx = json.load(open(context))
            else:
                tmp_ctx = json.loads(context)
        else:
            tmp_ctx = context
        if 'upload' in tmp_ctx.keys():
            return tmp_ctx['upload']
        return tmp_ctx
        
    def _communicate(self, subprocess_popen, raise_exception=None):
        """Helper function to process the subprocess.Popen output"""
        out, err = subprocess_popen.communicate()
        if not err:
            return out
        if raise_exception:
            raise raise_exception(err, -1)

    def upload(self):
        output_dir = os.environ['RUNDIR']+"/Output"
        return_dir = os.getcwd()
        try:
            os.chdir(output_dir)
            if self.context.get('gzip'):
                upload_file = self.compress()
            else:
                upload_file = self.tarball()
            self._upload(upload_file)
        finally:
            os.chdir(return_dir)

    def compress(self):
        self._suffix = '.tar.gz'
        with tarfile.open('upload.tar.gz', mode='w:gz') as archive:
            archive.add(os.getcwd(), recursive=True, arcname='')
        return "{0}/{1}".format(os.getcwd(),"upload.tar.gz")

    def tarball(self):
        with tarfile.open('upload.tar', mode='w') as archive:
                archive.add(os.getcwd(), recursive=True, arcname='')
        return "{0}/{1}".format(os.getcwd(),  "upload.tar")             
    
    def _upload(self, *args, **kwargs):
        raise NotImplementedError("Implement this for concrete uploader")

class GSIUploader(uploader):
    def __init__(self, context):
        """Gets the 'upload' Dict as context and uploads file to GSIFTP location"""
        self.context = self._get_context(context)
        _uberftp_result = subprocess.call(['which','uberftp'])
        _globus_result = subprocess.call(['which','globus-url-copy'])

        if _uberftp_result !=0 or _globus_result !=0:
            raise RuntimeError("Either uberftp or globus-url-copy are not installed")
        super(GSIUploader, self).__init__(context)
        self.upload()
        
    def _remove(self, path):
        command = ['uberftp', '-ls',  path]
        out, err = subprocess.Popen(command,stdout=subprocess.PIPE,  stderr=subprocess.PIPE).communicate()
        if out =='':
            return
        command = ['uberftp', '-rm',  path]
        _remove = subprocess.Popen(command,
                                    stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        return self._communicate(_remove, GSIUploadError)

    def _upload(self, upload_file):
        if self.context.get('overwrite'):
            self._remove(self._path+self._suffix)
        command = ['globus-url-copy',upload_file, self._path+self._suffix]
        _upload_file = subprocess.Popen(command,
                                        stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        return self._communicate(_upload_file, GSIUploadError)
        

