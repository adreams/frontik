import frontik.handler

class Page(frontik.handler.PageHandler):
    def get_page(self):
        self.doc.put(self.xml.xml_from_file('{0}.xml'.format(self.get_argument('postfix','cdata'))))