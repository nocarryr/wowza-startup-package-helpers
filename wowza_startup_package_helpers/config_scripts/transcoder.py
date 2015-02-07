from base_script import BaseScript

from wowza_startup_package_helpers.xml_handlers.objects import XMLNode, DictNode
from wowza_startup_package_helpers.xml_handlers.handler import XMLFile, ParsedXMLFile

class ParsedTransrate(ParsedXMLFile):
    def __init__(self, **kwargs):
        self.script = kwargs.get('script')
        fn = self.script.build_filename('transcoder', 'templates', 'transrate.xml')
        kwargs.setdefault('filename', fn)
        super(Transrate, self).__init__(**kwargs)
        
class Transrate(XMLFile):
    def __init__(self, **kwargs):
        self.script = kwargs.get('script')
        fn = self.script.build_filename('transcoder', 'templates', 'transrate.xml')
        kwargs.setdefault('filename', fn)
        super(Transrate, self).__init__(**kwargs)
        self.root_node = XMLNode(tag='Root', attribs={'version':'1'})
        tcnode = self.root_node.add_child(tag='Transcode')
        tcnode.add_child(tag='Description', text='Custom')
        tcnode.add_child(tag='Encodes')
        tcnode.add_child(tag='StreamNameGroups')
        
class TranscodeMod(object):
    def __init__(self, **kwargs):
        self.children = []
        self.script = kwargs.get('script')
        self.name = kwargs.get('name')
        self.xml_file = self.script.transrate_xml
        self.parent = kwargs.get('parent')
        if self.parent is None:
            self.base_path = '/'.join(['Transcode', self.search_path])
        self.node = self.find_node()
        if self.node is None:
            self.node = self.build_node(**kwargs)
        else:
            self.get_attrs_from_node()
    def add_child(self, cls, **kwargs):
        kwargs.setdefault('parent', self)
        kwargs.setdefault('script', self.script)
        obj = cls(**kwargs)
        self.children.append(obj)
        return obj
    def find_node(self):
        if self.parent is not None:
            obj = self.parent.node
            search_path = getattr(self, 'search_path', None)
            if search_path is not None:
                p = '/'.join([search_path, self.tag])
            else:
                p = self.tag
        else:
            obj = self.xml_file
            p = '/'.join([self.base_path, self.tag])
        if self.name is None:
            match = obj.find_by_path(p)
            if isinstance(match, XMLNode):
                return match
            if not len(list(match)):
                return None
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
            if not isinstance(node, XMLNode):
                node = list(node)[0]
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
        d = dict(tag=self.tag, children=[])
        for attr in self.tag_attrs:
            tag = self.format_tag_from_attr(attr)
            val = getattr(self, attr, None)
            if val is None:
                val = kwargs.get(attr)
                if val is None:
                    val = getattr(self, 'attr_defaults', {}).get(attr)
                setattr(self, attr, val)
            if val is None:
                continue
            d['children'].append(dict(tag=tag, text=str(val)))
        dnode = DictNode(**d)
        if self.parent is None:
            parent_node = self.xml_file.find_by_path(self.base_path)
        else:
            parent_node = self.parent.node
        return dnode.to_xml_node(parent=parent_node)
        
class Encode(TranscodeMod):
    search_path = 'Encodes'
    tag = 'Encode'
    tag_attrs = ['name', 'stream_name', 'enable']
    def __init__(self, **kwargs):
        super(Encode, self).__init__(**kwargs)
        self.video = self.add_child(EncodeVideo, **kwargs.get('video', {}))
        self.audio = self.add_child(EncodeAudio, **kwargs.get('audio', {}))
        self.stream_name = kwargs.get('stream_name')
        if self.stream_name is None and self.video.frame_size.width is not None:
            self.stream_name = 'mp4:${SourceStreamName}_%sp' % (self.video.frame_size.width)
        
class EncodeVideo(TranscodeMod):
    tag = 'Video'
    tag_attrs = ['profile', 'bitrate', 'implementation', 'gpu_id']
    attr_defaults = dict(
        implementation='default', 
        gpu_id=-1, 
    )
    def __init__(self, **kwargs):
        super(EncodeVideo, self).__init__(**kwargs)
        self.frame_size = self.add_child(FrameSize, **kwargs.get('frame_size', {}))
        self.keyframe = self.add_child(KeyframeInterval, **kwargs.get('keyframe_interval', {}))
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
        
class KeyframeInterval(TranscodeMod):
    tag = 'KeyframeInterval'
    tag_attrs = ['follow_source', 'interval']
    attr_defaults = dict(
        follow_source=True, 
        interval=60, 
    )
    def __init__(self, **kwargs):
        super(KeyframeInterval, self).__init__(**kwargs)
        
class EncodeAudio(TranscodeMod):
    tag = 'Audio'
    tag_attrs = ['codec', 'bitrate']
    def __init__(self, **kwargs):
        super(EncodeAudio, self).__init__(**kwargs)
        
        
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
        
class Script(BaseScript):
    def build_transrate(self, **kwargs):
        encodes = self.encodes = []
        str_groups = self.stream_name_groups = []
        kwargs.setdefault('script', self)
        if kwargs.get('strategy') == 'replace':
            self.transrate_xml = Transrate(**kwargs)
        else:
            self.transrate_xml = ParsedTransrate(**kwargs)
        for enc_conf in kwargs.get('encodes', []):
            enc_conf['script'] = self
            encodes.append(Encode(**enc_conf))
        for str_group in kwargs.get('stream_name_groups', []):
            str_group['script'] = self
            str_groups.append(StreamNameGroup(**str_group))
    def __call__(self):
        transrate_conf = self.config.get('transrate_conf')
        if transrate_conf is not None:
            self.build_transrate(**transrate_conf)

DEFAULTS = dict(
    strategy='replace', 
    encodes=[
        {
            'name':'source', 
            'enable':True, 
            'stream_name':'mp4:${SourceStreamName}_source', 
            'video':{
                'codec':'PassThru', 
                'bitrate':'${SourceVideoBitrate}', 
            }, 
            'audio':{
                'codec':'AAC', 
                'bitrate':128000, 
            }, 
        }, {
            'name':'720p', 
            'enable':True,
            'video':{
                'codec':'H.264', 
                'profile':'main', 
                'bitrate':1300000, 
                'frame_size':{
                    'width':1280, 
                    'height':720, 
                }, 
            }, 
            'audio':{
                'codec':'AAC', 
                'bitrate':128000, 
            }, 
        }, {
            'name':'360p', 
            'enable':True, 
            'video':{
                'codec':'H.264', 
                'profile':'main', 
                'bitrate':850000, 
                'frame_size':{
                    'width':640, 
                    'height':360, 
                }, 
            }, 
            'audio':{
                'codec':'AAC', 
                'bitrate':128000, 
            }, 
        }, {
            'name':'240p', 
            'enable':True, 
            'video':{
                'codec':'H.264', 
                'profile':'baseline', 
                'bitrate':350000, 
                'frame_size':{
                    'width':360, 
                    'height':240, 
                }, 
            }, 
            'audio':{
                'codec':'AAC', 
                'bitrate':96000, 
            }, 
        }, 
    ], 
    decode={}, 
    stream_name_groups=[
        {
            'name':'all', 
            'members':[
                {'name':'source'}, 
                {'name':'720p'}, 
                {'name':'360p'}, 
                {'name':'240p'}, 
            ], 
        }, 
    ], 
)
    
def test():
    kwargs = dict(filename='test.xml')
    kwargs.update(DEFAULTS)
    script = Script()
    script.build_transrate(**kwargs)
    return script
