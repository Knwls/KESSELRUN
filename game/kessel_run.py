# Music by Abstraction, found at https://soundcloud.com/abstraction/sets/ludum-dare-challenge

import pygame as pg
import random as rng
import time
import os

from game.res.colors import *

WIDTH = 198
HEIGHT = 178
FPS = 60

# initialize pg/sound and create window
pg.init()
pg.mixer.init()
screen = pg.display.set_mode((490, 615))
pg.display.set_caption("Kessel Run")
icon = pg.image.load(os.path.join(os.getcwd(), "res/images/icon.png")).convert()
icon.set_colorkey(WHITE)
pg.display.set_icon(icon)
clock = pg.time.Clock()
pg.mouse.set_visible(0)


def draw_text(surf, text, size, x, y):
    font_name = pg.font.match_font('arial')
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, DARK_GREEN)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)
    no_space = pg.sprite.spritecollide(m, mobs, False)
    if no_space:
        m.rect.x = rng.randrange(0, WIDTH - m.rect.width)


def draw_health_bar(surf, x, y, health):
    if health < 0:
        health = 0
    BAR_WIDTH = 50
    BAR_HEIGHT = 8
    fill = (health / 100) * BAR_WIDTH
    outline_rect = pg.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    pg.draw.rect(surf, DARK_GREEN, fill_rect)
    pg.draw.rect(surf, DARKER_GREEN, outline_rect, 2)


def start_screen(state):
    if state == 1:
        zone.blit(ss_play_img, (0, -10))
    elif state == 2:
        zone.blit(ss_scoreboard_img, (0, -10))
    elif state == 3:
        zone.blit(ss_mute_img, (0, -10))

    return state


def show_scoreboard(state):
    if state == 1:
        zone.blit(scoreboard_play, (0, -10))
    elif state == 2:
        zone.blit(scoreboard_exit, (0, -10))

    return state


def scoreboard():
    hs = open('res/stats/scores.txt', 'r')
    hs_ordered = []
    for line in hs.readlines():
        hs_ordered.append(int(line))

    hs_ordered = list(reversed(sorted(hs_ordered)))

    hs.close()
    return hs_ordered


def game_zone():
    # create  game zone
    zone = pg.image.load(os.path.join(os.getcwd(), "res/images/env/console.png")).convert()
    zone = pg.transform.scale(zone, (int(WIDTH * 0.98), int(HEIGHT * 0.97)))
    zone_rect = zone.get_rect()
    zone_rect.x = 147
    zone_rect.y = 87
    return [zone, zone_rect]


def power_up(p):
    if p == 1:
        player.health = 100
    if p == 2:
        player.double_shot = True
    if p == 3:
        player.invulnerable = True
        player.invulnerable_timer = 10


class Player(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = player_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 28
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 8
        self.speedx = 0
        self.health = 100
        self.double_shot = False
        self.invulnerable = False

    def update(self):
        self.speedx = 0
        keystate = pg.key.get_pressed()
        if keystate[pg.K_LEFT]:
            self.speedx = -3
        if keystate[pg.K_RIGHT]:
            self.speedx = +3
        self.rect.x += self.speedx
        if self.rect.right > WIDTH * 0.98:
            self.rect.right = WIDTH * 0.98
        if self.rect.left < WIDTH * 0.001:
            self.rect.left = WIDTH * 0.001

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top, "UP")
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()

    def double_shoot(self):
        bullet1 = Bullet(self.rect.centerx + 10, self.rect.top, "UP")
        all_sprites.add(bullet1)
        bullets.add(bullet1)
        bullet2 = Bullet(self.rect.centerx - 10, self.rect.top, "UP")
        all_sprites.add(bullet2)
        bullets.add(bullet2)
        shoot_sound.play()

    def invulnerable_animation(self, anim_state):
        if anim_state == 1:
            self.image = player_img
        else:
            self.image = playerinv_img


class Mob(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.last_update = pg.time.get_ticks()
        rng_spawn = rng.randrange(0, 100)
        self.spawn_mob(rng_spawn)

    def spawn_mob(self, rng_spawn):
        if rng_spawn >= 90:
            self.image = mob_imgs[2]
            self.rect = self.image.get_rect()
            self.image = pg.transform.scale(self.image, (int(self.rect.width / 2.5), int(self.rect.height / 2.5)))
            self.rect = self.image.get_rect()
            self.image.set_colorkey(BLACK)
            self.speedy = rng.randrange(1, 2)
            self.speedx = 0
            self.health = 300
            bosses.add(self)

        elif rng_spawn >= 45 and rng_spawn < 90:
            self.image = mob_imgs[1]
            self.rect = self.image.get_rect()
            self.image = pg.transform.scale(self.image, (int(self.rect.width * 2), int(self.rect.height * 2)))
            self.rect = self.image.get_rect()
            self.speedy = rng.randrange(2, 3)
            self.speedx = rng.randrange(-1, 1)
            self.health = 200

        else:
            self.image = mob_imgs[0]
            self.rect = self.image.get_rect()
            self.speedy = rng.randrange(2, 4)
            self.speedx = rng.randrange(-1, 1)
            self.health = 100

        self.rect.x = rng.randrange(0, WIDTH - self.rect.width)
        self.rect.y = rng.randrange(-100, -40)

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.bottom, "DOWN")
        all_sprites.add(bullet)
        boss_bullets.add(bullet)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > 262:
            self.rect.x = rng.randrange(0, WIDTH - self.rect.width)
            self.rect.y = rng.randrange(-100, -40)
            self.speedy = rng.randrange(1, 3)

        now = pg.time.get_ticks()
        if now - self.last_update > 1000:
            self.last_update = now
            # boss shot
            if bosses:
                for boss in bosses:
                    boss.shoot()


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, dir):
        pg.sprite.Sprite.__init__(self)
        self.dir = dir
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        if self.dir == "UP":
            self.speedy = -8
        elif self.dir == "DOWN":
            self.speedy = 2.5

    def update(self):
        self.rect.y += self.speedy
        # destroy if bullet leaves visible area
        if self.rect.bottom < 0:
            self.kill()
        if self.rect.top > HEIGHT:
            self.kill()


class PowerUp(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = powerup_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        # destroy if power up leaves visible area
        if self.rect.bottom < 0:
            self.kill()
        if self.rect.top > HEIGHT:
            self.kill()


# create game zone surface (gameboy screen)
zone = game_zone()[0]
zone_rect = game_zone()[1]


# graphics
# ~ game
background_img = pg.image.load(os.path.join(os.getcwd(), "res/images/env/console.png")).convert()
background_rect = background_img.get_rect()
player_img = pg.image.load(os.path.join(os.getcwd(), "res/images/sprites/player.png")).convert()
playerinv_img = pg.image.load(os.path.join(os.getcwd(), "res/images/sprites/player-inverted.png")).convert()
player_rect = player_img.get_rect()
playerinv_img.set_colorkey(BLACK)
player_img.set_colorkey(BLACK)
mob_imgs = [pg.image.load(os.path.join(os.getcwd(), "res/images/sprites/enemy-small.png")).convert(),
            pg.image.load(os.path.join(os.getcwd(), "res/images/sprites/enemy-big.png")).convert(),
            pg.image.load(os.path.join(os.getcwd(), "res/images/sprites/boss.png")).convert()]
bullet_img = pg.image.load(os.path.join(os.getcwd(), "res/images/objects/bullet.png")).convert()
bullet_rect = bullet_img.get_rect()
powerup_img = pg.image.load(os.path.join(os.getcwd(), "res/images/objects/power-up.png")).convert()
powerup_img = pg.transform.scale(powerup_img, (15,15))
powerup_rect = powerup_img.get_rect()
explosion_img = pg.image.load(os.path.join(os.getcwd(), "res/images/objects/explosion.png")).convert()
# ~ menu
ss_play_img = pg.image.load(os.path.join(os.getcwd(), "res/images/menu/screen-play.png")).convert()
ss_scoreboard_img = pg.image.load(os.path.join(os.getcwd(), "res/images/menu/screen-scoreboard.png")).convert()
ss_mute_img = pg.image.load(os.path.join(os.getcwd(), "res/images/menu/screen-mute.png")).convert()
# ~ scoreboard
scoreboard_play = pg.image.load(os.path.join(os.getcwd(), "res/images/menu/scoreboard-play.png")).convert()
scoreboard_exit = pg.image.load(os.path.join(os.getcwd(), "res/images/menu/scoreboard-exit.png")).convert()


# audio
shoot_sound = pg.mixer.Sound("res/audio/sound-effects/shoot.wav")
shoot_sound.set_volume(0.3)
powerup_sound = pg.mixer.Sound("res/audio/sound-effects/power-up.wav")
powerup_sound.set_volume(0.3)
explosion_sound = pg.mixer.Sound("res/audio/sound-effects/explosion.wav")
explosion_sound.set_volume(0.3)
explosion_collision_sound = pg.mixer.Sound("res/audio/sound-effects/explosion-collision.wav")
explosion_collision_sound.set_volume(0.5)
home_sound = pg.mixer.Sound("res/audio/sound-effects/home.wav")
home_sound.set_volume(0.5)
songs = ["res/audio/output.mp3", "res/audio/output-2.mp3"]
songChoice = rng.randrange(0,2)
pg.mixer.music.load(songs[songChoice])
pg.mixer.music.set_volume(0.5)


# sprites
# ~ sprite groups
all_sprites = pg.sprite.Group()
mobs = pg.sprite.Group()
bullets = pg.sprite.Group()
boss_bullets = pg.sprite.Group()
bosses = pg.sprite.Group()
pups = pg.sprite.Group()
# ~ player
player = Player()
all_sprites.add(player)


# states of game
menu = True
running = False
muted = False

# menu
menu_state = start_screen(1)


# menu loop
while menu:
    # keep loop running at the right speed
    clock.tick(FPS)

    # events
    for event in pg.event.get():
        # exit on close
        if event.type == pg.QUIT:
            menu = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT:
                if menu_state == 3:
                    menu_state = 1
                else:
                    menu_state += 1
            elif event.key == pg.K_LEFT:
                if menu_state == 1:
                    menu_state = 3
                else:
                    menu_state -= 1
            elif event.key == pg.K_RETURN:
                if menu_state == 1:
                    zone.fill(ZONE_GREEN)
                    screen.blit(zone, zone_rect)
                    pg.display.flip()
                    time.sleep(1)
                    home_sound.play()
                    time.sleep(0.9)
                    draw_text(zone, "CHEWIE", 20, WIDTH / 2, 50)
                    screen.blit(zone, zone_rect)
                    pg.display.flip()
                    time.sleep(2.3)
                    draw_text(zone, "WE'RE", 20, WIDTH / 2, 70)
                    screen.blit(zone, zone_rect)
                    pg.display.flip()
                    time.sleep(0.2)
                    draw_text(zone, "HOME", 20, WIDTH / 2, 90)
                    screen.blit(zone, zone_rect)
                    pg.display.flip()
                    menu = False
                    running = True
                    scoreboard = False
                    time.sleep(1)
                elif menu_state == 2:
                    high_scores = scoreboard()
                    menu = False
                    scoreboard = True
                elif menu_state == 3:
                    if muted:
                        pg.mixer.music.set_volume(0.5)
                        muted = False
                    else:
                        pg.mixer.music.set_volume(0)
                        muted = True

    # draw / render
    # ~ start screen
    menu_state = start_screen(menu_state)

    if not muted:
        draw_text(zone, "MUSIC: ON", 8, 21, 3)
    else:
        draw_text(zone, "MUSIC: OFF", 8, 23, 3)

    # ~ on screen
    screen.blit(background_img, background_rect)
    screen.blit(zone, zone_rect)

    # after drawing everything, flip the display
    pg.display.flip()

# state
scoreboard_state = 1

# scoreboard loop
while scoreboard:
    # keep loop running at the right speed
    clock.tick(FPS)

    # events
    for event in pg.event.get():
        # exit on close
        if event.type == pg.QUIT:
            scoreboard = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_RIGHT:
                if scoreboard_state == 2:
                    scoreboard_state = 1
                else:
                    scoreboard_state += 1
            elif event.key == pg.K_LEFT:
                if scoreboard_state == 1:
                    scoreboard_state = 2
                else:
                    scoreboard_state -= 1
            elif event.key == pg.K_RETURN:
                if scoreboard_state == 1:
                    zone.fill(ZONE_GREEN)
                    screen.blit(zone, zone_rect)
                    pg.display.flip()
                    time.sleep(1)
                    home_sound.play()
                    time.sleep(0.9)
                    draw_text(zone, "CHEWIE", 20, WIDTH / 2, 50)
                    screen.blit(zone, zone_rect)
                    pg.display.flip()
                    time.sleep(2.3)
                    draw_text(zone, "WE'RE", 20, WIDTH / 2, 70)
                    screen.blit(zone, zone_rect)
                    pg.display.flip()
                    time.sleep(0.2)
                    draw_text(zone, "HOME", 20, WIDTH / 2, 90)
                    screen.blit(zone, zone_rect)
                    pg.display.flip()
                    menu = False
                    running = True
                    scoreboard = False
                    time.sleep(1)
                elif scoreboard_state == 2:
                    running = False
                    scoreboard = False

    # draw / render
    # ~ scoreboard screen
    # ~ start screen
    scoreboard_state = show_scoreboard(scoreboard_state)
    for s in high_scores[:10]:
        index = high_scores.index(s) + 1
        t = str(str(index) + ". " + str(s))
        draw_text(zone, t, 9, WIDTH / 2, (index + 2.5) * 10)
    # ~ on screen
    screen.blit(background_img, background_rect)
    screen.blit(zone, zone_rect)

    # after drawing everything, flip the display
    pg.display.flip()


# ~ origin mobs
for i in range(8):
    newmob()
mob_spawned = pg.time.get_ticks()

# score declaration
score = 0

# starts game music
pg.mixer.music.play(loops=-1)

# declarations
invulnerable_start = 0
ds_start = 0
high_score = 0
changed = False

# game loop
while running:
    # time check
    last_update = pg.time.get_ticks()

    # keep loop running at the right speed
    clock.tick(FPS)

    # events
    for event in pg.event.get():
        # exit on close
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                if player.double_shot:
                    player.double_shoot()
                else:
                    player.shoot()

    if player.double_shot:
        if last_update - invulnerable_start > 30000:
            player.double_shot = False

    if player.invulnerable:
        draw_text(zone, "invulnerable", 8, 27, 15)
        num = last_update - invulnerable_start
        if not changed and num % 2 == 0:
            player.invulnerable_animation(0)
            changed = True
        elif changed and num % 2 != 0:
            player.invulnerable_animation(1)
            changed = False
        if last_update - invulnerable_start > 9000:
            player.invulnerable = False
            invulnerable_start = 0

    # update
    all_sprites.update()

    # draw / render
    # ~ on screen
    screen.blit(background_img, background_rect)
    screen.blit(zone, zone_rect)
    zone.fill(ZONE_GREEN)

    # ~ on game zone
    all_sprites.draw(zone)
    draw_text(zone, "SCORE: " + str(score), 8, WIDTH / 2, 13)
    hs = open('res/scores/scores.txt', 'r')
    for line in hs.readlines():
        try:
            if int(line) > high_score:
                high_score = int(line)
        except TypeError:
            pass

    hs.close()
    draw_text(zone, "HIGH SCORE: " + str(high_score), 8, WIDTH / 2, 3)
    draw_health_bar(zone, 5, 5, player.health)

    # collisions
    # ~ bullet hits
    hits = pg.sprite.groupcollide(mobs, bullets, False, True)
    for hit in hits:
        hit.health -= 100
        if hit.health <= 0:
            hit.kill()
            enemy_hit = hit.rect.width
            score += rng.randrange(enemy_hit * 5, enemy_hit * 7)
            newmob()
            explosion_sound.play()
            pup_chance = rng.randrange(0, 10)
            if pup_chance > 7:
                pup = PowerUp(hit.rect.centerx, hit.rect.y)
                all_sprites.add(pup)
                pups.add(pup)

    # ~ boss bullet hits
    bb_hit = pg.sprite.spritecollide(player, boss_bullets, True)
    if not player.invulnerable and bb_hit:
        player.health -= 25

    # ~ enemy hits
    collisions = pg.sprite.spritecollide(player, mobs, True)
    if not player.invulnerable:
        for collision in collisions:
            explosion_collision_sound.play()
            player.health -= 30
            newmob()

    # ~ power up hits
    collected = pg.sprite.spritecollide(player, pups, True)
    if collected:
        powerup_sound.play()
        type = rng.randrange(1, 4)
        power_up(type)
        if type == 2:
            ds_start = pg.time.get_ticks()
        elif type == 3:
            invulnerable_start = pg.time.get_ticks()

    # ~ spawn a mob every 3 seconds
    if last_update - mob_spawned > 2000:
        newmob()
        mob_spawned = pg.time.get_ticks()

    # ~ death
    if player.health <= 0:
        # write to high score list
        score_str = str(score)
        hs_file = open("res/stats/scores.txt", "a")
        hs_file.write("%s \n" % score_str)
        hs_file.close()

        for s in all_sprites:
            all_sprites.remove(s)
        for b in bullets:
            bullets.remove(b)
        for m in mobs:
            mobs.remove(m)
        for bb in boss_bullets:
            boss_bullets.remove(bb)
        for p in pups:
            pups.remove(p)

        score = 0
        # ~ player
        player = Player()
        all_sprites.add(player)

        time.sleep(1)

        # ~ origin mobs
        for i in range(8):
            newmob()

    # after drawing everything, flip the display
    pg.display.flip()


pg.quit()
