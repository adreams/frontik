import time

import tornado.ioloop

import frontik.handler

class Page(frontik.handler.PageHandler):
    def get_page(self):
        tornado.ioloop.IOLoop.instance().add_timeout(time.time()+0.6,
                     self.finish_group.add(self.async_callback(self.step2)))

    def step2(self):
        self.doc.put('ok!')
