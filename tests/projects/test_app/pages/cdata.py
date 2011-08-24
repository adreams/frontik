import frontik.handler
from frontik import etree

CDATA_XML = ('<root><![CDATA[test<ba//d> >><<]]></root>')

class Page(frontik.handler.PageHandler):
    def get_page(self):
        def _cb(xml, resp):
            xpath = xml.xpath("/doc/*")
            assert len(xpath) == 1
            assert etree.tostring(xpath[0]) == CDATA_XML
        self.post_url("http://localhost:%stest_app/cdata/" % self.get_argument("port"), "", callback=_cb)

    def post_page(self):
        root = self.ph_globals.xml.xml_parser(CDATA_XML)
        self.log.debug(etree.tostring(root))
        self.doc.put(root)