from os import environ
from flask import Flask, render_template, url_for, redirect
from crochet import setup, run_in_reactor, wait_for
import logging
logging.basicConfig()

# this MUST be called _before_ any Autobahn or Twisted imports!
setup()
from autobahn.twisted.wamp import Application  # noqa

wapp = Application()
app = Flask(__name__)


@run_in_reactor
def start_wamp():
    """
    Starts the WAMP app on a background thread and setup communication
    with the main thread that runs a (blocking) Flask server.
    """
    router_address = environ.get("ROUTER_ADDRESS", u"ws://127.0.0.1:8080/ws")
    wapp.run(
        unicode(router_address),
        u"realm1",
        start_reactor=False)
start_wamp()


@wait_for(timeout=1)
def publish(topic, *args, **kwargs):
    return wapp.session.publish(topic, *args, **kwargs)


@wait_for(timeout=1)
def call(name, *args, **kwargs):
    return wapp.session.call(name, *args, **kwargs)


@app.route('/publish_topic')
@app.route('/publish_topic/<title>')
def publish_topic(title=None):
    if title is None:
        return redirect(url_for('publish_topic', title="Topic Title"))
    publish('com.myapp.topic', title)
    data = {
        "title": title,
    }
    return render_template('topic.html', **data)


@app.route('/rpc_platform')
def rpc_platform():
    system, release = call('com.myapp.platform')
    data = {
        "system": system,
        "release": release,
    }
    return render_template('platform.html', **data)


@app.route('/rpc_divide')
@app.route('/rpc_divide/<int:a>/<int:b>')
def rpc_divide(a=None, b=None):
    if None in [a, b]:
        return redirect(url_for('rpc_divide', a=3, b=4))
    result = call('com.myapp.divide', a, b)
    data = {
        "a": a,
        "b": b,
        "result": result,
    }
    return render_template('divide.html', **data)


@app.route('/')
def home():
    data = {}
    return render_template('home.html', **data)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
