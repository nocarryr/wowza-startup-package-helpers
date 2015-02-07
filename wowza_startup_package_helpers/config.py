import sys
import os
import traceback
import urllib2
import json

from wowza_startup_package_helpers.logger import logger

WMS_ROOT = '/usr/local/WowzaStreamingEngine'

class Config(object):
    wms_root = WMS_ROOT
    def __init__(self, data=None, **kwargs):
        self.data = {}
        if isinstance(data, dict):
            self.data.update(data)
        for key, val in kwargs.iteritems():
            self.data[key] = val
    def __getitem__(self, key):
        return self.data[key]
    def __setitem__(self, key, item):
        self.data[key] = item
    def get(self, key, default=None):
        return self.data.get(key, default)
    def update(self, d):
        self.data.update(d)
    @classmethod
    def from_json(cls, js_str):
        d = json.loads(js_str)
        return cls(d)
    @classmethod
    def from_file(cls, filename):
        try:
            with open(filename, 'r') as f:
                s = f.read()
        except:
            logger.error(traceback.format_exc())
            logger.error('Config: unable to open file: %s' % (filename))
            sys.exit(0)
        return cls.from_json(s)
    @classmethod
    def from_url(cls, url):
        try:
            u = urllib2.urlopen(url)
            s = u.read()
            u.close()
        except:
            logger.error(traceback.format_exc())
            logger.error('Config: unable to open url: %s' % (url))
            sys.exit(0)
        return cls.from_json(s)
    def __repr__(self):
        return str(self)
    def __str__(self):
        return str(self.data)
    
def build_config():
    paths = [WMS_ROOT, os.getcwd()]
    for p in paths:
        fn = os.path.join(p, 'config_vars.json')
        if os.path.exists(fn):
            return Config.from_file(fn)
        fn = os.path.join(p, 'config_vars.url')
        if os.path.exists(fn):
            return Config.from_url(fn)
    logger.error('Config: no valid config_vars source')
    return Config()
    
config = build_config()
    
