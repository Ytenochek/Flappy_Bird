import os
import random
import sys
from itertools import cycle

import pygame


# import pickle


def load_image(fullname: str) -> pygame.Surface:
    """
    Return a pygame.Surface (image) for sprites
    """
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_animations(prefix: str) -> cycle:
    """
    Returns endless iterator of pygame.Surface for sprite's animation
    """
    animations = []
    prefix = os.path.join("data\\sprites", prefix)
    for name in os.listdir(prefix):
        path = os.path.join(prefix, name)
        if os.path.isfile(path):
            animations.append(load_image(path))
    return cycle(animations)


class Background(pygame.sprite.Sprite):
    """
    Endless moving background
    """

    def __init__(self):
        super().__init__(all_sprites)
        self.images = {
            "day": load_image("data\\sprites\\back_ground\\day.png"),
            "night": load_image("data\\sprites\\back_ground\\night.png"),
        }
        self.image = self.images["day"]
        self.rect = self.image.get_rect()
        self.speed = 2

    def change_image(self, time_of_day: str):
        """
        Changes image of backgruond
        """
        self.image = self.images[time_of_day]

    def set_x(self, x_pos: float):
        """
        Changes x pos of backgroung image (we use 2 pics)
        """
        self.rect.x = x_pos

    def update(self):
        if self.rect.x < -self.rect.width:
            self.rect.x = self.rect.width
        self.rect.x -= self.speed


class BasePipe(pygame.sprite.Sprite):
    """
    Barriers which you should dodge
    """

    def __init__(self):
        super().__init__(all_sprites, pipes)
        self.images = {
            "day": load_image("data\\sprites\\pipes\\day.png"),
            "night": load_image("data\\sprites\\pipes\\night.png"),
        }
        self.image = self.images["day"]
        self.rect = self.image.get_rect()
        self.speed = 2
        self.skylight = 100  # Distance between two pipes

    def change_image(self, time_of_day: str):
        """
        Changes image of pipe
        """
        self.image = self.images[time_of_day]

    def set_coin(self):
        """
        Spawn coin between pipes
        """
        pass

    def set_x(self, x_pos):
        self.rect.x = x_pos

    def update(self):
        if self.rect.x < -self.rect.width:
            self.kill()
        self.rect.x -= self.speed


class DownPipe(BasePipe):
    def __init__(self):
        super().__init__()
        self.set_y()

    def set_y(self):
        self.rect.y = random.randint(100, 350)
        UpPipe(self.rect.x, self.rect.y)


class UpPipe(BasePipe):
    def __init__(self, down_x, down_y):
        super().__init__()
        self.images["day"] = pygame.transform.flip(self.images["day"], False, True)
        self.images["night"] = pygame.transform.flip(self.images["night"], False, True)
        self.image = self.images["day"]
        self.rect.x = down_x
        self.rect.y = down_y - self.skylight - self.rect.height


class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, grounds)
        self.image = load_image("data\\sprites\\ground\\ground.png")
        self.rect = self.image.get_rect()
        self.rect.y = 400
        self.speed = 2

    def set_x(self, x_pos: float):
        """
        Changes x pos of ground image (we use 2 pics)
        """
        self.rect.x = x_pos

    def update(self):
        if self.rect.x < -self.rect.width:
            self.rect.x = self.rect.width
        self.rect.x -= self.speed


all_sprites = pygame.sprite.Group()
pipes = pygame.sprite.Group()
grounds = pygame.sprite.Group()


def main():
    pygame.init()
    pygame.display.set_caption("Flappy Bird")

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((288, 512))

    Background()
    b = Background()
    b.set_x(b.rect.width)

    Ground()
    g = Ground()
    g.set_x(g.rect.width)

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
