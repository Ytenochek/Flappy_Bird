import os
import random
import sys
from itertools import cycle

import pygame


# import pickle
GRAVITY = 0.09

KILL_BIRD = pygame.USEREVENT + 1
KILL_BIRD_EVENT = pygame.event.Event(KILL_BIRD)

ADD_SCORE = pygame.USEREVENT + 2
ADD_SCORE_EVENT = pygame.event.Event(ADD_SCORE)

ADD_COIN = pygame.USEREVENT + 3
ADD_COIN_EVENT = pygame.event.Event(ADD_COIN)


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
        super().__init__(all_sprites, backgrounds)
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
        if self.rect.x <= -self.rect.width:
            self.rect.x = self.rect.width
        self.rect.x -= self.speed


class Coin(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__(all_sprites, coins)
        self.anim = load_animations("coins")
        self.image = next(self.anim)
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos
        self.transform()

        self.speed = 2

        self.start_tick = pygame.time.get_ticks()

    def update(self):
        seconds = (pygame.time.get_ticks() - self.start_tick) / 1000
        if seconds > 0.1:
            self.image = next(self.anim)
            self.transform()
            x, y = self.rect.centerx, self.rect.y
            self.rect = self.image.get_rect()
            self.rect.centerx, self.rect.y = x, y
            self.start_tick = pygame.time.get_ticks()

        if self.rect.x < -self.rect.width:
            self.kill()
        self.rect.x -= self.speed

    def transform(self):
        self.image = pygame.transform.scale(
            self.image,
            (self.image.get_rect().width // 4, self.image.get_rect().height // 4),
        )


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
        self.used = False

    def change_image(self, time_of_day: str):
        """
        Changes image of pipe
        """
        self.image = self.images[time_of_day]

    def set_coin(self):
        """
        Spawn coin between pipes
        """
        Coin(self.rect.centerx, self.rect.y + self.skylight // 2)

    def set_x(self, x_pos):
        self.rect.x = x_pos

    def update(self):
        if not self.used and self.rect.x < 144:
            pygame.event.post(ADD_SCORE_EVENT)
            self.used = True
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
        if self.rect.x <= -self.rect.width:
            self.rect.x = self.rect.width
        self.rect.x -= self.speed


class Bird(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__(all_sprites)
        self.color = color
        self.anim = load_animations("birds\\" + self.color)
        self.image = next(self.anim)
        self.rect = self.image.get_rect()
        self.rect.x = 144 - self.rect.width // 2
        self.rect.y = 256 - self.rect.height // 2
        self.velocity = 0

        self.start_tick = pygame.time.get_ticks()

    def update(self):
        coins_collided = pygame.sprite.spritecollide(self, coins, False)
        for coin in coins_collided:
            coin.kill()
            pygame.event.post(ADD_COIN_EVENT)

        ground_collided = pygame.sprite.spritecollide(self, grounds, False)
        pipes_collided = pygame.sprite.spritecollide(self, pipes, False)

        if ground_collided or pipes_collided:
            pygame.event.post(KILL_BIRD_EVENT)

        self.velocity -= GRAVITY
        seconds = (pygame.time.get_ticks() - self.start_tick) / 1000

        if seconds > 0.1:
            self.image = next(self.anim)
            self.start_tick = pygame.time.get_ticks()

        if self.rect.y <= 0:
            self.velocity = -15 * GRAVITY

        self.rect.y -= self.velocity

    def jump(self):
        self.velocity = 2


class Text(pygame.sprite.Sprite):
    def __init__(self, x_finish, y_finish, name):
        super().__init__()
        self.image = load_image(name)
        self.rect = self.image.get_rect()
        self.x_finish = x_finish
        self.rect.y = y_finish
        self.rect.x = -self.rect.width
        self.speed = 10
        self.end = False

    def update(self):
        if self.rect.x < self.x_finish:
            self.rect.move_ip(self.speed, 0)
        else:
            self.end = True

    def renew(self):
        self.rect.x = -self.rect.width
        self.end = False
        self.speed = 10
        self.end = False


class Button(pygame.sprite.Sprite):
    def __init__(self, x_finish, y_finish, name):
        super().__init__()
        self.image = load_image(name)
        self.rect = self.image.get_rect()
        self.x_finish = x_finish
        self.rect.y = y_finish
        self.rect.x = -self.rect.width
        self.speed = 10
        self.end = False

    def check(self):
        return self.rect.collidepoint(*pygame.mouse.get_pos())

    def transform(self, size):
        y_pos = self.rect.y
        self.image = pygame.transform.scale(self.image, size)
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = -self.rect.width
        self.rect.y = y_pos

    def update(self):
        if self.rect.x < self.x_finish:
            self.rect.move_ip(self.speed, 0)
        else:
            self.end = True

    def renew(self):
        self.rect.x = -self.rect.width
        self.end = False


all_sprites = pygame.sprite.Group()
pipes = pygame.sprite.Group()
backgrounds = pygame.sprite.Group()
grounds = pygame.sprite.Group()
coins = pygame.sprite.Group()

pygame.init()
pygame.display.set_caption("Flappy Bird")
pygame.display.set_icon(load_image("data\\sprites\\ico\\ico.ico"))

clock = pygame.time.Clock()

screen = pygame.display.set_mode((288, 512))

Background()
b = Background()
b.set_x(b.rect.width)

Ground()
g = Ground()
g.set_x(g.rect.width)
bird = Bird("yellow")


class GameHandler:
    def __init__(self):
        self.game_mode = "MENU"
        self.prefix = "data\\sprites\\texts\\"
        self.over = Text(48, 235, self.prefix + "gameover.png")
        self.title = Text(55, 50, self.prefix + "title.png")
        self.get_ready = Text(52, 150, self.prefix + "get_ready.png")
        self.button_shop = Button(94, 450, self.prefix + "shop.png")

        self.button_shop.transform((100, 50))

    @staticmethod
    def terminate():
        pygame.quit()
        sys.exit()

    def start(self):
        while True:
            clock.tick(60)
            if self.game_mode == "MENU":
                self.game_mode = self.main_menu()
            elif self.game_mode == "GAME":
                self.game_mode = self.game()
            elif self.game_mode == "OVER":
                self.game_mode = self.game_over()

    def game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()

        if self.over.end:
            self.over.renew()
            pygame.time.wait(1000)
            bird.rect.y = 256 - bird.rect.height // 2
            return "MENU"

        self.over.update()

        all_sprites.draw(screen)
        screen.blit(self.over.image, self.over.rect)

        pygame.display.update()

        return "OVER"

    def main_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.title.renew()
                    self.get_ready.renew()
                    self.button_shop.renew()
                    bird.jump()
                    return "GAME"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print(self.button_shop.check())

        if not self.title.end:
            self.title.update()

        if not self.button_shop.end:
            self.button_shop.update()

        if not self.get_ready.end:
            self.get_ready.update()

        all_sprites.draw(screen)
        screen.blit(self.title.image, self.title.rect)
        screen.blit(self.get_ready.image, self.get_ready.rect)
        screen.blit(self.button_shop.image, self.button_shop.rect)

        pygame.display.update()
        return "MENU"

    def game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
            elif event.type == ADD_COIN:
                pass
            elif event.type == KILL_BIRD:
                bird.velocity = 0
                return "OVER"
            elif event.type == ADD_SCORE:
                pass
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.update()
        return "GAME"


def main():
    game = GameHandler()
    game.start()


if __name__ == "__main__":
    main()
