import threading
import sys


class Connection(threading.Thread):
    def __init__(self, sock, callback):
        threading.Thread.__init__(self)
        self._stop = threading.Event()

        self._socket = sock
        self._callback = callback

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while True:
            sockfd, addr = self._socket.accept()
            self._callback(sockfd, addr[1])
