import os

XSL_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "xsl"))
XML_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "xml" ))
apply_xsl = True

class Post(object):
    def __call__(self, handler, data, cb):
        handler.log.debug('posprocessor called')
        cb(data)
    def __repr__(self):
        return "re_app Post"
postprocessor = Post()

import lxml.etree
parser = lxml.etree.XMLParser()
class XFile(file):
    name = property(lambda self: self.viewable_name)
    def __init__(self, name, *args, **kwargs):
        self.viewable_name = name + " (fake)"
        file.__init__(self, os.path.join(XSL_root,'1/base.xsl'), *args, **kwargs)
def XSL_preparser(filename):
    if not os.path.exists(filename):
        return (XFile(filename)), parser
    return filename, parser

from frontik.app import Map2ModuleName
frontik_import("pages")
frontik_import("pages.simple")
frontik_import("pages.id_param")

urls=[
        ("/+id/+(?P<id>[^/]+)", pages.id_param.Page),
        ("/+ids/+(?P<id>[^/]+)", pages.id_param.Page, lambda x: x.split(',')),
        ("/+not_simple", pages.simple.Page),
        ("", Map2ModuleName(pages)),
]