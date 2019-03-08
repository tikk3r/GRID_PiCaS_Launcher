#!/bin/env python 
from GRID_PiCaS_Launcher.get_token_field import get_token_field
from GRID_PiCaS_Launcher.get_picas_credentials import picas_cred
import os

token = os.environ["TOKEN"]

pc = picas_cred()
upload_data = get_token_field(token, 'upload', pc.database, pc.user,  pc.password)
uberftp_exists = subprocess.Popen(['which','uberftp'], stdout=subprocess.PIPE).communicate()[0]
if uberftp_exists:
    results_uploader = GSIUploader(upload_data)
else:
    results_uploader = uploader(upload_data)
results_uploader.upload()    
