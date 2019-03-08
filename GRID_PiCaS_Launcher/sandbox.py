import subprocess
import os
import shutil 
import json
import tempfile
from multiprocessing import Pool, Process, Manager

class Sandbox(object):
    """A class that builds the sandbox from a json file, or 
    alternatively downloads it"""

    def __init__(self,config_file=None, config_json=None, location=None):
        if config_file:
            self.config = self._get_field_from_cfgfile(config_file)
        elif config_json:
            self.config = config_json
        elif location:
            self.location = location 
        else:
            raise RuntimeError("Neither configuration file nor location supplied")

    @staticmethod
    def _get_field_from_cfgfile(cfg_file):
        """Gets the data from the data file and returns it
        """
        with open(cfg_file,'r') as _f:
           data = json.load(_f)
        if 'sandbox' in data.keys():
            return data['sandbox']
        return data

    def build_sandbox(self, remove_gitdir=False):
        cfg = self.config
        if 'git' in cfg.keys():
            repo_branch = None
            repo_commit = None
            repo_loc = cfg['git']['url']
            checkout_dir = cfg['git'].get('checkout_dir', None)
            if 'branch' in cfg['git'].keys():
                repo_branch = cfg['git']['branch']
            if 'commit' in cfg['git']:
                repo_commit = cfg['git']['commit']
            kwargs = {'repo_location':repo_loc, 'repo_branch':repo_branch, 'repo_commit':repo_commit, 'checkout_dir':checkout_dir,
                     'remove_gitdir':remove_gitdir}
            p = Process(target=self._pull_git_repository, kwargs=kwargs)
            p.start()
            p.join()
#            self._pull_git_repository(repo_location=repo_loc, repo_branch=repo_branch,
#                    repo_commit=repo_commit, checkout_dir=checkout_dir)
        if 'scripts' in cfg.keys():
            for script in cfg['scripts']:
                script_cfg = cfg['scripts'][script.keys()[0]]
                repo_loc = script_cfg['url']
                repo_branch = script_cfg.get('branch', None)
                repo_commit = script_cfg.get('commit', None)
                checkout_dir = script_cfg.get('checkout_dir', None)
                kwargs = {'repo_location':repo_loc, 'repo_branch':repo_branch, 'repo_commit':repo_commit, 'checkout_dir':checkout_dir}
                p = Process(target=self._pull_git_repository, kwargs=kwargs)
                p.start()
                p.join()

    @staticmethod
    def _pull_git_repository(repo_location=None, repo_branch=None, repo_commit=None,
                             checkout_dir=None, remove_gitdir=False):
        """Internal function that checks out a specific commit or branch of a 
        repository. By default it does so in the current directory. """
        if not checkout_dir:
            return_dir = os.getcwd()
            checkout_dir_path = tempfile.mkdtemp(prefix=os.getcwd()+'/')
        else:
            return_dir = os.getcwd()
            checkout_dir_path = checkout_dir
        if not repo_location:
            raise RuntimeError("No repository to cone!!")
        with open(os.devnull, 'w') as FNULL:
            clone = subprocess.Popen(
                        ['git', 'clone', repo_location, checkout_dir_path],
                        stdout=FNULL, stderr=subprocess.STDOUT)
            clone.wait()
        os.chdir(checkout_dir_path)
        if repo_branch:
            checkout = subprocess.Popen(['git', 'checkout', repo_branch])
            checkout.communicate()
        if repo_commit:
            checkout = subprocess.Popen(['git', 'checkout', repo_commit])
            checkout.communicate()
        if remove_gitdir and os.path.isdir('.git'):
            shutil.rmtree('.git/')
        if not checkout_dir:
            files = os.listdir(checkout_dir_path)
            copy_src = checkout_dir_path+"/*"
#            shutil.copytree(checkout_dir_path, return_dir)
            subprocess.Popen("cp -r {0} {1}".format(copy_src, return_dir),shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
#            print(shell_copy.communicate())
#           out = subprocess.check_output(["cp", "-r", copy_src, return_dir],stderr=subprocess.STDOUT)
#           print(out)
#            for f in files:
#                src = os.path.join(checkout_dir_path, f)
#                dest = os.path.join(return_dir,f)
#                shutil.copy(src, dest)
        os.chdir(return_dir)
    
    @staticmethod
    def _do_download(downloader):
        downloader.download()
        downloader.check_download()
        downloader.extract_sandbox()
        downloader.remove_download_file()

    def download_sandbox(self,location=None):
        if not location:
            location = self.location
        if 'gsiftp' in location:
            self._do_download(SandboxGSIDownloader(location))
        elif 'http' in location or 'ftp' in location:
            self._do_download(SandboxWgetDownloader(location))


class SandboxDownloader(object):
    def __init__(self,location):
        self.location = location
        self.download_file = 'downloaded_sandbox'

    def download(self):
        raise NotImplementedError("Do not use this (Abstract) Class")

    def check_download(self):
        extension = self._get_sandbox_extension()
        if os.stat(self.download_file+extension).st_size == 0:
            raise ValueError("Sandbox could not be downloaded from {0}{1}"
                            .format(self.location,extension))

    def _extract_tar(self):
        ex = subprocess.Popen(['tar','-xf',self.download_file+'.tar'])
        ex.communicate()

    def _extract_tar_gz(self):
        ex = subprocess.Popen(['tar','-zxf',self.download_file+'.tar.gz'])
        ex.communicate()

    def _get_sandbox_extension(self):
        extension = ".{0}".format(self.location.split('.')[-1])
        return extension

    def _extract_zip(self):
         ex = subprocess.Popen(['unzip',self.download_file+'.zip'])
         ex.communicate()

    def extract_sandbox(self):
        extension = self._get_sandbox_extension()
        if extension == '.tar':
            self._extract_tar()
        if extension == '.tar.gz':
            self._extract_tar_gz()
        if extension == '.zip':
            self._extract_zip()
    
    def remove_download_file(self):
        extension = self._get_sandbox_extension()
        os.remove(self.download_file+extension)

class SandboxGSIDownloader(SandboxDownloader):
    def __init__(self,location):
        super(SandboxGSIDownloader, self).__init__(location)

    def download(self):
        extension = self._get_sandbox_extension()
        subprocess.call(['globus-url-copy', self.location,
            "{0}{1}".format(self.download_file, extension)])

class SandboxWgetDownloader(SandboxDownloader):
    def __init__(self,location):
        super(SandboxWgetDownloader, self).__init__(location)

    def download(self):
        extension = self._get_sandbox_extension()
        subprocess.call(['wget', "-O",
            "{0}{1}".format(self.download_file, extension),
            self.location])
