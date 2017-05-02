import pygslib
import sys
import random

screen_size = (640, 480)
screen_background = (0, 0, 0)
player_size = (32, 32)
players = {}

server = pygslib.server.Server()


class Player:
    def __init__(self, player_id, position, color=(0, 0, 0)):
        self.player_id = player_id
        self.position = position
        self.color = color

        self._x = 0
        self._y = 0

    def set_move_direction(self, x=None, y=None):
        if x is not None:
            self._x = x
        if y is not None:
            self._y = y

    def next_frame(self):
        self.position[0] += self._x
        self.position[1] += self._y
        return self._x != 0 or self._y != 0

    def to_msg(self):
        return {
            'id': self.player_id,
            'position': self.position,
            'color': self.color,
            'size': [32, 32]
        }


def create_player(client_id):
    global players

    x = random.randint(0, screen_size[0] - player_size[0])
    y = random.randint(0, screen_size[1] - player_size[1])
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    p = Player(player_id=client_id, position=[x, y], color=color)

    players[client_id] = p

    server.broadcast('new-player', {
        'player': p.to_msg()
    }, ignore_list=[client_id])

    other_players = {k: players[k].to_msg() for k in players if k != client_id}

    server.send('game-init', {
        'player': p.to_msg(),
        'other_players': other_players,
        'game': {
            'screen_size': screen_size,
            'screen_background': screen_background,
            'player_size': player_size
        },
        'client_id': client_id
    }, client_id)


def callback_new_connection(client_id):
    create_player(client_id)


def callback_client_message(client_id, event, data):
    global players

    if event == 'key_down':
        if data['key'] == 'left':
            players[client_id].set_move_direction(x=-1)
        elif data['key'] == 'right':
            players[client_id].set_move_direction(x=1)
        elif data['key'] == 'up':
            players[client_id].set_move_direction(y=-1)
        elif data['key'] == 'down':
            players[client_id].set_move_direction(y=1)
    elif event == 'key_up':
        if data['key'] == 'left':
            players[client_id].set_move_direction(x=0)
        elif data['key'] == 'right':
            players[client_id].set_move_direction(x=0)
        elif data['key'] == 'up':
            players[client_id].set_move_direction(y=0)
        elif data['key'] == 'down':
            players[client_id].set_move_direction(y=0)


def callback_frame():
    global players
    for player_id in players:
        if players[player_id].next_frame():
            server.broadcast('move-player', {
                'player': players[player_id].to_msg()
            })

server.set_client_message_callback(callback_client_message)
server.set_new_connection_callback(callback_new_connection)
server.set_frame_callback(callback_frame)

server.run(frame_rate=60)
