from base_script import BaseScript

class Script(BaseScript):
    def __call__(self):
        self.write_to_file(self.config.wms_license_key, 'config', 'Server.license')
