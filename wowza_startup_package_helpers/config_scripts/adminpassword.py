from base_script import BaseScript

class Script(BaseScript):
    def __call__(self):
        s = ' '.join([self.config.wms_admin_user, self.config.wms_admin_pass])
        self.write_to_file(s, 'conf', 'admin.password')
