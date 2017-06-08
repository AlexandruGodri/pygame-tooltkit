import pygslib
import sys
import random


host = '0.0.0.0'
if len(sys.argv) >= 2:
    host = sys.argv[1]

port = 5000
if len(sys.argv) >= 3:
    port = int(sys.argv[2])

screen_size = (640, 480)
screen_background = (0, 0, 0)
player_size = (16, 16)
brick_size = (32, 32)
players = {}

server = pygslib.server.Server(host=host, port=port)

bricks = []


def collision(source, target):
    if type(target) is not list:
        target = [target]

    for item in target:
        if item is source: continue

        if (source.position[0] > item.position[0] - source.size[0] and source.position[0] < item.position[0] + item.size[0]) and \
                (source.position[1] > item.position[1] - source.size[1] and source.position[1] < item.position[1] + item.size[1]):
            print source.to_msg()
            print item.to_msg()
            sys.stdout.flush()
            return True

    return False


class BaseRect(object):
    def __init__(self, position, color, size):
        self.position = position
        self.color = color
        self.size = size

    def to_msg(self):
        return {
            'position': self.position,
            'color': self.color,
            'size': self.size
        }


class Brick(BaseRect):
    def __init__(self, position, color=(0, 0, 0), size=(16, 16)):
        super(Brick, self).__init__(position, color, size)


class Player(BaseRect):
    def __init__(self, player_id, position, color=(0, 0, 0), size=(16, 16)):
        super(Player, self).__init__(position, color, size)
        self.player_id = player_id

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

        if collision(self, bricks + players.values()):
            self.position[0] -= self._x
            self.position[1] -= self._y
            self._x = 0
            self._y = 0

        return self._x != 0 or self._y != 0

    def to_msg(self):
        return {
            'id': self.player_id,
            'position': self.position,
            'color': self.color,
            'size': self.size
        }


def create_player(client_id):
    global players
    print 'create player'
    sys.stdout.flush()

    color = (random.randint(0, 150), random.randint(100, 255), random.randint(50, 200))
    while True:
        try:
            x = random.randint(0, screen_size[0] - player_size[0])
            y = random.randint(0, screen_size[1] - player_size[1])
            p = Player(player_id=client_id, position=[x, y], color=color)
            if not collision(p, bricks + players.values()):
                break
        except Exception as e:
            print 'exp', e
            sys.stdout.flush()

    print 'player generated'
    print p
    sys.stdout.flush()

    try:
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
            'bricks': [b.to_msg() for b in bricks],
            'client_id': client_id
        }, client_id)
    except Exception as e:
        print 'zcxz', e
        sys.stdout.flush()


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

for i in range(30):
    while True:
        size = random.randint(16, 32)
        x = random.randint(0, screen_size[0] - size)
        y = i * 32
        color = (255, 255, 255)
        b = Brick(position=(x, y), color=color, size=(size, size))
        print b
        sys.stdout.flush()
        if not collision(b, bricks):
            break
    bricks.append(b)

print len(bricks)
sys.stdout.flush()

server.run(frame_rate=60)
