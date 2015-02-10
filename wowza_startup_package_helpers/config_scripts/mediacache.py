from base_script import BaseScript
from wowza_startup_package_helpers.xml_handlers.hanlder import ParsedXMLFile

class Script(BaseScript):
    _conf_vars = ['aws_access_key_id', 'aws_secret_access_key']
    def __call__(self):
        fn = self.build_conf_filename('MediaCache.xml')
        xml_file = ParsedXMLFile(filename=fn)
        for props_node in xml_file.find_by_path('MediaCacheSources/MediaCacheSource/Properties'):
            for name_node in props_node.find_by_path('Property/Name'):
                if 'aws' not in name_node.text:
                    continue
                value_node = list(name_node.parent.find_by_path('Value'))[0]
                if 'accesskeyid' in name_node.text.lower():
                    value_node.text = self.config.aws_access_key_id
                elif 'secretaccesskey' in name_node.text.lower():
                    value_node.text = self.config.aws_secret_access_key
        xml_file.write()
