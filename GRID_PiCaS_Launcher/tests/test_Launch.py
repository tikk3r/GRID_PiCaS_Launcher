import unittest
from GRID_PiCaS_Launcher import get_picas_credentials as gpc
from GRID_PiCaS_Launcher.get_token_field import get_token_field
from GRID_PiCaS_Launcher.set_token_field import set_token_field
from GRID_PiCaS_Launcher.update_token_status import update_status
import os,sys
from time import sleep
from GRID_PiCaS_Launcher  import couchdb
from GRID_PiCaS_Launcher.tok_to_bash import export_tok_keys

from GRID_PiCaS_Launcher.picas.actors import RunActor
from GRID_PiCaS_Launcher.picas.clients import CouchClient
from GRID_PiCaS_Launcher.picas.iterators import BasicViewIterator
from GRID_PiCaS_Launcher.picas.modifiers import BasicTokenModifier
from GRID_PiCaS_Launcher.picas.modifiers import NestedTokenModifier
from GRID_PiCaS_Launcher.picas.executers import execute

from Launch import ExampleActor

class TestActor(RunActor):
    def __init__(self, iterator, modifier):
        self.iterator = iterator
        self.modifier = modifier
        self.client = iterator.client

    def process_token(self, key, token):
        raise Exception(key,token)
        

class Launchtest(unittest.TestCase):

    def setUp(self):
        vers=str(sys.version_info[0])+"."+str(sys.version_info[1])
        if vers == '2.6':
            vers = '2.6.0'
        self.t_type="travis_ci_test"+vers
        pc=gpc.picas_cred()
        creds=pc.return_credentials()
        self.usr=creds['user']
        self.pwd=creds['password']
        self.dbn="sksp_unittest"
        sys.argv=["dummy", self.dbn,self.usr,self.pwd]
        self.token="travis_getSBX_test"+vers
        server = couchdb.Server("https://picas-lofar.grid.surfsara.nl:6984")
        self.client = CouchClient(url="https://picas-lofar.grid.surfsara.nl:6984", db=self.dbn, username=self.usr, password=self.pwd)
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
        update_status(self.dbn, self.usr, self.pwd, self.token, 'todo')
        set_token_field(self.token,'SBXloc','https://home.strw.leidenuniv.nl/~apmechev/sandbox_travis.tar',self.dbn,self.usr,self.pwd)
        self.modifier = BasicTokenModifier()
        iterator = BasicViewIterator(self.client, self.token+"/todo", self.modifier)
        self.TestActor = TestActor(iterator, self.modifier)
        self.Ex=ExampleActor(iterator, self.modifier)
        self.nestedmodifier = NestedTokenModifier()

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
        self.client.modify_token(self.modifier.add_output(self.db[self.token],{'output':0}))
        self.assertTrue(get_token_field(self.token,'output',self.dbn,self.usr,self.pwd)==0)
        set_token_field(self.token,'string1','1234',self.dbn,self.usr,self.pwd)
        self.find_and_delete("png")
        self.client.modify_token(self.modifier.unlock(self.db[self.token]))
        self.client.modify_token(self.modifier.unclose(self.db[self.token]))
        update_status(self.dbn, self.usr, self.pwd, self.token, 'done')
        

    def test_lock_token(self):
        self.assertTrue(get_token_field(self.token,'lock',self.dbn,self.usr,self.pwd)==0)
        try:
            self.TestActor.run() 
        except Exception as e:
            self.assertTrue(e.args[0]==self.token)
            self.key=e.args[0]
            self.tok=e.args[1]
        self.assertTrue(get_token_field(self.token,'lock',self.dbn,self.usr,self.pwd)>0)
        set_token_field(self.token,'lock',0,self.dbn,self.usr,self.pwd)
        self.nestedmodifier.lock(self.token, self.client.db)
        self.assertTrue(get_token_field(self.token,'lock',self.dbn,self.usr,self.pwd)>0)
        self.nestedmodifier.unlock(self.token, self.client.db)
        self.assertTrue(get_token_field(self.token,'lock',self.dbn,self.usr,self.pwd)==0)
        self.nestedmodifier.close(self.token, self.client.db)
        self.assertTrue(get_token_field(self.token,'done',self.dbn,self.usr,self.pwd)>0)
        self.nestedmodifier.add_output(self.token, self.client.db, 12)
        self.assertTrue(get_token_field(self.token,'output',self.dbn,self.usr,self.pwd)==12)
        self.nestedmodifier.set_error(self.token, self.client.db)
        self.assertTrue(get_token_field(self.token,'done',self.dbn,self.usr,self.pwd)==-1)
        self.assertTrue(get_token_field(self.token,'lock',self.dbn,self.usr,self.pwd)==-1)
        self.nestedmodifier.unclose(self.token, self.client.db)
        self.assertTrue(get_token_field(self.token,'done',self.dbn,self.usr,self.pwd)==0)

    def test_failed_sbx(self):
        set_token_field(self.token,'SBXloc','ftp://ftp.strw.leidenuniv.nl/pub/apmechev/travis_ci_tests/sanddbox_travis.tar',self.dbn,self.usr,self.pwd) 
        tok=self.db[self.token]
        try:
            self.Ex.process_token(self.token,tok) 
        except Exception as e:
            self.assertTrue(str(e)=='Sandbox failed to download!')

    def test_missing_tokvar(self): 
        from GRID_PiCaS_Launcher.tok_to_bash import  export_tok_keys
        try:
            export_tok_keys('xtokvar.json',{'_id':self.token})
        except Exception as e:
            self.assertTrue('tokvar read error'  in str(e))
            self.assertTrue(get_token_field(self.token,'output',self.dbn,self.usr,self.pwd)==-2)

    def test_failed_sbx(self):
        tok=self.db[self.token]
        _=tok.pop('string1')
        self.db.update([tok])
        try:
            self.Ex.process_token(self.token,tok)
        except Exception as e:
            print(str(e))

    def test_scrub(self): 
        scrubs = get_token_field(self.token,'scrub_count',self.dbn,self.usr,self.pwd)
        self.client.modify_token(self.modifier.scrub(self.db[self.token]))
        self.assertTrue(scrubs+1 == int(get_token_field(self.token,'scrub_count',self.dbn,self.usr,self.pwd)))
        _ = self.nestedmodifier.scrub(self.token, self.client.db)
        self.assertTrue(scrubs+2 == int(get_token_field(self.token,'scrub_count',self.dbn,self.usr,self.pwd)))
        
        set_token_field(self.token,'scrub_count',scrubs,self.dbn,self.usr,self.pwd)

    def test_uploadpng(self):
        self.Ex.database = 'sksp_unittest'
        self.Ex.user = self.usr
        self.Ex.password = self.pwd
        self.Ex.run() 
        for att in self.db[self.token]['_attachments']:
            if "png" in att:
                return
        raise Exception("test.png was not attached to the Token!")
