import unittest
import get_picas_credentials as gpc
from get_token_field import get_token_field
from set_token_field import set_token_field
import os,sys
from time import sleep
import couchdb
from tok_to_bash import export_tok_keys

from picas.actors import RunActor
from picas.clients import CouchClient
from picas.iterators import BasicViewIterator
from picas.modifiers import BasicTokenModifier
from picas.executers import execute

from getSBX import ExampleActor

class TestActor(RunActor):
    def __init__(self, iterator, modifier):
        self.iterator = iterator
        self.modifier = modifier
        self.client = iterator.client

    def process_token(self, key, token):
        raise Exception(key,token)
        

class getSBXtest(unittest.TestCase):

    def setUp(self):
        vers=str(sys.version_info[0])+"."+str(sys.version_info[1])
        self.t_type="travis_ci_test"+vers
        token="travis_getSBX_test"+vers
        pc=gpc.picas_cred()
        creds=pc.return_credentials()
        self.usr=creds['user']
        self.pwd=creds['password']
        self.dbn="sksp_unittest"
        sys.argv=["dummy", self.dbn,self.usr,self.pwd]
        self.token="travis_getSBX_test"+vers
        server = couchdb.Server("https://picas-lofar.grid.sara.nl:6984")
        self.client = CouchClient(url="https://picas-lofar.grid.sara.nl:6984", db=self.dbn, username=self.usr, password=self.pwd)
        server.resource.credentials = (self.usr,self.pwd)
        self.db= server[self.dbn]
        tok={'type':self.token}
        vers=".".join([str(i) for i in sys.version_info])
        tok['_id']=self.token
        if '_attachments' in tok.keys():
            _=tok.pop("_attachments")
        self.db.update([tok])
        set_token_field(self.token,'lock',0,self.dbn,self.usr,self.pwd)
        set_token_field(self.token,'string1','1234',self.dbn,self.usr,self.pwd)
        set_token_field(self.token,'done',0,self.dbn,self.usr,self.pwd)
        set_token_field(self.token,'status','todo',self.dbn,self.usr,self.pwd)
        set_token_field(self.token,'SBXloc','ftp://ftp.strw.leidenuniv.nl/pub/apmechev/travis_ci_tests/sandbox_travis.tar',self.dbn,self.usr,self.pwd)
        modifier = BasicTokenModifier()
        iterator = BasicViewIterator(self.client, self.token+"/todo", modifier)
        self.TestActor = TestActor(iterator, modifier)
        self.Ex=ExampleActor(iterator, modifier)

    def travis_safe_upload(self,att,att_tok):
        fail=1
        with open(att,'r') as att_file:
            while(fail==1):
                try:
                    self.db.put_attachment(self.db[self.token], att_file,att_tok)
                    fail=0
                except couchdb.http.ResourceConflict:
                    sleep(1)
                    fail=1

    def find_and_delete(self,string):
        for att in self.db[self.token]['_attachments']:
            if string in att:
                self.db.delete_attachment(self.db[self.token],att)

    def tearDown(self):
        set_token_field(self.token,'lock',0,self.dbn,self.usr,self.pwd)
        set_token_field(self.token,'done',0,self.dbn,self.usr,self.pwd)
        set_token_field(self.token,'status','todo',self.dbn,self.usr,self.pwd)
        set_token_field(self.token,'hostname','',self.dbn,self.usr,self.pwd)
        set_token_field(self.token,'output',0,self.dbn,self.usr,self.pwd)
        set_token_field(self.token,'string1','1234',self.dbn,self.usr,self.pwd)
        self.find_and_delete("png")

    def test_lock_token(self):
        self.assertTrue(get_token_field(self.token,'lock',self.dbn,self.usr,self.pwd)==0)
        try:
            self.TestActor.run() 
        except Exception as e:
            self.assertTrue(e.args[0]==self.token)
            self.key=e.args[0]
            self.tok=e.args[1]
        self.assertTrue(get_token_field(self.token,'lock',self.dbn,self.usr,self.pwd)>0)

    def test_failed_sbx(self):
        set_token_field(self.token,'SBXloc','ftp://ftp.strw.leidenuniv.nl/pub/apmechev/travis_ci_tests/sanddbox_travis.tar',self.dbn,self.usr,self.pwd) 
        tok=self.db[self.token]
        try:
            self.Ex.process_token(self.token,tok) 
        except Exception as e:
            self.assertTrue(str(e)=='Sandbox failed to download!')

    def test_missing_tokvar(self): 
        from tok_to_bash import  export_tok_keys
        try:
            export_tok_keys('xtokvar.cfg',{'_id':self.token})
        except Exception as e:
            self.assertTrue(str(e)=='tokvar missing')
            self.assertTrue(get_token_field(self.token,'output',self.dbn,self.usr,self.pwd)==-2)

    def test_failed_sbx(self):
        tok=self.db[self.token]
        _=tok.pop('string1')
        self.db.update([tok])
        try:
            self.Ex.process_token(self.token,tok)
        except Exception as e:
            print(str(e))

    def test_uploadpng(self):
        self.Ex.run()
        for att in self.db[self.token]['_attachments']:
            if "png" in att:
                return
        raise Exception("test.png does not exist!")
