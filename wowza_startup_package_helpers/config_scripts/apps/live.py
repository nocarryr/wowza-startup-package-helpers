from base import BaseApp

class Live(BaseApp):
    app_type = 'Live'
    def modify_xml(self):
        root = self.xml_file.root_node
        node = list(root.find_by_path('Application/Streams/LiveStreamPacketizers'))[0]
        node.text = 'cupertinostreamingpacketizer, mpegdashstreamingpacketizer, sanjosestreamingpacketizer, smoothstreamingpacketizer'
        node = list(root.find_by_path('Application/Client/Access/StreamWriteAccess'))[0]
        node.text = '*'
        node = list(root.find_by_path('Application/Modules'))[0]
        mod = node.add_child(tag='Module')
        mod.add_child(tag='Name', text='ModuleCoreSecurity')
        mod.add_child(tag='Description', text='Core Security Module for Applications')
        mod.add_child(tag='Class', text='com.wowza.wms.security.ModuleCoreSecurity')
