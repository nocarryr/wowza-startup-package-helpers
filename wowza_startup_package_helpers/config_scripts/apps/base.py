import os
import shutil

from wowza_startup_package_helpers.config_scripts.base_script import BaseScript
from wowza_startup_package_helpers.xml_handlers.handler import ParsedXMLFile

class BaseApp(BaseScript):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', self.__class__.__name__)
    def prepare_dirs(self):
        app_dir = self.build_filename('applications', self.name.lower())
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)
        conf_root = self.build_filename('conf')
        conf_dir = self.build_filename('conf', self.name.lower())
        if not os.path.exists(conf_dir):
            os.makedirs(conf_dir)
        if os.path.exists(os.path.join(conf_dir, 'Application.xml')):
            return
        shutil.copy(os.path.join(conf_root, 'Application.xml'), conf_dir)
    def __call__(self):
        self.prepare_dirs()
        fn = self.build_filename('conf', self.name, 'Application.xml')
        self.xml_file = ParsedXMLFile(filename=fn)
        self.modify_xml()
        self.xml_file.write()
    def modify_xml(self):
        root = self.xml_file.root_node
        node = list(root.find_by_path('Application/Name'))[0]
        node.text = self.name
        node = list(root.find_by_path('Application/AppType'))[0]
        node.text = self.app_type
