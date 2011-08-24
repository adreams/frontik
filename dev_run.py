#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.options
import tornado.ioloop
from frontik.server import main

if __name__ == "__main__":
    try:
        main('./frontik_dev.cfg')
    except:
        print 'shutdowning instance'
        tornado.ioloop.IOLoop.instance().stop()
