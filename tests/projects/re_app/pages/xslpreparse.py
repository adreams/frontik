import frontik.handler

class Page(frontik.handler.PageHandler):
    def get_page(self):
        self.set_xsl('{0}.xsl'.format(self.get_argument('postfix','simple')))