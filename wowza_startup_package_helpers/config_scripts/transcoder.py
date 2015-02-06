from base_script import BaseScript
from wowza_startup_package_helpers.xml_handlers.objects import DictNode
from wowza_startup_package_helpers.xml_handlers.handler import ParsedXMLFile

class Transrate(ParsedXMLFile):
    def __init__(self, **kwargs):
        self.script = kwargs.get('script')
        kwargs['filename'] = self.script.build_filename('transcoder', 'templates', 'transrate.xml')
        super(Transrate, self).__init__(**kwargs)
class TranscodeMod(object):
    def __init__(self, **kwargs):
        self.script = kwargs.get('script')
        self.name = kwargs.get('name')
        self.base_path = '/'.join(['Root/Transcode', self.search_path])
        self.xml_file = self.script.transrate_xml
        self.node = self.find_node()
    def find_node(self):
        p = '/'.join([self.base_path, self.tag, 'Name'])
        for match in self.xml_file.find_by_path(p, single_result=False):
            if match.text == self.name:
                return match
                
class Encode(TranscodeMod):
    search_path = 'Encodes'
    tag = 'Encode'
    def __init__(self, **kwargs):
        super(Encode, self).__init__(**kwargs)
        self.enabled = kwargs.get('enabled')
        self.width = kwargs.get('width')
        self.height = kwargs.get('height')
        self.profile = kwargs.get('profile')
        self.bitrate = kwargs.get('bitrate')
        self.aud_codec = kwargs.get('aud_codec')
        self.aud_bitrate = kwargs.get('aud_bitrate')
        
class StreamNameGroup(TranscodeMod):
    def __init__(self, **kwargs):
        super(StreamNameGroup, self).__init__(**kwargs)
        self.stream_name = kwargs.get('stream_name', '${SourceStreamName}_all')
        self.members = []
        for encode in kwargs.get('members', []):
            self.add_member(encode)
    def add_member(self, encode):
        self.members.append(encode)
        
class Script(BaseScript):
    pass
