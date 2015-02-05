from xml.etree import ElementTree

class XMLNode(object):
    def __init__(self, **kwargs):
        self._node = None
        self.children = []
        self.parent = kwargs.get('parent')
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
    def add_child(self, **kwargs):
        kwargs['parent'] = self
        obj = XMLNode(**kwargs)
        self.children.append(obj)
        return obj
    def __str__(self):
        return str(self.node)
