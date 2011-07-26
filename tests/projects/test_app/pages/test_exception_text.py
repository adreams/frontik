import frontik.handler
import lxml.etree as etree

class Page(frontik.handler.PageHandler):
    def get_page(self):
        self.text = "old bad text"
        raise frontik.handler.HTTPError(status_code=202, text = "This is just a plain text")
        self.text = "absolutely not forty two, no way"
