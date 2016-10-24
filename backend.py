from __future__ import division
from platform import system, release
from os import environ
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner


class Component(ApplicationSession):
    """
    An application component providing procedures with different kinds
    of arguments.
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")

        def on_topic(title):
            print("Got event: {}".format(title))

        def platform():
            print "backend platform()"
            return [system(), release()]

        def divide(a, b):
            print "backend divide()"
            return a / b

        yield self.subscribe(on_topic, u'com.myapp.topic')
        yield self.register(platform, u'com.myapp.platform')
        yield self.register(divide, u'com.myapp.divide')
        print("Procedures registered; ready for frontend.")


if __name__ == '__main__':
    router_address = environ.get("ROUTER_ADDRESS", u"ws://127.0.0.1:8080/ws")
    runner = ApplicationRunner(
        unicode(router_address),
        u"realm1",
    )
    runner.run(Component)
