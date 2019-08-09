#!/bin/env python 
from GRID_PiCaS_Launcher.get_token_field import get_token_field
from GRID_PiCaS_Launcher.get_picas_credentials import PicasCred
import os
import sys
import subprocess
from GRID_PiCaS_Launcher.upload_results import uploader, GSIUploader

token = os.environ["TOKEN"]

pc = PicasCred()
upload_data = get_token_field(token, 'upload', pc)
context = get_token_field(token, 'config.json', pc)
if not upload_data:
    sys.exit()
context['upload'] = upload_data
uberftp_exists = subprocess.Popen(['which','uberftp'], stdout=subprocess.PIPE).communicate()[0]

if uberftp_exists:
    results_uploader = GSIUploader(context)
else:
    results_uploader = uploader(context)

results_uploader.upload()
