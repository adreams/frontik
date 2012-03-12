# -*- coding: utf-8 -*-

import time
import urllib2
import contextlib
import socket
import lxml.etree as etree

import tornado_util.supervisor as supervisor
import tornado.options
from frontik.app import App

from functools import partial
from tornado.options import options
import frontik.app
import tornado.httpserver
import tornado.ioloop

class MockHttpClient(object):
    def __init__(self, *arg, **kwarg):
        super(MockHttpClient, self).__init__(*arg, **kwarg)
    def fetch_request(self, req, callback):
        raise RuntimeError('set http_fetch_intercept by subclassing/'+\
                           'augmenting MockHttpClient and passing it to MockTestApp')

class MockTestApp(App):
    def __init__(self, *arg, **kwarg):
        # hack here to workaround lazy init MockTestApp w/o touching App class
        self.mock_http_client = kwarg.pop('mock_http_client')
        super(MockTestApp, self).__init__(*arg, **kwarg)

    def _initialize(self):
        # continues here
        result = super(MockTestApp, self)._initialize()
        self.ph_globals.http_client = self.mock_http_client
        return result

    def get_test_handler(self):
        return 

def simple_main(port, cfg, mock_http_client, ioloop=True):
    import frontik.options

    tornado.options.parse_config_file(cfg)
    tornado.options.process_options()
    app_factory = partial(MockTestApp, mock_http_client=mock_http_client)
    app = frontik.app.get_app(options.urls, 
                              options.apps, 
                              app_factory = app_factory)

    if ioloop:
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port, options.host)
        io_loop = tornado.ioloop.IOLoop.instance()
        io_loop.start()
    else:
        return app
    
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
    def __init__(self, cfg="./tests/projects/frontik.cfg", dev_run = None, threaded = False, ioloop=True):
        self.cfg = cfg
        tornado.options.parse_config_file(self.cfg)
        self.port = None
        self.supervisor = supervisor
        self.dev_run = dev_run
        self.threaded = threaded
        self.ioloop = ioloop

    def start(self):
        port = try_open_port()
        supervisor.start_worker("./dev_run.py", self.cfg, port)
        self.wait_for(lambda: supervisor.is_running(port))
        self.port = port

    def start_threaded(self,):
        def run():
            simple_main(port, self.cfg)
        import threading
        port = try_open_port()
        frontik_server_tread = threading.Thread(target = run, )
        frontik_server_tread.daemon = True
        frontik_server_tread.start()
        self.wait_for(lambda: supervisor.is_running(port))
        self.frontik_server_tread = frontik_server_tread
        self.port = port

    def __del__(self):
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
