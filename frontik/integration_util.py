# -*- coding: utf-8 -*-

import time
import urllib2
import contextlib
import socket
import lxml.etree as etree

import tornado_util.supervisor as supervisor
import tornado.options


def simple_main(port, cfg):
    from tornado.options import options
    import frontik.app
    import frontik.options

    import tornado.httpserver
    import tornado.ioloop

    tornado.options.define('host', '0.0.0.0', str)
    #tornado.options.define('port', '0', int)
    tornado.options.define('daemonize', False, bool)
    tornado.options.define('autoreload', False, bool)
    options['host'].set('0.0.0.0')
    options['port'].set(port)
    tornado.options.parse_config_file(cfg)
    tornado.options.process_options()

    app = frontik.app.get_app(options.urls, options.apps)


    http_server = tornado.httpserver.HTTPServer(app)
    
    http_server.listen(options.port, options.host)

    io_loop = tornado.ioloop.IOLoop.instance()
    io_loop.start()

def get_page(port, page, xsl=False):
    url = "http://localhost:{0}/{1}{2}".format(port, page,
                                               ("/?" if "?" not in page else "&") + ("noxsl=true" if not xsl else ""))
    data = urllib2.urlopen(url)
    return data

def try_open_port():
    for port in xrange(9000, 10000):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("", port))
            s.close()
            break
        except:
            pass
    else:
        raise AssertionError("no empty port in 9000-10000 for frontik test instance")
    return port

class FrontikTestInstance(object):
    def __init__(self, cfg="./tests/projects/frontik.cfg", dev_run = None, threaded = False):
        self.cfg = cfg
        tornado.options.parse_config_file(self.cfg)
        self.port = None
        self.supervisor = supervisor
        self.dev_run = dev_run
        self.threaded = threaded

    def start(self):
        port = try_open_port()
        supervisor.start_worker("./dev_run.py", self.cfg, port)
        self.wait_for(lambda: supervisor.is_running(port))
        self.port = port

    def start_threaded(self,):
        import threading
        port = try_open_port()
        def run():
            simple_main(port, self.cfg)

        frontik_server_tread = threading.Thread(target = run, )
        frontik_server_tread.daemon = True
        frontik_server_tread.start()
        self.wait_for(lambda: supervisor.is_running(port))
        self.frontik_server_tread = frontik_server_tread
        self.port = port

    def __del__(self):
        print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! __del__'
        self.supervisor.stop_worker(self.port)
        self.wait_for(lambda: not(self.supervisor.is_running(self.port)))
        if self.frontik_server_tread:
            return
        self.supervisor.rm_pidfile(self.port)

    def wait_for(self, fun, n=50):
        for i in range(n):
            if fun():
                return
            time.sleep(0.1)

        assert(fun())

    @contextlib.contextmanager
    def instance(self):
        if not self.port:
            if self.threaded:
                self.start_threaded()
            else:
                self.start()
        try:
            yield self.port
        finally:
            data = urllib2.urlopen("http://localhost:{0}/ph_count/".format(self.port)).read().split("\n")
            ph_count = int(data[0])
            refs = data[1:]
            print "ph_count={0}".format(ph_count)
            print "refs={0}".format(refs)


    @contextlib.contextmanager
    def get_page_xml(self, page_name, xsl=True):
        with self.instance() as srv_port:
            data = get_page(srv_port, page_name, xsl).read()
    
            try:
                res = etree.fromstring(data)
            except:
                print "failed to parse xml: \"%s\"" % (data,)
                raise
    
            yield res

    @contextlib.contextmanager
    def get_page_text(self, page_name, xsl=True):
        with self.instance() as srv_port:
            data = get_page(srv_port, page_name, xsl).read()
            yield data

global http_fetch_intercept
def http_fetch_intercept(self, req, callback):
    raise RuntimeError('set http_fetch_intercept by subclassing InterceptHttpFetchTestCase')

def patch_frontik_fetch_request():
    import frontik.handler
    global http_fetch_intercept
    def fetch_request(handler, req, callback):
        return http_fetch_intercept(handler, req, callback)
    frontik.handler.PageHandler.fetch_request = fetch_request
    return http_fetch_intercept

import unittest

class InterceptHttpFetchTestCase(unittest.TestCase):
    def setUp(self):
        global http_fetch_intercept
        http_fetch_intercept = self.http_fetch_intercept
    def tearDown(self):
        pass

    def http_fetch_intercept(self, handler, req, callback):
        raise NotImplementedError()

class StackCallbackTestCase(InterceptHttpFetchTestCase):
    def setUp(self):
        self.callback_heap = []
        super(StackCallbackTestCase, self).setUp()

    def http_fetch_intercept(self, handler, req, callback):
        self.callback_heap.append((handler, req, callback))
