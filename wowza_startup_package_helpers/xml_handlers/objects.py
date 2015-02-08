from xml.etree import ElementTree
import json

class BaseNode(object):
    _path_sep = '/'
    def __init__(self, **kwargs):
        self._path = None
        self._tag = None
        self._text = None
        self.attribs = {}
        self.parent = kwargs.get('parent')
        self.children = []
    @property
    def root(self):
        if self.parent is None:
            return self
        return self.parent.root
    @property
    def path(self):
        parent = self.parent
        if parent is None:
            p = self.tag
        else:
            p = self._path_sep.join([parent.path, self.tag])
        if p != self._path:
            self._path = p
        return p
    @property
    def depth(self):
        p = self.parent
        if p is None:
            return 0
        return p.depth + 1
    @property
    def tag(self):
        return self._get_tag()
    @tag.setter
    def tag(self, value):
        self._set_tag(value)
    @property
    def text(self):
        return self._get_text()
    @text.setter
    def text(self, value):
        self._set_text(value)
    def _get_tag(self):
        return self._tag
    def _set_tag(self, value):
        if value == self._tag:
            return
        self._tag = value
    def _get_text(self):
        return self._text
    def _set_text(self, value):
        if value == self._text:
            return
        self._text = value
    def get_attrib(self, key, default=None):
        return self.attribs.get(key, default)
    def set_attrib(self, key, val):
        self.attribs[key] = val
    def update_attribs(self, attribs):
        self.attribs.update(attribs)
    def add_child(self, **kwargs):
        kwargs['parent'] = self
        obj = self.__class__(**kwargs)
        self.children.append(obj)
        return obj
    def delete(self):
        if self.parent is None:
            return
        self.parent.node.remove(self.node)
        self.parent.children.remove(self)
    def find_by_path(self, p, **kwargs):
        path_sep = self._path_sep
        psplit = p.split(path_sep)
        first = psplit[0]
        if len(psplit) > 1:
            remain = path_sep.join(psplit[1:])
        else:
            remain = None
        for child in self.children:
            match_iter = None
            if child.tag != first:
                continue
            if remain is None:
                match_iter = [child]
            else:
                match_iter = child.find_by_path(remain)
            for match in match_iter:
                yield match
        
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
                self.set_attrib(key, val)
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
    def _get_tag(self):
        if self.node is not None:
            t = self.node.tag
            if t != self._tag:
                self._tag = t
            return t
        return self._tag
    def _set_tag(self, value):
        if self.node is not None:
            self.node.tag = value
        self._tag = value
    def _get_text(self):
        if self.node is None:
            t = self._text
        else:
            t = self.node.text
        if isinstance(t, basestring):
            if '\n' in t or '\t' in t:
                for char in ['\n', '\t']:
                    t = ''.join(t.split(char))
                t = t.strip(' ')
                if self.node is not None:
                    self.node.text = t
                    self.node.tail = ''
            self._text = t
        return t
    def _set_text(self, value):
        super(XMLNode, self)._set_text(value)
        if self.node is not None:
            self.node.text = value
    def get_attrib(self, key, default=None):
        if self.node is not None:
            return self.node.get(key, default)
        return super(XMLNode, self).get_attrib(key, default)
    def set_attrib(self, key, val):
        if self.node is not None:
            self.node.set(key, val)
        super(XMLNode, self).set_attrib(key, val)
    def prepare_print(self):
        d = self.depth
        p = self.parent
        if p is not None:
            if not p.text:
                p.text = '\n' + '\t' * d
            self.node.tail = '\n' + '\t' * p.depth
        for c in self.children:
            c.prepare_print()
    def __str__(self):
        return str(self.node)
        
class DictNode(BaseNode):
    def __init__(self, **kwargs):
        super(DictNode, self).__init__(**kwargs)
        self.tag = kwargs.get('tag')
        self.update_attribs(kwargs.get('attribs', {}))
        self.text = kwargs.get('text')
        for child in kwargs.get('children', []):
            self.add_child(**child)
    def to_dict(self):
        d = dict(tag=self.tag, attribs=self.attribs, text=self.text)
        d['children'] = []
        for child in self.children:
            d['children'].append(child.to_dict())
        return d
    def to_xml_node(self, **kwargs):
        d = self.to_dict()
        p = kwargs.get('parent')
        if p is not None:
            return p.add_child(**d)
        return XMLNode(**d)
    @classmethod
    def from_json(cls, js_str):
        d = json.loads(js_str)
        return cls(**d)
