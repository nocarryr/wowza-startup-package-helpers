from base_script import BaseScript

class Script(BaseScript):
    _conf_vars = ['wms_license_key']
    def __call__(self):
        self.write_to_file(self.config.wms_license_key, 'config', 'Server.license')
