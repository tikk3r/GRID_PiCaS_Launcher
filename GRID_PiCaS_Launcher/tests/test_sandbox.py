import unittest
from GRID_PiCaS_Launcher.sandbox import Sandbox
from GRID_PiCaS_Launcher.sandbox import SandboxWgetDownloader
import os
import shutil

import GRID_PiCaS_Launcher
BASE_DIR = GRID_PiCaS_Launcher.__file__.split('__init__')[0]
DUMMY_CONFIG = BASE_DIR+"/tests/sandbox.json"
#TODO: confirm that the branch and commit are correct using internal function

class testSandbox(unittest.TestCase):
        _multiprocess_can_split_ = True

        def setUp(self):
            os.chdir(BASE_DIR+"/..")
            self.base_dir = BASE_DIR+"/.."

        def test_checkout_commit(self):
            pre_run_dir = os.getcwd()
            s=Sandbox(config_file=DUMMY_CONFIG)
            s._pull_git_repository(repo_location='https://github.com/apmechev/GRID_Sandbox.git',
                    repo_branch='prefactor', 
                    repo_commit='4df7866', 
                    checkout_dir='test_sbx')
            self.assertTrue(os.getcwd() == pre_run_dir)
            self.assertTrue(os.path.isdir(os.getcwd()+"/test_sbx"))
            self.assertTrue(os.path.exists(os.getcwd()+"/test_sbx/.git"))
            shutil.rmtree(pre_run_dir+"/test_sbx")

        def test_checkout_branch(self):
            pre_run_dir = os.getcwd()
            s=Sandbox(config_file=DUMMY_CONFIG)
            s._pull_git_repository(repo_location='https://github.com/apmechev/GRID_Sandbox.git',
                    repo_branch='prefactor',
                    checkout_dir='test_sbx3')
            self.assertTrue(os.getcwd() == pre_run_dir)
            self.assertTrue(os.path.isdir(pre_run_dir+"/test_sbx3"))
            print(os.listdir((pre_run_dir+"/test_sbx3")))
            print(os.getcwd())
            self.assertTrue(os.path.exists(pre_run_dir+"/test_sbx3/.git"))
            shutil.rmtree(pre_run_dir+"/test_sbx3")

        def test_checkout_master(self):
            pre_run_dir = os.getcwd()
            s=Sandbox(config_file=DUMMY_CONFIG)
            s._pull_git_repository(repo_location='https://github.com/apmechev/GRID_Sandbox.git',
                    checkout_dir='test_sbx2')
            self.assertTrue(os.getcwd() == pre_run_dir)
            self.assertTrue(os.path.isdir(pre_run_dir+"/test_sbx2"))
            print(os.listdir((pre_run_dir+"/test_sbx2")))
            print(os.getcwd())     
            self.assertTrue(os.path.exists(pre_run_dir+"/test_sbx2/.git"))
            shutil.rmtree(pre_run_dir+"/test_sbx2")
           
        def test_checkout_cwd(self):
            #We need to make a directory since otherwise it kills the GRID_PiCaS_Launcher .git folder
            os.mkdir("testcwd")
            os.chdir('testcwd')
            s=Sandbox(config_file=DUMMY_CONFIG)
            s._pull_git_repository(repo_location='https://github.com/apmechev/GRID_Sandbox.git',
                    remove_gitdir=True)
            self.assertTrue(not os.path.exists('.git'))
            os.chdir('..')
            shutil.rmtree("testcwd")

class testSandboxDownloader(unittest.TestCase):

    def test_https_download(self):
        os.mkdir("test_dl_https")
        os.chdir("test_dl_https")
        s_dl = SandboxWgetDownloader(location='https://home.strw.leidenuniv.nl/~apmechev/sandbox_travis.tar')
        s_dl.download()
        s_dl.check_download()
        s_dl.extract_sandbox()
        s_dl.remove_download_file()
        self.assertTrue('downloaded_sandbox.tar' not in os.listdir(os.getcwd()))
        self.assertTrue('master.sh' in os.listdir(os.getcwd()))
        os.chdir('..')
#        shutil.rmtree('test_dl_https')

class testSandboxBuilder(unittest.TestCase):

    def test_build_master(self):
        cfgfile = BASE_DIR+'/tests/sandbox.json'
        sbx = Sandbox(config_file=cfgfile)
        sbx.build_sandbox()
        assert 'master.sh' in os.listdir(os.getcwd())
