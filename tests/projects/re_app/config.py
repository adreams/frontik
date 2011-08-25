import os

XSL_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "xsl"))
XML_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "xml" ))
apply_xsl = True

def post(self, data, cb):
    self.log.debug('posprocessor called')
    cb(data)
    
postprocessor = post


import StringIO
class MyXString(StringIO.StringIO):
    def __init__(self, buf = '', fake_name='generated x'):
        self.fake_name = fake_name
        StringIO.StringIO.__init__(self, buf)
    def __repr__(self):
        return "'{0}'".format(self.fake_name)
from lxml import etree
parser = etree.XMLParser()
def XML_preparser(filename):
    if 'fool' in filename:
        res = MyXString("<fool/>", 'new on-the-go fake {0}'.format(filename))
        return res, parser
    return filename, parser

def XSL_preparser(filename):
    if 'fool' in filename:
        return filename.replace('fool', 'simple'), parser
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