from subprocess import Popen
import sys

class SafePopen(object):                                                                                         
    def __init__(self, *popen_args, **popen_kwargs):
        if sys.version_info.major ==2:
            return Popen.__init__(*popen_args, **popen_kwargs)
        if sys.version_info.major == 3 : 
            popen_kwargs['encoding'] = 'utf8'
        return Popen.__init__(*popen_args, **popen_kwargs)

