import socket
import json
import sys
import time
import connection
import listener
import frame


class Server:
    def __init__(self,
                 host="127.0.0.1",
                 port=5000,
                 buffer=4096):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(10)

        self.listeners = []
        self.connection_ids = {}
        self.connection_ids_reverse = {}
        self.buffer = buffer

        self.callback_new_connection = None
        self.callback_client_message = None
        self.callback_frame = None

    def set_new_connection_callback(self, cb):
        self.callback_new_connection = cb

    def set_client_message_callback(self, cb):
        self.callback_client_message = cb

    def set_frame_callback(self, cb):
        self.callback_frame = cb

    def send(self, event, data, sock_id):
        message = json.dumps({
            'event': event,
            'data': data
        })

        s = self.connection_ids[sock_id]
        try:
            s.send(message)
        except Exception as e:
            print 'Could not emit message (send) ', message, ' - socket - ', s
            s.close()

    def broadcast(self, event, data, ignore_list=None):
        if ignore_list is None:
            ignore_list = []

        message = json.dumps({
            'event': event,
            'data': data
        })

        for s in self.connection_ids:
            if s in ignore_list:
                continue

            try:
                self.connection_ids[s].send(message)
            except Exception as e:
                print 'Could not emit message (broadcast) ', message, ' - socket - ', self.connection_ids[s]
                sys.stdout.flush()
                self.connection_ids[s].close()

    def handle_new_connection(self, sock, conn_id):
        self.connection_ids[conn_id] = sock
        self.connection_ids_reverse[sock] = conn_id

        if self.callback_new_connection is not None:
            self.callback_new_connection(client_id=conn_id)

        l = listener.Listener(sock, self.buffer, self.handle_client_message)
        l.start()
        self.listeners.append(l)


    def handle_client_message(self, sock, data):
        client_id = self.connection_ids_reverse[sock]
        event = data['event']
        data = data['data']
        self.callback_client_message(client_id, event, data)

    def run(self, frame_rate=30):
        self.connection = connection.Connection(sock=self.server_socket, callback=self.handle_new_connection)
        self.connection.start()

        self.frame = frame.Frame(frame_rate=frame_rate, callback=self.callback_frame)
        self.frame.start()
