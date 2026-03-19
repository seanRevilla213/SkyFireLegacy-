import pygame

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800

TYPE_SMALL = 1
TYPE_MIDDLE = 2
TYPE_BIG = 3


# Bullet Class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_img, init_pos):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.midbottom = init_pos
        self.speed = 10

    def move(self):
        self.rect.top -= self.speed


# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self, plane_img, player_rects, init_pos):
        super().__init__()

        self.images = []
        for rect in player_rects:
            self.images.append(plane_img.subsurface(rect).convert_alpha())

        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = init_pos

        self.speed = 8
        self.bullets = pygame.sprite.Group()
        self.img_index = 0
        self.is_hit = False

    def shoot(self, bullet_img):
        bullet = Bullet(bullet_img, self.rect.midtop)
        self.bullets.add(bullet)

    def move_up(self):
        self.rect.top = max(self.rect.top - self.speed, 0)

    def move_down(self):
        self.rect.top = min(self.rect.top + self.speed,
                            SCREEN_HEIGHT - self.rect.height)

    def move_left(self):
        self.rect.left = max(self.rect.left - self.speed, 0)

    def move_right(self):
        self.rect.left = min(self.rect.left + self.speed,
                             SCREEN_WIDTH - self.rect.width)


# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_img, enemy_down_imgs, init_pos):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.topleft = init_pos
        self.down_imgs = enemy_down_imgs
        self.speed = 2
        self.down_index = 0

    def move(self):
        self.rect.top += self.speed