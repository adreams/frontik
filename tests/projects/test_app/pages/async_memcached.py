# -*- coding: utf-8 -*-

import logging
from functools import partial
import frontik.memcache as memcache
from frontik.adisp import async, process
import random
import frontik.handler

log = logging.getLogger(__name__)

class Page(frontik.handler.PageHandler):   

    @process
    def get_page(self):
        rand_key = "random_key_{0}".format(random.randint(1, 1000))
        rand_val = "random_val_{0}".format(random.randint(1, 1000))

        yield self.memcache.set(rand_key, rand_val)
        value = yield self.memcache.get(rand_key)
        yield self.memcache.delete(rand_key)

        if value == rand_val:
            self.text = "OK"
        else:
            self.text = "ERROR"
