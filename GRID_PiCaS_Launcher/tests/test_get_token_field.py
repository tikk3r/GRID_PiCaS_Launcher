import unittest
from GRID_PiCaS_Launcher import get_picas_credentials as gpc
from GRID_PiCaS_Launcher import get_token_field
import os
from time import sleep
from GRID_PiCaS_Launcher import couchdb
from GRID_PiCaS_Launcher.tok_to_bash import export_tok_keys
import sys
import subprocess

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

    def test_get_value(self):
        val1 = get_token_field.main(self.dbn,
                                    self.usr, self.pwd, self.token_id,'integer1')
        os.environ['PICAS_USR'] = self.usr
        os.environ['PICAS_USR_PWD'] = self.pwd
        os.environ['PICAS_DB'] = self.dbn
        val2 = get_token_field.main(self.token_id,'integer1')
        self.assertTrue(val1 == val2)

