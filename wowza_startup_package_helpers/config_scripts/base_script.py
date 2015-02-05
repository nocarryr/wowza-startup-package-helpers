import os

from wowza_startup_package_helpers.config import config

class BaseScript(object):
    config = config
    def build_filename(self, *args):
        args = [config.wms_root] + list(args)
        return os.path.join(*args)
    def build_conf_filename(self, *args):
        args = ['conf'] + list(args)
        return self.build_filename(*args)
    def write_to_file(self, s, *args):
        filename = self.build_filename(*args)
        with open(filename, 'w') as f:
            f.write(s)
    def __call__(self):
        pass
        
