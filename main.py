import os
import random
import sys
from itertools import cycle
import pickle

import pygame


pygame.init()

GRAVITY = 0.1

KILL_BIRD = pygame.USEREVENT + 1
KILL_BIRD_EVENT = pygame.event.Event(KILL_BIRD)

ADD_SCORE = pygame.USEREVENT + 2
ADD_SCORE_EVENT = pygame.event.Event(ADD_SCORE)

ADD_COIN = pygame.USEREVENT + 3
ADD_COIN_EVENT = pygame.event.Event(ADD_COIN)


def load_audio():
    sounds = {}
    sound_prefix = "data/audio/"
    if "win" in sys.platform:
        sound_prefix += "wav/"
    else:
        sound_prefix += "ogg/"
    for file_name in os.listdir(sound_prefix):
        sound = pygame.mixer.Sound(sound_prefix + file_name)
        sound.set_volume(0.1)
        sounds[file_name.split(".")[0]] = sound
    return sounds


SOUNDS = load_audio()


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
    prefix = os.path.join("data/sprites", prefix)
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
            "day": load_image("data/sprites/back_ground/day.png"),
            "night": load_image("data/sprites/back_ground/night.png"),
        }
        self.image = self.images["day"]
        self.rect = self.image.get_rect()
        self.speed = 2

    def change_image(self, time_of_day: str):
        """
        Changes image of background
        """
        self.image = self.images[time_of_day]

    def set_x(self, x_pos: float):
        """
        Changes x pos of background image (we use 2 pics)
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
            "day": load_image("data/sprites/pipes/day.png"),
            "night": load_image("data/sprites/pipes/night.png"),
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
        Coin(self.rect.x - 23, self.rect.y - self.skylight // 2 - 12)

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
        self.rect.y = random.randint(200, 350)


class UpPipe(BasePipe):
    def __init__(self, down_x, down_y):
        super().__init__()
        self.images["day"] = pygame.transform.flip(self.images["day"], False, True)
        self.images["night"] = pygame.transform.flip(self.images["night"], False, True)
        self.image = self.images["day"]
        self.rect.x = down_x
        self.rect.y = down_y - self.skylight - self.rect.height

    def update(self):
        if not self.used and self.rect.x < 144:
            self.used = True
        if self.rect.x < -self.rect.width:
            self.kill()
        self.rect.x -= self.speed


class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, grounds)
        self.image = load_image("data/sprites/ground/ground.png")
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
        self.anim = load_animations("birds/" + self.color)
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
        SOUNDS["wing"].play()
        self.velocity = 2

    def change_color(self, color):
        self.color = color
        self.anim = load_animations("birds/" + self.color)
        self.image = next(self.anim)


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


class Score:
    def __init__(self, score, y_pos):
        self.score = score
        self.y_pos = y_pos
        self.images = {
            file_name[0]: load_image("data/sprites/nums/" + file_name)
            for file_name in os.listdir("data/sprites/nums")
        }
        self.digits = []

    def __add__(self, other):
        self.score += other

    def refresh(self):
        self.digits.clear()
        n = 0
        for num in str(self.score):
            digit = pygame.sprite.Sprite()
            digit.image = self.images[num]
            digit.rect = digit.image.get_rect()
            digit.rect.x = digit.image.get_width() * n
            digit.rect.y = self.y_pos
            n += 1
            self.digits.append(digit)

    def show(self):
        for digit in self.digits:
            screen.blit(digit.image, digit.rect)


all_sprites = pygame.sprite.Group()
pipes = pygame.sprite.Group()
backgrounds = pygame.sprite.Group()
grounds = pygame.sprite.Group()
coins = pygame.sprite.Group()
nums = pygame.sprite.Group()

pygame.font.init()
FONT = pygame.font.SysFont("Comic Sans MS", 15)

pygame.display.set_caption("Flappy Bird")
pygame.display.set_icon(load_image("data/sprites/ico/ico.ico"))

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
        self.prefix = "data/sprites/texts/"
        self.over = Text(48, 235, self.prefix + "gameover.png")
        self.title = Text(55, 50, self.prefix + "title.png")
        self.get_ready = Text(52, 150, self.prefix + "get_ready.png")
        self.button_shop = Button(94, 450, self.prefix + "shop.png")
        self.bird_yellow_button = Button(31, 130, "data/sprites/birds/yellow/1.png")
        self.bird_blue_button = Button(127, 130, "data/sprites/birds/blue/1.png")
        self.bird_red_button = Button(223, 130, "data/sprites/birds/red/1.png")

        self.button_shop.transform((100, 50))

        self.score = Score(0, 0)

        self.high_score, self.coins, color, self.shop_bought = self.load_data()
        bird.change_color(color)

        self.high_score_text = FONT.render(
            f"High score: {self.high_score}", False, (255, 0, 0)
        )
        self.coins_text = FONT.render(f"Coins: {self.coins}", False, (255, 0, 0))
        self.bought_text = FONT.render("Bought", False, (255, 0, 0))
        self.price_text = FONT.render("250 coins", False, (255, 0, 0))

        self.time = random.choice(["day", "night"])

        for background in backgrounds:
            background.change_image(self.time)
        SOUNDS["swoosh"].play()

    @staticmethod
    def load_data():
        with open("data/data.fbd", "rb") as f:
            data = pickle.load(f)
        return data

    def save_data(self):
        with open("data/data.fbd", "wb") as f:
            pickle.dump((self.high_score, self.coins, bird.color, self.shop_bought), f)

    def terminate(self):
        self.save_data()
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
            elif self.game_mode == "SHOP":
                self.game_mode = self.shop()

    def game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()

        if self.over.end:
            self.over.renew()
            pygame.time.wait(2000)
            for pipe in pipes:
                pipe.kill()
            for coin in coins:
                coin.kill()
            bird.rect.y = 256 - bird.rect.height // 2
            self.time = random.choice(["day", "night"])
            self.high_score_text = FONT.render(
                f"High score: {self.high_score}", False, (255, 0, 0)
            )
            self.coins_text = FONT.render(f"Coins: {self.coins}", False, (255, 0, 0))
            for background in backgrounds:
                background.change_image(self.time)
            return "MENU"

        self.over.update()

        all_sprites.draw(screen)
        nums.draw(screen)
        grounds.draw(screen)
        screen.blit(self.over.image, self.over.rect)
        screen.blit(self.high_score_text, (0, 475))

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
                    self.score.refresh()
                    for i in range(5):
                        dp = DownPipe()
                        dp.rect.x = 300 + dp.rect.x + 200 * i
                        if random.choices([True, False], k=1, weights=[1, 3])[0]:
                            dp.set_coin()
                        up = UpPipe(dp.rect.x, dp.rect.y)
                        dp.change_image(self.time)
                        up.change_image(self.time)
                    for background in backgrounds:
                        background.change_image(self.time)
                    return "GAME"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_shop.check():
                    bird.rect.x = -100
                    SOUNDS["swoosh"].play()
                    return "SHOP"

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

    def choose_bird(self, color):
        bird.change_color(color)
        bird.rect.x = 144 - bird.rect.width // 2
        self.bird_yellow_button.renew()
        self.bird_red_button.renew()
        self.bird_blue_button.renew()
        SOUNDS["swoosh"].play()

    def shop(self):
        txts = [
            (self.bought_text, 25, 165),
            (self.bought_text if self.shop_bought[1] else self.price_text, 110, 165),
            (self.bought_text if self.shop_bought[2] else self.price_text, 215, 165),
        ]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if all(
                    [
                        self.bird_yellow_button.end,
                        self.bird_blue_button.end,
                        self.bird_red_button.end,
                    ]
                ):
                    if self.bird_red_button.check():
                        if self.shop_bought[2]:
                            self.choose_bird("red")
                            return "MENU"
                        else:
                            if self.coins >= 250:
                                self.coins -= 250
                                self.shop_bought[2] = True
                                SOUNDS["bought"].play()
                    if self.bird_yellow_button.check():
                        if self.shop_bought[0]:
                            self.choose_bird("yellow")
                            return "MENU"
                    if self.bird_blue_button.check():
                        if self.shop_bought[1]:
                            self.choose_bird("blue")
                            return "MENU"
                        else:
                            if self.coins >= 250:
                                self.coins -= 250
                                self.shop_bought[1] = True
                                SOUNDS["bought"].play()

        if not self.bird_yellow_button.end:
            self.bird_yellow_button.update()

        if not self.bird_blue_button.end:
            self.bird_blue_button.update()

        if not self.bird_red_button.end:
            self.bird_red_button.update()

        all_sprites.draw(screen)
        screen.blit(self.bird_yellow_button.image, self.bird_yellow_button.rect)
        screen.blit(self.bird_blue_button.image, self.bird_blue_button.rect)
        screen.blit(self.bird_red_button.image, self.bird_red_button.rect)
        screen.blit(self.coins_text, (0, 475))

        for t in txts:
            screen.blit(t[0], (t[1], t[2]))

        pygame.display.update()
        return "SHOP"

    def game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
            elif event.type == ADD_COIN:
                self.coins += 1
                SOUNDS["collect_coin"].play()
            elif event.type == KILL_BIRD:
                SOUNDS["hit"].play()
                SOUNDS["die"].play()
                bird.velocity = 0
                if self.score.score > self.high_score:
                    self.high_score = self.score.score
                    self.high_score_text = FONT.render(
                        f"High score: {self.high_score}", False, (255, 0, 0)
                    )
                self.score.score = 0
                return "OVER"
            elif event.type == ADD_SCORE:
                SOUNDS["point"].play()
                dp = DownPipe()
                dp.rect.x = 150 + dp.rect.x + 200 * 5
                up = UpPipe(dp.rect.x, dp.rect.y)
                dp.change_image(self.time)
                up.change_image(self.time)
                if random.choices([True, False], k=1, weights=[1, 3])[0]:
                    dp.set_coin()
                self.score + 1
                self.score.refresh()
        all_sprites.update()
        all_sprites.draw(screen)
        grounds.draw(screen)
        self.score.show()
        pygame.display.update()
        return "GAME"


def main():
    game = GameHandler()
    game.start()


if __name__ == "__main__":
    main()
