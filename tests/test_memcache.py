import tornado.testing
from frontik.adisp import async, process
from frontik.memcache import AsyncClientPool


class MemcacheTestCase(tornado.testing.AsyncTestCase):

    def get_new_ioloop(self):
        return tornado.ioloop.IOLoop.instance()

    def setUp(self):
        self.mc = AsyncClientPool("MemcacheTestCase", ["127.0.0.1:11211"])
        super(MemcacheTestCase, self).setUp()

    @process
    def setget(self, key, val, callback):
        yield self.mc.set(key, val)
        newval = yield self.mc.get(key)

        if newval == val:
            callback(1)
        else:
            callback(0)

    def test_setget_a_string(self):
        self.setget("a_string", "some random string", self.stop)
        assert self.wait() == 1

    def test_setget_an_integer(self):
        self.setget("an_integer", 42, self.stop)
        assert self.wait() == 1

    def test_long(self):
        @process
        def _test(callback):
            long_val = long(1<<30)
            assert ((yield async(self.setget)("long", long_val)) == 1)
            assert ((yield self.mc.delete("long")) == 1)
            assert ((yield self.mc.get("long")) is None)
            callback()
        _test(self.stop)
        self.wait()



if __name__ == "__main__":
    tornado.testing.main()
