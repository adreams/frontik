import logging
import os.path
import urlparse

import lxml.etree as etree


log = logging.getLogger("frontik.xml_util")
parser = etree.XMLParser(strip_cdata=False)

class PrefixResolver(etree.Resolver):
    def __init__(self, scheme, path):
        self.scheme = scheme
        self.path = os.path.abspath(path)

    def resolve(self, system_url, public_id, context):
        parsed_url = urlparse.urlsplit(system_url)
        if parsed_url.scheme == self.scheme:
            path = os.path.abspath(os.path.join(self.path, parsed_url.path))
            if not os.path.commonprefix([self.path, path]).startswith(self.path):
                raise etree.XSLTParseError('Open files out of XSL root is not allowed: {0}'.format(path))
            return self.resolve_filename(path, context)

def _abs_filename(base_filename, filename):
    if filename.startswith("/"):
        return filename
    else:
        base_dir = os.path.dirname(base_filename)
        return os.path.normpath(os.path.join(base_dir, filename))

def _read_one_xsl(source, log=log, parser=parser):
    """return (etree.ElementTree, xsl_includes)"""

    name = source.name if hasattr(source, 'name') else str(source)
    log.debug("read file %s", name)
    tree = etree.parse(source, parser)
    xsl_includes = [_abs_filename(name, imp.get("href"))
                    for imp in tree.xpath('xsl:import|xsl:include',namespaces={'xsl':'http://www.w3.org/1999/XSL/Transform'})
                    if imp.get("href").find(":") == -1]
    xsl_includes.append(name)
    return tree, xsl_includes

def read_xsl(source, log=log, parser=parser):
    """return (etree.XSL, xsl_files_watchlist)"""

    xsl_includes = set()

    result, new_xsl_files = _read_one_xsl(source, log, parser)

    diff = set(new_xsl_files).difference(xsl_includes)
    while diff:
        new_xsl_files = set()

        for i in diff:
            _, i_files = _read_one_xsl(i, log)
            xsl_includes.add(i)
            new_xsl_files.update(i_files)

        diff = new_xsl_files.difference(xsl_includes)

    return (etree.XSLT(result), xsl_includes)
