import unittest
from GRID_PiCaS_Launcher import get_picas_credentials as pc
import os
from os.path import expanduser

class getcredstest(unittest.TestCase):
    
    def setUp(self):
        ##Saves the original credentials
        if os.environ['PICAS_USR']!="":
            self.orig_dest='env'
            self.orig_pc=pc.PicasCred(usr=os.environ['PICAS_USR'],pwd=os.environ['PICAS_USR_PWD'],dbn=os.environ['PICAS_DB'])
        else:
            self.orig_pc=pc.PicasCred(source='~/.picasrc')
            self.orig_dest='file'
        self.d_usr="dummy"
        self.d_pwd="dammy"
        self.d_dbn="dommy"
          
    def tearDown(self):
        #restores original credentials
        if self.orig_dest=='file':
            self.orig_pc.put_creds_in_file()
        else:
            self.orig_pc.put_picas_creds_in_env()

    def test_readenv_vars(self):
        os.environ['PICAS_USR']=self.d_usr
        os.environ['PICAS_USR_PWD']=self.d_pwd
        os.environ['PICAS_DB']=self.d_dbn
        pc1=pc.PicasCred()
        pc1.get_picas_creds_from_env()
        self.assertTrue(pc1.user==self.d_usr)
        self.assertTrue(pc1.password==self.d_pwd)
        self.assertTrue(pc1.database==self.d_dbn)

    def test_readfile_vars(self):
        testfile='~/test_picas'
        with open(expanduser(testfile),'w') as tf:
            tf.write('user='+self.d_usr+"\n")
            tf.write('password='+self.d_pwd+"\n")
            tf.write('database='+self.d_dbn+"\n")
        pc2=pc.PicasCred(source=testfile)
        pc2.get_picas_creds_from_file(testfile)
        self.assertTrue(pc2.user==self.d_usr)
        self.assertTrue(pc2.password==self.d_pwd)
        self.assertTrue(pc2.database==self.d_dbn)

    def test_put_creds_in_env(self):
        os.environ['PICAS_USR']=""
        os.environ['PICAS_USR_PWD']=""
        os.environ['PICAS_DB']=""
        pc2=pc.PicasCred(usr=self.d_usr,pwd=self.d_pwd,dbn=self.d_dbn)
        pc2.put_picas_creds_in_env()       
        self.assertTrue(os.environ['PICAS_USR']==self.d_usr)
        self.assertTrue(os.environ['PICAS_USR_PWD']==self.d_pwd)
        self.assertTrue(os.environ['PICAS_DB']==self.d_dbn)

    def test_put_creds_in_file(self):
        testfile='~/test_picas'
        pc2=pc.PicasCred(usr=self.d_usr,pwd=self.d_pwd,dbn=self.d_dbn)
        pc2.put_creds_in_file(testfile)
        pc3=pc.PicasCred(source=testfile)  
        self.assertTrue(pc3.user==self.d_usr)
        self.assertTrue(pc3.password==self.d_pwd)
        self.assertTrue(pc3.database==self.d_dbn)
        self.orig_pc.put_creds_in_file()

