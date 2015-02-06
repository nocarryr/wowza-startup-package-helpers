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
        self.parent = kwargs.get('parent')
        self.node = self.find_node()
    def find_node(self):
        if self.parent is not None:
            obj = self.parent.node
        else:
            obj = self.xml_file
        p = '/'.join([self.base_path, self.tag])
        if self.name is None:
            return obj.find_by_path(p)
        p = '/'.join([p, 'Name'])
        for match in obj.find_by_path(p, single_result=False):
            if match.text == self.name:
                return match
    def build_node(self, **kwargs):
        return DictNode(**kwargs)
        
class Encode(TranscodeMod):
    search_path = 'Encodes'
    tag = 'Encode'
    def __init__(self, **kwargs):
        super(Encode, self).__init__(**kwargs)
        self.enabled = kwargs.get('enabled')
        vkwargs = kwargs.get('video', {})
        vkwargs.update(dict(script=self.script, parent=self))
        self.video = EncodeVideo(**vkwargs)
        akwargs = kwargs.get('audio', {})
        akwargs.update(dict(script=self.script, parent=self))
        self.audio = EncodeAudio(**akwargs)
        
class EncodeVideo(TranscodeMod):
    tag = 'Video'
    def __init__(self, **kwargs):
        super(EncodeVideo, self).__init__(**kwargs)
        self.width = kwargs.get('width')
        self.height = kwargs.get('height')
        self.profile = kwargs.get('profile')
        self.bitrate = kwargs.get('bitrate')
        
class EncodeAudio(TranscodeMod):
    tag = 'Audio'
    def __init__(self, **kwargs):
        super(EncodeAudio, self).__init__(**kwargs)
        self.codec = kwargs.get('codec')
        self.bitrate = kwargs.get('bitrate')
        
        
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
