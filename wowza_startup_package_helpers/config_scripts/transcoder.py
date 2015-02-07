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
        self.children = []
        self.script = kwargs.get('script')
        self.name = kwargs.get('name')
        self.base_path = '/'.join(['Transcode', self.search_path])
        self.xml_file = self.script.transrate_xml
        self.parent = kwargs.get('parent')
        self.node = self.find_node()
    def add_child(self, cls, **kwargs):
        kwargs.setdefault('parent', self)
        kwargs.setdefault('script', self.script)
        obj = cls(**kwargs)
        self.children.append(obj)
        return obj
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
    def format_tag_from_attr(self, attr):
        return ''.join([s.title() for s in attr.split('_')])
    def get_attrs_from_node(self):
        for attr in self.tag_attrs:
            tag = self.format_tag_from_attr(attr)
            node = self.node.find_by_path(tag)
            val = node.text
            if val == 'True':
                val = True
            elif val == 'False':
                val = False
            elif isinstance(val, basestring) and val.isdigit():
                val = int(val)
            setattr(self, attr, val)
    def update_node(self):
        for attr in self.tag_attrs:
            val = getattr(self, attr)
            if val is None:
                continue
            val = str(val)
            tag = self.format_tag_from_attr(attr)
            node = self.node.find_by_path(tag)
            if node.text == val:
                continue
            node.text = val
    def build_node(self, **kwargs):
        return DictNode(**kwargs)
        
class Encode(TranscodeMod):
    search_path = 'Encodes'
    tag = 'Encode'
    tag_attrs = ['name', 'stream_name', 'enable']
    def __init__(self, **kwargs):
        super(Encode, self).__init__(**kwargs)
        self.stream_name = kwargs.get('stream_name')
        self.enable = kwargs.get('enable')
        self.video = self.add_child(EncodeVideo, **kwargs.get('video', {}))
        self.audio = self.add_child(EncodeAudio, **kwargs.get('audio', {}))
        self.stream_name = kwargs.get('stream_name')
        if self.stream_name is None and self.video.width is not None:
            self.stream_name = 'mp4:${SourceStreamName}_%sp' % (self.video.width)
        
class EncodeVideo(TranscodeMod):
    tag = 'Video'
    tag_attrs = ['profile', 'bitrate', 'implementation', 'gpu_id']
    attr_defaults = dict(
        implementation='default', 
        gpu_id=-1, 
    )
    def __init__(self, **kwargs):
        super(EncodeVideo, self).__init__(**kwargs)
        self.profile = kwargs.get('profile')
        self.bitrate = kwargs.get('bitrate')
        self.frame_size = self.add_child(FrameSize, **kwargs.get('frame_size', {}))
        self.keyframe = self.add_child(KeyframeInterval, **kwargs.get('keyframe_interval'))
    def format_tag_from_attr(self, attr):
        if attr == 'gpu_id':
            return 'GPUID'
        return super(EncodeVideo, self).format_tag_from_attr(attr)
    
class FrameSize(TranscodeMod):
    tag = 'FrameSize'
    tag_attrs = ['fit_mode', 'width', 'height']
    attr_defaults = dict(
        fit_mode='fit-height', 
    )
    def __init__(self, **kwargs):
        super(FrameSize, self).__init__(**kwargs)
        self.fit_mode = kwargs.get('fit_mode')
        self.width = kwargs.get('width')
        self.height = kwargs.get('height')
        
class KeyframeInterval(TranscodeMod):
    tag = 'KeyframeInterval'
    tag_attrs = ['follow_source', 'interval']
    attr_defaults = dict(
        follow_source=True, 
        interval=60, 
    )
    def __init__(self, **kwargs):
        super(KeyframeInterval, self).__init__(**kwargs)
        self.follow_source = kwargs.get('follow_source')
        self.interval = kwargs.get('interval')
        
class EncodeAudio(TranscodeMod):
    tag = 'Audio'
    def __init__(self, **kwargs):
        super(EncodeAudio, self).__init__(**kwargs)
        self.codec = kwargs.get('codec')
        self.bitrate = kwargs.get('bitrate')
        
        
class StreamNameGroup(TranscodeMod):
    search_path = 'StreamNameGroups'
    tag = 'StreamNameGroup'
    tag_attrs = ['name', 'stream_name']
    def __init__(self, **kwargs):
        super(StreamNameGroup, self).__init__(**kwargs)
        self.stream_name = kwargs.get('stream_name', '${SourceStreamName}_all')
        for member in kwargs.get('members', []):
            self.add_member(**member)
    def add_member(self, **kwargs):
        return self.add_child(Member, **kwargs)
        
        
class Member(TranscodeMod):
    tag = 'Member'
    tag_attrs = ['member_name', 'encode_name']
    def __init__(self, **kwargs):
        super(Member, self).__init__(**kwargs)
        self.member_name = kwargs.get('member_name', self.name)
        self.encode_name = kwargs.get('encode_name', self.member_name)
    
class Decode(TranscodeMod):
    tag = 'Decode'
    tag_attrs = ['implementation', 'deinterlace']
    attr_defaults = dict(
        implementation='default', 
    )
    def __init__(self, **kwargs):
        super(Decode, self).__init__(**kwargs)
        self.implementation = kwargs.get('implementation')
        self.deinterlace = kwargs.get('deinterlace')
        
class Script(BaseScript):
    def build_transrate(self, **kwargs):
        encodes = self.encodes = []
        str_groups = self.stream_name_groups = []
        self.transrate_xml = Transrate(script=self)
        for enc_conf in kwargs.get('encodes', []):
            encodes.append(Encode(script=self))
        for str_groups in kwargs.get('stream_name_groups', []):
            str_groups.append(StreamNameGroup(script=self))
    def __call__(self):
        transrate_conf = self.config.get('transrate_conf')
        if transrate_conf is not None:
            self.build_transrate(**transrate_conf)
