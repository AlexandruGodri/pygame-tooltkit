import os
import sys
import pygclib
import game
import pygame
from Queue import *
from pygclib.runner import Runner


q = Queue()

client = pygclib.client.Client(queue=q)
game_instance = None
player_sprite = None
players = {}

key_mappings = {
    pygame.K_LEFT: 'left',
    pygame.K_RIGHT: 'right',
    pygame.K_UP: 'up',
    pygame.K_DOWN: 'down'
}


def handle_key_down(event):
    if event.key in key_mappings:
        client.send('key_down', {'key': key_mappings[event.key]})


def handle_key_up(event):
    if event.key in key_mappings:
        client.send('key_up', {'key': key_mappings[event.key]})


def defer_game_init(*args):
    global game_instance, player_sprite, client, players

    event = args[0]
    data = args[1]

    game_instance.init(data['game']['screen_size'], data['game']['screen_background'])
    player_sprite = game_instance.create_rectangle(color=data['player']['color'], position=data['player']['position'], size=data['game']['player_size'])
    players[str(data['client_id'])] = player_sprite

    other_players = data['other_players']
    for player_id in other_players:
        p = other_players[player_id]
        players[str(player_id)] = game_instance.create_rectangle(color=p['color'], position=p['position'], size=p['size'])

    game_instance.ready()
    game_instance.run()


def handle_game_init(*args):
    Runner(callback=defer_game_init, args=args).start()


def handle_new_player(event, data):
    global game_instance, client, players

    players[str(data['player']['id'])] = game_instance.create_rectangle(
        color=data['player']['color'],
        position=data['player']['position'],
        size=data['player']['size'])


def handle_move_player(event, data):
    global game_instance, players
    try:
        game_instance.move_sprite(players[str(data['player']['id'])], position=data['player']['position'])
    except Exception as e:
        print 'Exception during move player', e


client.on('game-init', handle_game_init, new_thread=False)
client.on('new-player', handle_new_player)
client.on('move-player', handle_move_player)

client.start()

game_instance = game.game.Game()

game_instance.on(pygame.KEYDOWN, handle_key_down)
game_instance.on(pygame.KEYUP, handle_key_up)

while True:
    method = q.get()
    try:
        method()
    except Exception as e:
        print 'Exception during event execution', e
        sys.stdout.flush()
