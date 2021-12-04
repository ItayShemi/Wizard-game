import random
import sys
import pygame
import os
import csv
# from pygame import mixer

pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('game')


# set framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75

# define player action variables
moving_left = False
moving_right = False
shoot = False
shoot_lighting = False
FIRE = False
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 16
cooldown_tracker = 0
ability = False
timer_event = pygame.USEREVENT+1
pygame.time.set_timer(timer_event, 1000)
counter, text = 10, '10'.rjust(3)
pygame.time.set_timer(pygame.USEREVENT, 1000)
font = pygame.font.SysFont('Consolas', 30)
bg_scroll = 0
screen_scroll = 0
SCROLL_THRESH = 200
lighting_bolt = False

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# load images
Fire_img = pygame.image.load('img/Icon/fire.png').convert_alpha()
fire_img = pygame.transform.scale(Fire_img, (int(Fire_img.get_width() * 0.07), int(Fire_img.get_height() * 0.07)))
Fire_dragon_img = pygame.transform.scale(Fire_img, (int(Fire_img.get_width() * 0.11), int(Fire_img.get_height() * 0.11)))
ice_ball_img = pygame.image.load('img/Icon/ice_ball.png').convert_alpha()
Ice_ball_img = pygame.transform.scale(ice_ball_img, (int(ice_ball_img.get_width() * 0.12), int(ice_ball_img.get_height() * 0.12)))

exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
start_img = pygame.image.load('img/start_btn.png').convert_alpha()

Enegy_img = pygame.image.load('img/Icon/ball_attack.png').convert_alpha()
enegy_img = pygame.transform.scale(Enegy_img, (int(Enegy_img.get_width() * 0.1), int(Enegy_img.get_height() * 0.1)))
Potion_img = pygame.image.load('img/Icon/potion.png').convert_alpha()
potion_img = pygame.transform.scale(Potion_img, (int(Potion_img.get_width() * 0.105), int(Potion_img.get_height() * 0.105)))
Lightning_bolt_img = pygame.image.load('img/Icon/lightning_bolt.png').convert_alpha()
lightning_bolt_img = pygame.transform.scale(Lightning_bolt_img, (int(Lightning_bolt_img.get_width() * 0.5), int(Lightning_bolt_img.get_height() * 0.7)))



pine1_img = pygame.image.load('img/Backgrounds/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Backgrounds/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Backgrounds/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Backgrounds/sky_cloud.png').convert_alpha()

item_boxes = {
    'Health': potion_img
}


# define colours
BG = (88, 214, 141)
RED = (255, 0, 0)
Blue = (57, 139, 198)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))




# button class
class Button():
    def __init__(self,x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action




class Wizard(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, health):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.shoot_cooldown = 0
        self.health = health
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.hits = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.finish = False
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # load all images for the players
        animation_types = ['Idle', 'run', 'jump', 'death', 'attack']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
        screen_scroll = 0

        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
            wizard.update_action(1)  # 1: run


        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
            wizard.update_action(1)  # 1: run


        # jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            var = self.vel_y
        dy += self.vel_y



        # check collision with floor
        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

            # check if going off the edges of the screen
            if self.char_type == 'wizard':
                if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                    dx = 0


            # check if fallen off the map
            if self.rect.bottom > SCREEN_HEIGHT:
                self.health = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy


        if self.char_type == 'wizard':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (
                    world.level_length * TILE_SIZE) - SCREEN_WIDTH):
                self.rect.x -= dx
                screen_scroll = -dx



        return screen_scroll


    def shoot(self):
        if self.shoot_cooldown == 0:
            # wizard.update_action(4)
            # mixer.init()
            # mixer.music.load('img/sound_effect/Fireball.mp3')
            # mixer.music.play()

            if self.shoot_cooldown == 0:
                self.shoot_cooldown = 20
                bullet = FIRE_BALL(self.rect.centerx + (0.7 * self.rect.size[0] * self.direction),
                                self.rect.centery - 20,
                                self.direction)
                fire_ball_group.add(bullet)


    def shoot_lightning(self):
        if self.shoot_cooldown == 0:
            # mixer.init()
            # mixer.music.load('img/sound_effect/Fireball.mp3')
            # mixer.music.play()

            if self.shoot_cooldown == 0:
                self.shoot_cooldown = 20
                bullet = LIGHTINING_BOLT(self.rect.centerx + (0.67 * self.rect.size[0] * self.direction),
                                self.rect.centery - 20,
                                self.direction)
                lightning_bolt_group.add(bullet)
    

    def special_ability(self):
        self.health = self.max_health


    def update_animation(self):
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                """
            if self.action == 4:
                self.finish = True
            if self.finish == True:
                self.update_action(0)
                """

        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)




    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    def ai(self):
        if self.alive and wizard.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)# 0: idle
                self.idling = True
                self.idling_counter = 50
            # check if the ai in near the player
            if self.vision.colliderect(wizard.rect):
                # stop running and face the player
                self.update_action(0)# 0: idle
                # shoot
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)#1: run
                    self.move_counter += 1
                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        self.rect.x += screen_scroll










class Dragon(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        self.shoot_cooldown = 0

        # load all images for the players
        animation_types = ['fly']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            self.shoot()
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            self.shoot()
            dx = self.speed
            self.flip = False
            self.direction = 1


        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 130
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


    def shoot(self):
        if self.shoot_cooldown == 0:
            # mixer.init()
            # mixer.music.load('img/sound_effect/Fireball.mp3')
            # mixer.music.play()

            bullet = FIRE_BALL_Dragon(self.rect.centerx + (0.4 * self.rect.size[0] * self.direction),
                            self.rect.centery - 10,
                            self.direction)
            bullet1 = FIRE_BALL_Dragon(self.rect.centerx + (0.4 * self.rect.size[0] * self.direction),
                                      self.rect.centery - 10,
                                      self.direction)
            bullet2 = FIRE_BALL_Dragon(self.rect.centerx + (0.4 * self.rect.size[0] * self.direction),
                                      self.rect.centery - 10,
                                      self.direction)
            fire_ball_dragon_group.add(bullet)
            fire_ball_dragon_group.add(bullet1)
            fire_ball_dragon_group.add(bullet2)

            self.shoot_cooldown = 20


    def ai(self):
        if self.direction == 1:
            ai_moving_right = True
            self.shoot()
        else:
            ai_moving_right = False
            self.shoot()


        ai_moving_left = not ai_moving_right

        self.move(ai_moving_left, ai_moving_right)
        self.move_counter += 1

        if self.move_counter > TILE_SIZE:
            self.direction *= -1
            self.move_counter *= -1
            self.shoot()


        self.rect.x += screen_scroll


class Wizard_boss(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, health):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.shoot_cooldown = 0
        self.health = health
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.hits = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.finish = False
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        self.game_win = False

        # load all images for the players
        animation_types = ['Idle', 'run', 'jump', 'death', 'attack']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # reset movement variables
        screen_scroll = 0

        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
            wizard.update_action(1)  # 1: run

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
            wizard.update_action(1)  # 1: run

        # jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            var = self.vel_y
        dy += self.vel_y

        # check collision with floor
        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

            # check if going off the edges of the screen
            if self.char_type == 'wizard':
                if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                    dx = 0

            # check if fallen off the map
            if self.rect.bottom > SCREEN_HEIGHT:
                self.health = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        if self.char_type == 'wizard':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (
                    world.level_length * TILE_SIZE) - SCREEN_WIDTH):
                self.rect.x -= dx
                screen_scroll = -dx

            if (self.rect.left < SCREEN_WIDTH - SCROLL_THRESH and bg_scroll <
                    (world.level_length * TILE_SIZE) - SCREEN_WIDTH):
                self.rect.x += dx
                screen_scroll = +dx

        return screen_scroll

    def shoot(self):
        if self.shoot_cooldown == 0:
            # wizard.update_action(4)
            # mixer.init()
            # mixer.music.load('img/sound_effect/Fireball.mp3')
            # mixer.music.play()

            if self.shoot_cooldown == 0:
                self.shoot_cooldown = 20
                bullet = Ice_ball(self.rect.centerx + (0.7 * self.rect.size[0] * self.direction),
                                   self.rect.centery - 20,
                                   self.direction)
                ice_ball_group.add(bullet)

    def shoot_lightning(self):
        if self.shoot_cooldown == 0:
            # mixer.init()
            # mixer.music.load('img/sound_effect/Fireball.mp3')
            # mixer.music.play()

            if self.shoot_cooldown == 0:
                self.shoot_cooldown = 20
                bullet = LIGHTINING_BOLT(self.rect.centerx + (0.67 * self.rect.size[0] * self.direction),
                                         self.rect.centery - 20,
                                         self.direction)
                lightning_bolt_group.add(bullet)


    def update_animation(self):
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)
            self.game_win = True

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    def ai(self):
        if self.alive and wizard.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50
            # check if the ai in near the player
            if self.vision.colliderect(wizard.rect):
                # stop running and face the player
                self.update_action(0)  # 0: idle
                # shoot
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1
                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        self.rect.x += screen_scroll


class Ice_ball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 7
        self.image = Ice_ball_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed)
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
      #check collision with characters
        if pygame.sprite.spritecollide(wizard, ice_ball_group, False):
            if wizard.alive:
                wizard.health -= 13
                self.kill()





class FIRE_BALL_Dragon(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 7
        self.image = Fire_dragon_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
    def update(self):
        r = random.randint(2, 45)
        #move bullet
        self.rect.x += (self.direction * self.speed)
        self.rect.y += r
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
      #check collision with characters
        if pygame.sprite.spritecollide(wizard, fire_ball_dragon_group, False):
            for boss in boss_group:
                if boss.alive == True:
                    if wizard.alive:
                        wizard.health -= 20
                        self.kill()





class FIRE_BALL(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = fire_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed)
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()


        #check collision with characters
        if pygame.sprite.spritecollide(wizard, fire_ball_group, False):
            if wizard.alive:
                wizard.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, fire_ball_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()

        for boss in boss_group:
            if pygame.sprite.spritecollide(boss, fire_ball_group, False):
                if boss.alive:
                    boss.health -= 25
                    self.kill()







class LIGHTINING_BOLT(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = lightning_bolt_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed)
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()


        #check collision with characters
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, lightning_bolt_group, False):
                if enemy.alive:
                    enemy.health -= 36
                    self.kill()

        for boss in boss_group:
            if pygame.sprite.spritecollide(boss, lightning_bolt_group, False):
                if boss.alive:
                    boss.health -= 40
                    self.kill()



class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


    def update(self):
        #check if the player has picked up the box
        if pygame.sprite.collide_rect(self, wizard):
            #check what kind of box it was
            if self.item_type == 'Health':
                if wizard.alive:
                    wizard.health += 25
                    if wizard.health > wizard.max_health:
                        wizard.health = wizard.max_health

            self.kill()

        self.rect.x += screen_scroll


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #update with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))



class World():

    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        # iterate through each value in level data file
        self.level_length = len(data[0])

        global wizard, health_bar
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 3:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 4 and tile <= 7:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 8:  # create player
                        wizard = Wizard('wizard', x * TILE_SIZE, y * TILE_SIZE, 0.2, 4, 250)
                        health_bar = HealthBar(10, 10, wizard.health, wizard.health)
                    elif tile == 9:  # create enemies
                        enemy = Wizard('enemy', x * TILE_SIZE, y * TILE_SIZE, 0.2, 2, 100)
                        enemy_group.add(enemy)
                    elif tile == 10:  # create health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 11:  # create health box
                        dragon = Dragon('dragon', x * TILE_SIZE, y * TILE_SIZE, 1.8, 5)
                        dragon_group.add(dragon)
                    elif tile == 12:
                        tree = Tree1(img, x * TILE_SIZE, y * TILE_SIZE)
                        tree1_group.add(tree)
                    elif tile >= 13 and tile <= 14:
                        tree = Tree2(img, x * TILE_SIZE, y * TILE_SIZE)
                        tree2_group.add(tree)
                    elif tile == 15:
                        boss = Wizard_boss('wizard_boss', x * TILE_SIZE, y * TILE_SIZE, 0.2, 2, 500)
                        boss_group.add(boss)

        return wizard, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])



class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Tree1(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(img, (int(img.get_width() * 6), int(img.get_height() * 6)))
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Tree2(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(img, (int(img.get_width() * 5.), int(img.get_height() * 10)))
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll



wizard = Wizard('wizard', 200, 200, 0.2, 4, 250)
health_bar = HealthBar(10, 10, wizard.health, wizard.health)


# create sprite groups
fire_ball_group = pygame.sprite.Group()
lightning_bolt_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
fire_ball_dragon_group = pygame.sprite.Group()
dragon_group = pygame.sprite.Group()
tree1_group = pygame.sprite.Group()
tree2_group = pygame.sprite.Group()
ice_ball_group = pygame.sprite.Group()

world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# load in level data and create world
with open(f'level0_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
wizard, health_bar = world.process_data(world_data)


font = pygame.font.Font(None, 40)
font2 = pygame.font.Font(None, 35)
gray = pygame.Color('gray19')
blue = pygame.Color('dodgerblue')
# The clock is used to limit the frame rate
# and returns the time since last tick.
#create buttons
exit_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = Button(SCREEN_WIDTH // 2 - 103, SCREEN_HEIGHT // 2 - 50, restart_img, 2)
start_button = Button(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 150, start_img, 1)

run = True
while run:

    clock.tick(FPS)

    draw_bg()

    world.draw()


    health_bar.draw(wizard.health)


    wizard.update()
    wizard.draw()


    for enemy in enemy_group:
        enemy.draw()
        enemy.update()
        enemy.ai()


    for boss in boss_group:
        boss.draw()
        boss.update()
        boss.ai()

    for dragon in dragon_group:
        dragon.draw()
        dragon.update()
        dragon.ai()

    # update and draw groups
    ice_ball_group.update()
    decoration_group.update()
    tree1_group.update()
    tree2_group.update()
    fire_ball_dragon_group.update()
    lightning_bolt_group.update()
    item_box_group.update()
    fire_ball_group.update()
    fire_ball_group.draw(screen)
    item_box_group.draw(screen)
    decoration_group.draw(screen)
    lightning_bolt_group.draw(screen)
    fire_ball_dragon_group.draw(screen)
    tree1_group.draw(screen)
    tree2_group.draw(screen)
    ice_ball_group.draw(screen)


    # update player actions
    if wizard.alive:
        if wizard.in_air:
            wizard.update_action(2)  # 2: jump
        elif shoot:
            wizard.shoot()
            wizard.update_action(0)
        elif shoot_lighting:
            wizard.shoot_lightning()
            wizard.update_action(0)
        elif moving_left or moving_right:
            wizard.update_action(1)  # 1: run
        else:
            wizard.update_action(0)  # 0: idle
        screen_scroll = wizard.move(moving_left, moving_right)
    elif wizard.alive == False:
        if restart_button.draw(screen):
            exec(open("main.py").read())
            pygame.quit()
            sys.exit()
        if exit_button.draw(screen):
            pygame.quit()
            sys.exit()

    for boss in boss_group:
        if not boss.alive:
            wizard.speed = 0
            for dragon in dragon_group:
                dragon.speed = 0
            for enemy in enemy_group:
                enemy.speed = 0
            if start_button.draw(screen):
                exec(open("main.py").read())
                pygame.quit()
                sys.exit()
            if exit_button.draw(screen):
                pygame.quit()
                sys.exit()


    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.USEREVENT:
            counter -= 1
            text = str(counter).rjust(3) if counter > 0 else 'Special Ability Ready'
            if counter <= 0:
                ability = True

        if event.type == pygame.QUIT:
            run = False

            # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_t:
                shoot_lighting = True
            if event.key == pygame.K_w and wizard.alive:
                wizard.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_g and ability == True and wizard.alive == True:
                wizard.special_ability()
                counter = 10
                ability = False


        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_t:
                shoot_lighting = False


    screen.blit(font.render(text, True, (231, 76, 60)), (12, 48))

    pygame.display.update()

pygame.quit()