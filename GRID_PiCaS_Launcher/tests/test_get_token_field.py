import unittest
from GRID_PiCaS_Launcher import get_picas_credentials as gpc
from GRID_PiCaS_Launcher.get_token_field import get_token_field
from GRID_PiCaS_Launcher.set_token_field import set_token_field
import os
from time import sleep
from GRID_PiCaS_Launcher import couchdb
from GRID_PiCaS_Launcher.tok_to_bash import export_tok_keys
import sys

class getfieldtest(unittest.TestCase):

    def setUp(self):
        vers=str(sys.version_info[0])+"."+str(sys.version_info[1])
        if vers == '2.6':
            vers = '2.6.0'
        self.token_id='travis_getSBX_test'+vers
        pc=gpc.picas_cred()
        creds=pc.return_credentials()  
        self.usr=creds['user']
        self.pwd=creds['password']
        self.dbn=str('sksp_unittest')
        server = couchdb.Server("https://picas-lofar.grid.surfsara.nl:6984")
        server.resource.credentials = (self.usr,self.pwd)

    def tearDown(self):
        if os.path.isfile('test_attachment'): os.remove('test_attachment')
        if os.path.isfile('test_attachment2'): os.remove('test_attachment2')
        if os.path.isfile('test1var'):os.remove('test1var')
        if os.path.isfile(self.test_tokvarile):os.remove(self.test_tokvarile)
 
    def test_get_value(self):
        val1 = subprocess.call(['python','GRID_PiCaS_Launcher/get_token_field.py',self.dbn,
                                self.usr, self.pwd, self.token_id,'integer1' ])
        os.environ['PICAS_USR'] = self.usr
        os.environ['PICAS_USR_PWD'] = self.pwd
        os.environ['PICAS_DB'] = self.dbn
        val2 = subprocess.call(['python','GRID_PiCaS_Launcher/get_token_field.py',
            self.token_id,'integer1'])
        self.assertTrue(val1 == val2)

