import threading
import time
import sys


class Frame(threading.Thread):
    def __init__(self, frame_rate, callback):
        threading.Thread.__init__(self)
        self._stop = threading.Event()

        self._frame_rate = frame_rate
        self._callback = callback

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while True:
            time.sleep(1.0/self._frame_rate)
            try:
                self._callback()
            except Exception as e:
                print 'Exception during server frame', e
                sys.stdout.flush()
