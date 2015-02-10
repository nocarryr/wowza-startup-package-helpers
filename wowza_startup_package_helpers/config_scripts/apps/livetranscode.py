from live import Live

class LiveTranscode(Live):
    def modify_xml(self):
        super(LiveTranscode, self).modify_xml()
        root = self.xml_file.root_node
        node = list(root.find_by_path('Application/Transcoder/LiveStreamTranscoder'))[0]
        node.text = 'transcoder'
