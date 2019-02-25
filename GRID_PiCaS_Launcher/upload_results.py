from GRID_PiCaS_Launcher  import couchdb
import os
import sys
import time
import subprocess
from GRID_PiCaS_Launcher.picas.clients import CouchClient

from datetime import datetime                                                                                                               
import json



def export_date_to_env(json_data):
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
    def __init__(self, message, errors, return_code):
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

    def _check_valid_location(self, location):
        raise NotImplementedError("Implement this for concrete uploader")

    def _ls_file(self,file_uri):
        raise NotImplementedError("Implement this for concrete uploader")

    def upload(self,src, dest):
        raise NotImplementedError("Implement this for concrete uploader")

    def delete(self,location):
        raise NotImplementedError("Implement this for concrete uploader")


class GSIUploader(uploader):
    def __init__(self):
        _uberftp_result = subprocess.call(['which','uberftp'])
        _globus_result = subprocess.call(['which','globus-url-copy'])
        if _uberftp_result !=0 or _globus_result !=0:
            raise RuntimeError("Either uberftp or globus-url-copy are not installed")

    def _ls_file(self, file_uri):
        _file_loc = subprocess.Popen(['uberftp','-ls',file_uri], stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        out, err= _file_loc.communicate()
        if not err:
            return out
        
