from vod import Vod

class VodS3(Vod):
    def modify_xml(self):
        super(VodS3, self).modify_xml()
        root = self.xml_file.root_node
        node = list(root.find_by_path('Application/MediaReader/Properties'))[0]
        prop = node.add_child(tag='Property')
        prop.add_child(tag='Name', text='randomAccessReaderClass')
        prop.add_child(tag='Value', text='com.wowza.wms.mediacache.impl.MediaCacheRandomAccessReaderVODEdge')
        prop.add_child(tag='Type', text='String')
        prop = node.add_child(tag='Property')
        prop.add_child(tag='Name', text='bufferSeekIO')
        prop.add_child(tag='Value', text='true')
        prop.add_child(tag='Type', text='Boolean')
        node = list(root.find_by_path('Application/HTTPStreamer/Properties'))[0]
        prop = node.add_child(tag='Property')
        prop.add_child(tag='Name', text='httpOptimizeFileReads')
        prop.add_child(tag='Value', text='true')
        prop.add_child(tag='Type', text='Boolean')
