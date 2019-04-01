# -*- coding: utf-8 -*-
import os
import sys
from app import app
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


dev_db = prefix + os.path.join(app.root_path, 'data.db')

SQLALCHEMY_DATABASE_URI = dev_db
SQLALCHEMY_TRACK_MODIFICATIONS = False