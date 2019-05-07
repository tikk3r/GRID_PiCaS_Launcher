import unittest                                                                                                                             
from GRID_PiCaS_Launcher.singularity import download_singularity_from_env, parse_singularity_link, download_simg_from_gsiftp, pull_image_from_shub, put_variables_in_env, get_image_file_hash, HiddenPrints
import os
import sys
import logging
import json
import GRID_PiCaS_Launcher
from contextlib import contextmanager
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


BASE_DIR = GRID_PiCaS_Launcher.__file__.split('__init__')[0]
DUMMY_CONFIG = BASE_DIR+"/tests/cal_pref3_v1.0.json"
#TODO: confirm that the branch and commit are correct using internal function

@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class testsingularity(unittest.TestCase):

    def test_all(self):
        config = json.load(open(DUMMY_CONFIG))
        put_variables_in_env(config)
        self.assertTrue(os.environ['SIMG'] == config['container']['singularity']['SIMG'])
        self.assertTrue(os.environ['SIMG_COMMIT'] == config['container']['singularity']['SIMG_COMMIT'])
        put_variables_in_env(config['container'])
        self.assertTrue(os.environ['SIMG'] == config['container']['singularity']['SIMG'])
        self.assertTrue(os.environ['SIMG_COMMIT'] == config['container']['singularity']['SIMG_COMMIT'])
        put_variables_in_env(config['container']['singularity'])
        self.assertTrue(os.environ['SIMG'] == config['container']['singularity']['SIMG'])
        self.assertTrue(os.environ['SIMG_COMMIT'] == config['container']['singularity']['SIMG_COMMIT'])
        out = download_singularity_from_env()
        self.assertTrue('tikk3r-lofar-grid-hpccloud-master-lofar.simg' in out) 
        del os.environ['SIMG_COMMIT']
        out = download_singularity_from_env()
        self.assertTrue('tikk3r-lofar-grid-hpccloud-master-lofar.simg' in out)
        del os.environ['SIMG']
        try:
            download_singularity_from_env()
        except RuntimeError as e:
            self.assertTrue(str(e) == "NO $SIMG in Environment!")

    def test_badJson(self):
        badjson={}
        try:
            put_variables_in_env(badjson)
        except RuntimeError as e:
            self.assertTrue(str(e) == "Could not find SIMG in {}")

    def test_silent_print(self):
        logging.getLogger().setLevel(logging.ERROR)
        config = json.load(open(DUMMY_CONFIG))
        put_variables_in_env(config)
        with captured_output() as output:
            outfile = download_singularity_from_env()
        (out, err) = output
        #self.assertTrue(len(out.getvalue().split("\n")) == 2)


        with captured_output() as output:
            with HiddenPrints():
                outfile = download_singularity_from_env()
        (out, err) = output
        #self.assertTrue(len(out.getvalue().split("\n"))==1)


