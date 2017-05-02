import threading
import sys
import time
import json


class Listener(threading.Thread):
    def __init__(self, sock, buffer, callback):
        threading.Thread.__init__(self)
        self._stop = threading.Event()

        self._socket = sock
        self._buffer = buffer
        self._callback = callback

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while True:
            try:
                data = self._socket.recv(self._buffer)
                if not data:
                    continue
                self._callback(json.loads(data))
            except Exception as e:
                if type(e).__name__ in ['timeout', 'ValueError']:
                    continue
                else:
                    print 'Exception listening to events from server', e, type(e).__name__
                    sys.stdout.flush()
                    self._socket.close()
                    self._stop()
            time.sleep(0.016)
