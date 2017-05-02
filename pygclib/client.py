import socket
import sys
import threading
import time
import json
import listener
import runner


class Client(threading.Thread):
    def __init__(self, host="127.0.0.1", port=5000, buffer=4096, queue=None):
        threading.Thread.__init__(self)
        self._stop = threading.Event()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(2)

        self.buffer = buffer
        self.queue = queue

        self.events = {}
        self.threaded_events = {}

        try:
            self.client_socket.connect((host, port))
        except Exception as e:
            print 'Exception during connection', e
            sys.exit()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def send(self, event, data):
        msg = json.dumps({
            'event': event,
            'data': data
        })

        self.client_socket.send(msg)

    def on(self, event, cb, new_thread=False):
        if new_thread:
            if event not in self.threaded_events:
                self.threaded_events[event] = []
            self.threaded_events[event].append(cb)
        else:
            if event not in self.events:
                self.events[event] = []
            self.events[event].append(cb)

    def handle_message(self, message):
        try:
            event = message['event']
            data = message['data']
            if event in self.events:
                for cb in self.events[event]:
                    self.queue.put(lambda: cb(event, data))
            if event in self.threaded_events:
                for cb in self.threaded_events[event]:
                    runner.Runner(cb).start()
        except Exception as e:
            print 'Exception during handle message', e
            sys.stdout.flush()

    def run(self):
        l = listener.Listener(self.client_socket, self.buffer, self.handle_message)
        l.start()
