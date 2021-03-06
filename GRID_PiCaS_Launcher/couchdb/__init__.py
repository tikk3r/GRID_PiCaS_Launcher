# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Christopher Lenz
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from GRID_PiCaS_Launcher.couchdb.client import Database, Document, Server
from GRID_PiCaS_Launcher.couchdb.http import HTTPError, PreconditionFailed, Resource, \
        ResourceConflict, ResourceNotFound, ServerError, Session, Unauthorized
import warnings


warnings.filterwarnings('ignore', category=UserWarning, append=True)
try:
    __version__ = __import__('pkg_resources').get_distribution('CouchDB').version
except:
    __version__ = '?'

warnings.resetwarnings()
