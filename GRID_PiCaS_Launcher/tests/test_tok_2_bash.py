import unittest
from GRID_PiCaS_Launcher import get_picas_credentials as gpc
from get_token_field import get_token_field
from set_token_field import set_token_field
import os
from time import sleep
from GRID_PiCaS_Launcher import couchdb
from tok_to_bash import export_tok_keys
import sys

class tok2bashtest(unittest.TestCase):

    def setUp(self):
        vers=str(sys.version_info[0])+"."+str(sys.version_info[1])
        self.token_id='travis_getSBX_test'+vers
        pc=gpc.picas_cred()
        creds=pc.return_credentials()  
        self.usr=creds['user']
        self.pwd=creds['password']
        self.dbn=str('sksp_unittest')
        self.test_tokvarile='GRID_PiCaS_Launcher/tests/test_tok_var.cfg'
        server = couchdb.Server("https://picas-lofar.grid.sara.nl:6984")
        server.resource.credentials = (self.usr,self.pwd)
        self.db= server[self.dbn]
        with open(self.test_tokvarile,'w') as f:
            f.write('string1: $STRING1'+'\n')
            f.write('_id: $TOKEN'+'\n')
            f.write("'_attachments':"+'\n')
            f.write('     test_attachment: test_attachment'+'\n')
            f.write('     test_attachment2: $ATTACH'+'\n')
            f.write('integer1: $INT1'+'\n')
        set_token_field(self.token_id,'string1','test_string',self.dbn,self.usr,self.pwd)
        set_token_field(self.token_id,'integer1',1234,self.dbn,self.usr,self.pwd)
        if os.path.isfile('test_attachment'): os.remove('test_attachment')

    def travis_safe_upload(self,att,att_tok):
        fail=1
        with open(att,'r') as att_file:
            while(fail==1):
                try:
                    self.db.put_attachment(self.db[self.token_id], att_file,att_tok)
                    fail=0
                except couchdb.http.ResourceConflict:
                    sleep(1)
                    fail=1

    def tearDown(self):
        if os.path.isfile('test_attachment'): os.remove('test_attachment')
        if os.path.isfile('test_attachment2'): os.remove('test_attachment2')
        if os.path.isfile('test1var'):os.remove('test1var')
        if os.path.isfile(self.test_tokvarile):os.remove(self.test_tokvarile)
 
    def test_read_string(self):
        os.environ['TOKEN']=self.token_id
        token=self.db[self.token_id]
        export_tok_keys(self.test_tokvarile,token)
        self.assertTrue(os.environ['STRING1']=='test_string')

    def test_read_int(self):
        os.environ['TOKEN']=self.token_id
        token=self.db[self.token_id]
        export_tok_keys(self.test_tokvarile,token)
        self.assertTrue(os.environ['INT1']=='1234')

    def test_dl_attach(self):
        self.travis_safe_upload('GRID_PiCaS_Launcher/tests/test_attachment.txt', 'test_attachment')
        token=self.db[self.token_id]
        export_tok_keys(self.test_tokvarile,token)
        self.assertTrue(os.path.isfile('test_attachment'))

    def test_dl_attach_var(self):
        self.travis_safe_upload('GRID_PiCaS_Launcher/tests/test_attachment.txt', 'test_attachment2')
        token=self.db[self.token_id]
        export_tok_keys(self.test_tokvarile,token)
        self.assertTrue(os.path.isfile('test_attachment2'))
        self.assertTrue(os.environ.get('ATTACH')!=None)

    def test_wrong_key(self):
        os.environ['TOKEN']=self.token_id
        token=self.db[self.token_id]
        os.system("sed  's\string1\spring1\g' %s >test1var "%(self.test_tokvarile) ) 
        export_tok_keys('test1var',token)
         

