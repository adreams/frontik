import frontik.handler


class Page(frontik.handler.PageHandler):
    def get_page(self):
        self.finish_with_401()
