import unittest
import tempfile
import os

from GRID_PiCaS_Launcher.upload_results import uploader



class UploadTest(unittest.TestCase):
    
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix=os.getcwd()+"/")
        
    def test_tar_uploader(self):
        data = {"upload": {
                "add_date": True,
                "add_hour":True,
                "gzip": True,
                "location": "gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/CI",
                "remove_prev": False,
                "template": "CI_pref3_cal_$DATE"

            }}
        try:
            os.environ['RUNDIR']=self.tmpdir
            os.mkdir(self.tmpdir+"/Output")
            self.touch(self.tmpdir+"/Output/a")
            self.touch(self.tmpdir+"/Output/b")
            self.touch(self.tmpdir+"/Output/c")
            self.touch(self.tmpdir+"/Output/d")
            test_uploader = uploader(data)
            self.assertTrue(test_uploader.context.get('add_date'))
            self.assertTrue(test_uploader.context.get('add_hour'))
            self.assertTrue(test_uploader.context.get('gzip'))
            test_uploader.upload()
        except NotImplementedError:
            pass


    @staticmethod
    def _touch(fname, times=None):
        with open(fname, 'a'):
            os.utime(fname, times)

