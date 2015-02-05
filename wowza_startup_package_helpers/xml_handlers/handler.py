from xml.etree import ElementTree

from wowza_startup_package_helpers.xml_handlers.objects import XMLNode, DictNode

class XMLDoc(object):
    def __init__(self, **kwargs):
        pass
        
class XMLFile(XMLDoc):
    def __init__(self, **kwargs):
        super(XMLFile, self).__init__(**kwargs)
        self.filename = kwargs.get('filename')
        
class ParsedXMLFile(XMLFile):
    def __init__(self, **kwargs):
        super(ParsedXMLFile, self).__init__(**kwargs)
        tree = ElementTree.parse(self.filename)
        root = tree.getroot()
        self.root_node = XMLNode(node=root)
