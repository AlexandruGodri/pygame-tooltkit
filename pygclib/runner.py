import threading
import sys


class Runner(threading.Thread):
    def __init__(self, callback, args):
        threading.Thread.__init__(self)
        self._stop = threading.Event()

        self._callback = callback
        self._args = args

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        self._callback(*self._args)
