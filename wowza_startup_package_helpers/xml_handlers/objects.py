from xml.etree import ElementTree
import json

class BaseNode(object):
    def __init__(self, **kwargs):
        self.parent = kwargs.get('parent')
        self.children = []
    @property
    def root(self):
        if self.parent is None:
            return self
        return self.parent.root
    def add_child(self, **kwargs):
        kwargs['parent'] = self
        obj = self.__class__(**kwargs)
        self.children.append(obj)
        return obj
        
class XMLNode(BaseNode):
    def __init__(self, **kwargs):
        self._node = None
        super(XMLNode, self).__init__(**kwargs)
        self.node = kwargs.get('node')
        if self.node is None:
            if self.parent is None:
                self.node = ElementTree.Element('a')
            else:
                self.node = ElementTree.SubElement(self.parent.node, 'a')
            self.tag = kwargs.get('tag')
            for key, val in kwargs.get('attrib', {}).iteritems():
                self.node.set(key, val)
            if 'text' in kwargs:
                self.text = kwargs['text']
            for child in kwargs.get('children', []):
                self.add_child(**child)
    @property
    def node(self):
        return self._node
    @node.setter
    def node(self, node):
        if node is self._node:
            return
        self._node = node
        if node is None:
            return
        for c in node:
            self.add_child(node=c)
    @property
    def tag(self):
        if self.node is None:
            return None
        return self.node.tag
    @tag.setter
    def tag(self, value):
        if self.node is None:
            return
        self.node.tag = value
    @property
    def text(self):
        if self.node is None:
            return None
        t = self.node.text
        if t is None:
            return t
        for char in ['\n', '\t']:
            t = ''.join(t.split(char))
        t = t.strip(' ')
        return t
    @text.setter
    def text(self, value):
        if self.node is None:
            return
        self.node.text = value
    def __str__(self):
        return str(self.node)
        
class DictNode(BaseNode):
    def __init__(self, **kwargs):
        super(DictNode, self).__init__(**kwargs)
        self.tag = kwargs.get('tag')
        self.attribs = kwargs.get('attribs', {})
        self.text = kwargs.get('text')
        for child in kwargs.get('children', []):
            self.add_child(**child)
    def to_dict(self):
        d = dict(tag=self.tag, attribs=self.attribs, text=self.text)
        d['children'] = []
        for child in self.children:
            d['children'].append(child.to_dict())
        return d
    def to_xml_node(self):
        d = self.to_dict()
        return XMLNode(**d)
    @classmethod
    def from_json(cls, js_str):
        d = json.loads(js_str)
        return cls(**d)
