import subprocess
import os
import shutil 

class Sandbox(object):
    """A class that builds the sandbox from a json file, or 
    alternatively downloads it"""

    def __init__(self,config_file=None, location=None):
        if config_file:
            self.config_file = config_file
        elif location:
            self.location = location 
        else:
            raise RuntimeError("Neither configuration file nor location supplied")


    def build_sandbox(self):
        cfg_file = self.config_file
        
    @staticmethod
    def _pull_git_repository(repo_location=None, repo_branch='master', repo_commit=None,
                             checkout_dir=None):
        """Internal function that checks out a specific commit or branch of a 
        repository. By default it does so in the current directory. """
        if not checkout_dir:
            checkout_dir = os.getcwd()
        else:
            return_dir = os.getcwd()
        if not repo_location:
            raise RuntimeError("No repository to cone!!")
        clone = subprocess.Popen(
                    ['git', 'clone', repo_location, checkout_dir])
        clone.wait()
        os.chdir(checkout_dir)
        checkout = subprocess.Popen(['git', 'checkout', repo_branch])
        checkout.wait()
        if repo_commit:
            checkout = subprocess.Popen(['git', 'checkout', repo_commit])
            checkout.wait()
        shutil.rmtree('.git/')
        os.chdir(return_dir)

    def download_sandbox(self,command,location):
        if os.path.isfile("sandbox.tar"): os.remove("sandbox.tar")
        if command=='globus-url-copy':
            subprocess.call([command, location, "sandbox.tar"])
        elif command=='wget':
            subprocess.call([command, location, '-T','30','-t','10', "-O",'sandbox.tar'])
        if os.stat("sandbox.tar").st_size == 0: 
            set_token_field(self.token_name,'output',-2,self.p_db,self.p_usr,self.p_pwd)
            set_token_field(self.token_name,'done',time.time(),self.p_db,self.p_usr,self.p_pwd)
            raise Exception("Sandbox failed to download!")


