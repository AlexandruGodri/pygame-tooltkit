import time
import pygame


class Game():
    def __init__(self):
        self._size = None
        self._background = None
        self.screen = None
        self.sprites = pygame.sprite.Group()
        self.events = {}

        self._ready = False

    def init(self, size, background):
        self._size = size
        self._background = background

        pygame.init()

        self.screen = pygame.display.set_mode(size)
        self.screen.fill(background)

    def ready(self):
        self._ready = True

    def create_image_sprite(self, img_path, position, angle, size):
        try:
            img = pygame.sprite.Sprite()
            img.image = pygame.Surface(size)
            img.image = pygame.image.load(img_path).convert_alpha()
            img.image = pygame.transform.rotate(img.image, angle)
            img.rect = img.image.get_rect()
            img.rect.x = position[0]
            img.rect.y = position[1]
            self.sprites.add(img)
            return img
        except Exception as e:
            print 'Error Adding Image', e, img_path, position, size, angle
            return None

    def create_rectangle(self, color, position, size):
        try:
            img = pygame.sprite.Sprite()
            img.image = pygame.Surface(size)
            img.image.fill(color)
            img.rect = img.image.get_rect()
            img.rect.x = position[0]
            img.rect.y = position[1]
            self.sprites.add(img)
            return img
        except Exception as e:
            print 'Error Adding Rectangle', e, position, size
            return None

    def move_sprite(self, sprite, position=None, angle=None):
        if sprite in self.sprites:
            if angle is not None:
                orig_rect = sprite.image.get_rect()
                rot_image = pygame.transform.rotate(sprite.image, angle)
                rot_rect = orig_rect.copy()
                rot_rect.center = rot_image.get_rect().center
                sprite.image = rot_image.subsurface(rot_rect).copy()
            if position is not None:
                sprite.rect.x = position[0]
                sprite.rect.y = position[1]

    def render(self):
        self.screen.fill(self._background)
        self.sprites.update()
        self.sprites.draw(self.screen)
        pygame.display.flip()

    def on(self, event, cb):
        if event not in self.events:
            self.events[event] = []

        self.events[event].append(cb)

    def run(self):
        while not self._ready:
            time.sleep(0.01)

        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if self._ready:
                    if event.type in self.events:
                        for cb in self.events[event.type]:
                            cb(event)

            if self._ready:
                try:
                    self.render()
                except Exception as e:
                    pass
            clock.tick(60)
