import unittest
from GRID_PiCaS_Launcher.sandbox import Sandbox
import os
import shutil

#TODO: confirm that the branch and commit are correct using internal function
class testSandbox(unittest.TestCase):

        def test_checkout_commit(self):
            pre_run_dir = os.getcwd()
            s=Sandbox(config_file='DUMMY_FILE_NAME')
            s._pull_git_repository(repo_location='https://github.com/apmechev/GRID_Sandbox.git',
                    repo_branch='prefactor', 
                    repo_commit='4df7866', 
                    checkout_dir='test_sbx')
            self.assertTrue(os.getcwd() == pre_run_dir)
            self.assertTrue(os.path.isdir(os.getcwd()+"/test_sbx"))
            self.assertFalse(os.path.exists(os.getcwd()+"/test_sbx/.git"))
            shutil.rmtree(os.getcwd()+"/test_sbx")

        def test_checkout_branch(self):
            pre_run_dir = os.getcwd()
            s=Sandbox(config_file='DUMMY_FILE_NAME')
            s._pull_git_repository(repo_location='https://github.com/apmechev/GRID_Sandbox.git',
                    repo_branch='prefactor',
                    checkout_dir='test_sbx3')
            self.assertTrue(os.getcwd() == pre_run_dir)
            self.assertTrue(os.path.isdir(os.getcwd()+"/test_sbx3"))
            self.assertFalse(os.path.exists(os.getcwd()+"/test_sbx3/.git"))
            shutil.rmtree(os.getcwd()+"/test_sbx3")

        def test_checkout_master(self):
            pre_run_dir = os.getcwd()
            s=Sandbox(config_file='DUMMY_FILE')
            s._pull_git_repository(repo_location='https://github.com/apmechev/GRID_Sandbox.git',
                    checkout_dir='test_sbx2')
            self.assertTrue(os.getcwd() == pre_run_dir)
            self.assertTrue(os.path.isdir(os.getcwd()+"/test_sbx2"))
            self.assertFalse(os.path.exists(os.getcwd()+"/test_sbx2/.git"))
            shutil.rmtree(os.getcwd()+"/test_sbx2")
           
        def test_checkout_cwd(self):
            #We need to make a directory since otherwise it kills the GRID_PiCaS_Launcher .git folder
            os.mkdir("testcwd")
            os.chdir('testcwd')
            s=Sandbox(config_file='DUMMY_FILE')
            s._pull_git_repository(repo_location='https://github.com/apmechev/GRID_Sandbox.git')
            self.assertFalse(os.path.exists('.git'))
            os.chdir('..')


