import pygame
import os
import time
import random

pygame.font.init()

WIDTH = 640
HEIGHT = 480

ship_scale = [int(WIDTH * 0.05), int(HEIGHT * 0.05)]
laser_scale = [int(WIDTH * 0.05), int(HEIGHT * 0.05)]

# Canvas for the game
pygame.display.set_icon(pygame.image.load("./graphics/blueship.png"))
CANVAS = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space shooter")

BG = pygame.transform.scale(
    pygame.image.load("./graphics/background.png"), (WIDTH, HEIGHT)
)
pygame.display.update()

# Ships
RED_SPACESHIP = pygame.transform.rotate(
    pygame.transform.scale(pygame.image.load("./graphics/redship.png"), ship_scale), 180
)
BLUE_SPACESHIP = pygame.transform.rotate(
    pygame.transform.scale(pygame.image.load("./graphics/blueship.png"), ship_scale),
    180,
)
GREEN_SPACESHIP = pygame.transform.rotate(
    pygame.transform.scale(pygame.image.load("./graphics/greenship.png"), ship_scale),
    180,
)
PLAYER_SPACESHIP = pygame.transform.scale(
    pygame.image.load("./graphics/playership.png"), ship_scale
)

# Weapons
ENEMY_LASER = pygame.transform.scale(
    pygame.image.load("./graphics/enemylaser.png"), laser_scale
)
PLAYER_LASER = pygame.transform.scale(
    pygame.image.load("./graphics/playerlaser.png"), laser_scale
)

player_location = [(WIDTH / 2), (HEIGHT / 4 * 3)]
red_location = [random.randint(0, WIDTH), 100]
blue_location = [random.randint(0, WIDTH), 100]
green_location = [random.randint(0, WIDTH), 100]


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(
                int(
                    (self.x + self.ship_img.get_width() / 2)
                    - self.laser_img.get_width() / 2
                ),
                int(self.y - self.ship_img.get_height() / 2),
                self.laser_img,
            )
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SPACESHIP
        self.laser_img = PLAYER_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(
            window,
            (255, 0, 0),
            (
                self.x,
                self.y + self.ship_img.get_height() + 5,
                self.ship_img.get_width(),
                10,
            ),
        )
        pygame.draw.rect(
            window,
            (0, 255, 0),
            (
                self.x,
                self.y + self.ship_img.get_height() + 5,
                int(self.ship_img.get_width() * (self.health / self.max_health)),
                10,
            ),
        )


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACESHIP),
        "green": (GREEN_SPACESHIP),
        "blue": (BLUE_SPACESHIP),
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img = self.COLOR_MAP[color]
        self.laser_img = ENEMY_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_healt = health

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 50
    level = 0
    lives = 4
    main_font = pygame.font.SysFont("arial", 25)
    lost_font = pygame.font.SysFont("helvetica", 70)

    lives_font = pygame.font.SysFont("comic", 30)

    enemies = []
    wave_lenght = 0
    enemy_vel = 1

    player_vel = 5
    laser_vel = 4

    player = Player(300, 350)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    lostlife = 0
    gainedlife = 0
    counter_3sec = 3 * FPS
    counter_2sec = 2 * FPS

    def update_canvas():
        CANVAS.blit(BG, (0, 0))

        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        enemies_label = main_font.render(f"Enemies: {len(enemies)}", 1, (255, 255, 255))

        CANVAS.blit(lives_label, (10, HEIGHT - 40))
        CANVAS.blit(level_label, (10, 10))
        CANVAS.blit(enemies_label, (WIDTH - enemies_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(CANVAS)

        player.draw(CANVAS)

        if lost:
            lost_label = lost_font.render("Game Over", 1, (213, 16, 129))
            CANVAS.blit(
                lost_label, (int(WIDTH / 2 - lost_label.get_width() / 2), int(HEIGHT / 2))
            )

        if lostlife > 0:
            lives_lostlbl = lives_font.render("A life was lost", 1, (200, 50, 50))
            CANVAS.blit(lives_lostlbl, (int(WIDTH / 2 - lives_lostlbl.get_width() / 2), 30))

        if gainedlife > 0:
            lives_gainedlbl = lives_font.render(
                "A life was given for new level", 1, (50, 200, 50)
            )
            CANVAS.blit(
                lives_gainedlbl, (int(WIDTH / 2 - lives_gainedlbl.get_width() / 2), 50)
            )

        pygame.display.update()

    while run:
        clock.tick(FPS)

        update_canvas()

        if gainedlife > 0:
            gainedlife -= 1

        if lostlife > 0:
            lostlife -= 1

        if player.health <= 0:
            lives -= 1
            lostlife = counter_2sec
            player.health = player.max_health

        if lives <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > counter_3sec:
                run = False
            else:
                continue

        if len(enemies) == 0:
            FPS += 1
            level += 1
            gainedlife = counter_3sec
            lives += 1
            wave_lenght += 5
            for i in range(wave_lenght):
                enemy = Enemy(
                    random.randrange(30, WIDTH - 30),
                    random.randrange(-1500, -100),
                    random.choice(["red", "green", "blue"]),
                )
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and player.x - player_vel > 0:  # Left
            player.x -= player_vel
        if (
            keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH
        ):  # Right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # Up
            player.y -= player_vel
        if (
            keys[pygame.K_s]
            and player.y + player_vel + player.get_height() + player.get_height() / 2
            < HEIGHT
        ):  # Down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 3 * FPS) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                lostlife = counter_2sec
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        CANVAS.blit(BG, (0, 0))
        title_label = title_font.render(
            "Press mousebutton to begin...", 1, (255, 255, 255)
        )
        CANVAS.blit(title_label, (int(WIDTH / 2 - title_label.get_width() / 2), int(HEIGHT / 2)))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()


main_menu()
