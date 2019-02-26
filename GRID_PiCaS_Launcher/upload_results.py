from GRID_PiCaS_Launcher  import couchdb
import os
import sys
import time
import tarfile
import subprocess
from GRID_PiCaS_Launcher.picas.clients import CouchClient

from datetime import datetime                                                                                                               
import json



def get_date(json_data):
    upload = json_data.get('upload')

    if not upload or not upload.get('add_date'):
        return ""
    H, M = "", ""

    if upload.get('add_hour'):
        H="_%H:"
        if upload.get('add_minute'):
            M="%M"
        else:
            M="00"
    else:
        M=""

    now=datetime.now()
    formatted_date = now.strftime("%Y-%m-%d{0}{1}".format(H,M))
    return formatted_date



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
    def __init__(self):
        pass

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
        with tarfile.open('upload.tar.gz', mode='w:gz') as archive:
                archive.add(os.getcwd(), recursive=True, arcname='')
        return "{0}/{1}".format(os.getcwd(),"upload.tar.gz")

    def tarball(self):
        with tarfile.open('upload.tar', mode='w') as archive:
                archive.add(os.getcwd(), recursive=True, arcname='')
        return "{0}/{1}".format(os.getcwd(),  "upload.tar")             
    
    def _upload(self):
        raise NotImplementedError("Implement this for concrete uploader")

class GSIUploader(uploader):
    def __init__(self, context):
        """Gets the 'upload' Dict as context and uploads file to GSIFTP location"""
        if 'upload' in context:
            context = context['upload']
        self.context = context
        _uberftp_result = subprocess.call(['which','uberftp'])
        _globus_result = subprocess.call(['which','globus-url-copy'])
        self._date = get_date(self.context)

        self._path= "{0}/{1}".format(self.context['location'], self.context['template'])
        if _uberftp_result !=0 or _globus_result !=0:
            raise RuntimeError("Either uberftp or globus-url-copy are not installed")
        self.upload()
        
    def _upload(self, upload_file):
        if self.context.get('overwrite'):
            command = ['globus-url-copy', '-sync', '-sync-level', '3', upload_file, self._path]
        else:
            command = ['globus-url-copy',upload_file, self._path]
        _upload_file = subprocess.Popen(command,
                                        stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        return self._communicate(_upload_file, GSIUploadError)
        

