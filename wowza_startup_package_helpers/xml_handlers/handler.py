from xml.etree import ElementTree

from wowza_startup_package_helpers.xml_handlers.objects import XMLNode, DictNode

class XMLDoc(object):
    def __init__(self, **kwargs):
        self._tree = None
        self._root_node = None
    @property
    def tree(self):
        return self._tree
    @tree.setter
    def tree(self, value):
        self._tree = value
    @property
    def root_node(self):
        return self._root_node
    @root_node.setter
    def root_node(self, value):
        self._root_node = value
    def find_by_path(self, path, single_result=True):
        match = list(self.root_node.find_by_path(path))
        if not len(match):
            return []
        if single_result:
            if len(match) > 1:
                raise Exception('Multiple matches for %s' % (path))
            match = match[0]
        return match
    def insert_dict_node(self, dnode, path):
        parent = self.find_by_path(path)
        dnode.to_xml_node(parent=parent)
    def insert_from_dict(self, d, path):
        parent = self.find_by_path(path)
        dnode = DictNode(**d)
        dnode.to_xml_node(parent=parent)
    def insert_from_json(self, js_str, path):
        parent = self.find_by_path(path)
        dnode = DictNode.from_json(js_str)
        dnode.to_xml_node(parent=parent)
        
class XMLFile(XMLDoc):
    def __init__(self, **kwargs):
        super(XMLFile, self).__init__(**kwargs)
        self.filename = kwargs.get('filename')
    def write(self):
        root = self.root_node
        root.prepare_print()
        t = self.tree
        if t is None:
            t = ElementTree.ElementTree(element=root.node)
        t.write(self.filename, encoding='UTF-8')
        
class ParsedXMLFile(XMLFile):
    def __init__(self, **kwargs):
        super(ParsedXMLFile, self).__init__(**kwargs)
        self.tree = ElementTree.parse(self.filename)
        root = self.tree.getroot()
        self.root_node = XMLNode(node=root)
