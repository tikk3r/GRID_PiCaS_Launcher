try:
    from urllib import urlretrieve, urlopen
except ImportError:
    from urllib.request import urlretrieve, urlopen
         
import os
import stat
import sys
import zipfile
import time
import tarfile
import warnings
import subprocess
from shutil import copyfile, move
from GRID_PiCaS_Launcher.picas.clients import CouchClient
from GRID_PiCaS_Launcher  import couchdb

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
    upload = json_data['upload']

    if not upload or not upload.get('add_date'):
        return ""
    
    if upload.get('date_granularity') == 'hour':
        mask = "%Y-%m-%d_%H-00"
    elif upload.get('date_granularity') == 'minute':
        mask = "%Y-%m-%d_%H-%M"
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
    """ Takes a dict of env variables with a prepender $, replaces the instances of these
    variables in the string with the value in the environemt"""
    
    if not variables:
        return s
    for variable in variables:
        s = s.replace(variable, #keeps the $VARIABLE if not in env
                os.environ.get(variable[1:], variable))
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
        if 'upload' not in self.context.keys():
            raise RuntimeError('no upload field in context')
        self._suffix = '.tar'
        self._date = get_date(self.context)
        if 'location' not in self.context['upload'] or self.context['upload']['location'] != '':
            self._path= "{0}/{1}".format(self.context['upload']['location'], self.context['upload']['template'])
        else:
            self._path = self.context['upload']['template']
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
        compress = self.context['upload'].get('gzip')
        os.chdir(output_dir)
        try:
            upload_file = self.tarball(compress=compress)
            self._upload(upload_file)
        finally:
            os.chdir(return_dir)

    def tarball(self, compress=False):
        if compress:
            mode = 'w:gz'
            self._suffix = '.tar.gz'
        else:
            mode = 'w'
            self._suffix = '.tar'
        with tarfile.open('upload{0}'.format(self._suffix), mode=mode) as archive:
                archive.add(os.getcwd(), recursive=True, arcname='')
        return "{0}/{1}".format(os.getcwd(),  "upload{0}".format(self._suffix))
    
    def _upload(self, *args, **kwargs):
        raise NotImplementedError("Implement this for concrete uploader")

class GSIUploader(uploader):
    def __init__(self, context):
        """Gets the 'upload' Dict as context and uploads file to GSIFTP location"""
        self.context = self._get_context(context)
        #_uberftp_result = subprocess.call(['which','uberftp'])
        _globus_result = subprocess.call(['which','globus-url-copy'])
        _gfal_result = subprocess.call(['which','gfal-copy'])

        #if _uberftp_result !=0 or _globus_result !=0 or _gfal_result != 0:
        if _uberftp_result !=0 or _globus_result !=0 or _gfal_result != 0:
            raise RuntimeError("Either globus-url-copy or gfal-copy is not installed")
        super(GSIUploader, self).__init__(context) 
    #    self.upload()
        
    def _remove(self, path):
        command = ['gfal-ls',  path]
        out, err = subprocess.Popen(command,stdout=subprocess.PIPE,  stderr=subprocess.PIPE).communicate()
        if out =='':
            return
        command = ['gfal-rm',  path]
        _remove = subprocess.Popen(command,
                                    stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        return self._communicate(_remove, GSIUploadError)

    def _upload(self, upload_file):
        if self.context['upload'].get('overwrite'):
            self._remove(self._path+self._suffix)
        print("\n{}".format(self._path+self._suffix))
        command = ['globus-url-copy',upload_file, self._path+self._suffix]
        _upload_file = subprocess.Popen(command,
                                        stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        return self._communicate(_upload_file, GSIUploadError)
        
class RcloneUploader(uploader):
    """Uploader that downloads rclone and uses it to upload data to the upload location"""
    def __init__(self, context, macaroon='upload.conf'):
        self.context = self._get_context(context) 
        rclone_link = 'https://downloads.rclone.org/rclone-current-linux-amd64.zip'
        urlretrieve(rclone_link, 'rclone.zip')
        with zipfile.ZipFile('rclone.zip', 'r') as zip_ref:
            zip_ref.extractall('rclone')
            rclone_files = zip_ref.namelist() 
        rclone_file = None
        for link in rclone_files:
            if link.split('/')[1] == 'rclone':
                rclone_file = "{}/rclone/{}".format(os.getcwd(), link)
        self._rclone_path = rclone_file
        st = os.stat(self._rclone_path)
        os.chmod(self._rclone_path, st.st_mode | stat.S_IEXEC)
        self.macaroon = macaroon
        self.macaroon_head = macaroon.split('.conf')[0]
        copyfile(macaroon, "{}/Output/{}".format(os.environ['RUNDIR'], macaroon))
        super(RcloneUploader, self).__init__(context)

    def _upload(self, upload_file):
       print("\n{}".format(self._path+self._suffix))
       move(upload_file, self._path+self._suffix)
       command = [self._rclone_path, 'copy', '--config={}'.format(self.macaroon),
                  self._path+self._suffix, '{}:'.format(self.macaroon_head)]
       _upload_file = subprocess.Popen(command,
               stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
       return self._communicate(_upload_file, GSIUploadError)


