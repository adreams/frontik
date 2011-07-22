import frontik.handler


class Page(frontik.handler.PageHandler):
    def get_page(self):
        self.doc.put("42")
        raise frontik.handler.HTTPErrorNew(status_code=200)
        self.doc.put("absolutely not forty two, no way")
