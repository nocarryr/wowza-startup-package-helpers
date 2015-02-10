import os
import shutil

from wowza_startup_package_helpers.config_scripts.base_script import BaseScript

class BaseApp(BaseScript):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', self.__class__.__name__)
    def prepare_dirs(self):
        app_dir = self.build_filename('applications', self.name)
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)
        conf_root = self.build_filename('conf')
        conf_dir = self.build_filename('conf', self.name)
        if not os.path.exists(conf_dir):
            os.makedirs(conf_dir)
        if os.path.exists(os.path.join(conf_dir, 'Application.xml')):
            return
        shutil.copy(os.path.join(conf_root, 'Application.xml'), conf_dir)
    def __call__(self):
        self.prepare_dirs()
