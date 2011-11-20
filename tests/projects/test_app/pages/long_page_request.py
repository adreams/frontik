import time

import tornado.ioloop

import frontik.handler
import random

class Page(frontik.handler.PageHandler):
    def get_page(self):
        self.get_url('localhost:{0}/test_app/long_page/'.format(self.get_argument('port')),
                     request_timeout=0.3,
                     callback=self.step2)

    def step2(self, xml, response):
        if response.error:
            self.doc.put('error')
        else:
            self.doc.put('ok')
