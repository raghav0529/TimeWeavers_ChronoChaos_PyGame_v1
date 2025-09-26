import pygame, sys
import random
import math
import os

clock = pygame.time.Clock()

from pygame.locals import *
pygame.init()

pygame.display.set_caption('Pygame Window')

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

try:
    pygame.mixer.music.load(resource_path('assets/music.mp3'))
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Error loading or playing music: {e}")
    
WINDOW_SIZE = (1000,700)
transformation_size = 70
screen = pygame.display.set_mode(WINDOW_SIZE,0,32)

player_image = pygame.image.load(resource_path(r'assets/player.png')).convert_alpha()
gun_img = pygame.image.load(resource_path(r"assets/gun.png")).convert_alpha()
gun_img = pygame.transform.scale(gun_img,(80,80))

try:
    witch_img = pygame.image.load(resource_path(r"assets/witch.png")).convert_alpha()
except pygame.error:
    witch_img = pygame.Surface((100, 150), pygame.SRCALPHA)
    witch_img.fill((128, 0, 128, 255))
    pygame.draw.circle(witch_img, (255, 255, 255), (50, 50), 40)
witch_img = pygame.transform.scale(witch_img, (100, 150))

grass_image = pygame.image.load(resource_path(r'assets/dirtimg1.png')).convert()
grass_image.set_colorkey((255,255,255))
dirt_image = pygame.image.load(resource_path(r'assets/dirt.png'))
grass_modified = pygame.transform.scale(grass_image,(transformation_size,transformation_size))
dirt_modified = pygame.transform.scale(dirt_image,(transformation_size,transformation_size))

moving_up = False
moving_right = False
moving_left = False
player_transformed = pygame.transform.scale(player_image,(30,60))
player_location = [50,50]
player_y_momentum = 0

scroll = [0,0]

player_rect = pygame.Rect(200,50,player_transformed.get_width(),player_transformed.get_height())
test_rect = pygame.Rect(100,100,100,50)

import csv

with open(resource_path(r"assets/level0_datafinalgrasslong.csv"), newline="") as f:
    reader = csv.reader(f)
    data_as_list = [[int(value) for value in row] for row in reader]

try:
    gunshot_sound = pygame.mixer.Sound(resource_path(r'assets/gunshot.wav'))
except pygame.error as e:
    gunshot_sound = None

class Particle_System:
    def __init__(self, surface, pos_getter, color, radius_range, vel_range_x, vel_range_y, decay):
        self.surface = surface
        self.pos_getter = pos_getter
        self.particles = []
        self.color = color
        self.radius_range = radius_range
        self.vel_range_x = vel_range_x
        self.vel_range_y = vel_range_y
        self.decay = decay

    def emit(self):
        pos = self.pos_getter()
        for i in range(random.randint(5, 10)):
            self.particles.append([
                pos,
                [random.uniform(self.vel_range_x[0], self.vel_range_x[1]),
                 random.uniform(self.vel_range_y[0], self.vel_range_y[1])],
                random.randint(self.radius_range[0], self.radius_range[1])
            ])

    def update_and_draw(self):
        self.particles = [
            [
                [p[0][0] + p[1][0], p[0][1] + p[1][1]],
                [p[1][0] * 0.9, p[1][1] + 0.1],
                p[2] - self.decay
            ]
            for p in self.particles if p[2] > 0
        ]
        for particle in self.particles:
            pygame.draw.circle(self.surface, self.color, (int(particle[0][0]), int(particle[0][1])), int(particle[2]))

ps = Particle_System(
    surface = screen,
    pos_getter = pygame.mouse.get_pos,
    color = (random.randint(20,100),random.randint(100,150),random.randint(100,200)),
    radius_range = (5,20),
    vel_range_x = (-5, 5),
    vel_range_y = (-5, 5),
    decay = 0.5
)

def load_map(path):
    f = open(path + '.csv','r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map


tile_size = 70
grass = []
dirt =[]


class Enemy:
    def __init__(self, x, y, size, health=100):
        self.rect = pygame.Rect(x, y, size[0], size[1])
        self.health = health
        self.size = size
        self.image = pygame.image.load(resource_path(r'assets/enemy.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)

    def move_towards_player(self, player_rect, speed):
        if self.rect.x < player_rect.x and self.rect.x < MAX_ENEMY_X:
            self.rect.x += speed
        elif self.rect.x > player_rect.x:
            self.rect.x -= speed
        if self.rect.y < player_rect.y:
            self.rect.y += speed
        elif self.rect.y > player_rect.y:
            self.rect.y -= speed

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def draw(self, surface, scroll):
        surface.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        
class Witch:
    def __init__(self, x, y):
        self.rect = witch_img.get_rect(topleft=(x, y))
        self.health = 5
        self.max_health = 5
    
    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def draw(self, surface, scroll):
        surface.blit(witch_img, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        
        health_bar_width = 100
        health_bar_height = 10
        health_bar_x = self.rect.x - scroll[0] + (self.rect.width - health_bar_width) / 2
        health_bar_y = self.rect.y - scroll[1] - 20
        
        pygame.draw.rect(surface, (255, 255, 255), (health_bar_x - 2, health_bar_y - 2, health_bar_width + 4, health_bar_height + 4))
        pygame.draw.rect(surface, (0, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
        health_rect = pygame.Rect(health_bar_x, health_bar_y, health_bar_width * (self.health / self.max_health), health_bar_height)
        pygame.draw.rect(surface, (0, 255, 0), health_rect)


MAX_ENEMY_X = 9400
WITCH_SPAWN_X = 11954
WITCH_SPAWN_Y = 1400
BOSS_ACTIVATION_DISTANCE = 1000

enemies = []
witch = None
last_enemy_spawn_time = 0
enemy_spawn_interval = 2500
player_facing_right = True
recoil = True
score = 0
game_state = "PLAYING"

font = pygame.font.Font(None, 50)
score_font = pygame.font.Font(None, 36)

start_time = pygame.time.get_ticks()
countdown_duration = 120000

player_health_bar_duration = 5000
player_health_current = player_health_bar_duration
boss_fight_start_time = 0

class Animation():
    def __init__(self,entity,path,name,img_number,frames,size,location):
        self.entity = entity
        self.path = path
        self.img_number = img_number
        self.name = name
        self.frames = frames
        self.size = size
        self.location = location
        self.imgs_loaded = [pygame.image.load(self.path+self.name+str(i)+".png").convert() for i in range(self.img_number)]
        self.transformed_images = []
        for i in range(len(self.imgs_loaded)):
            self.imgs_loaded[i].set_colorkey((255,255,255))
            self.transformed_images.append(pygame.transform.scale(self.imgs_loaded[i],self.size))
        self.idx = 0
        self.frame = 0

    def update(self):
        self.frame += 1
        if self.frame >= self.frames:
            self.idx = (self.idx+1)%len(self.transformed_images)
            self.frame = 0
            
    def get_image(self):
        image = self.transformed_images[self.idx]
        return image

player_run = Animation("player",resource_path("player_animations/run/"),"",2,5,(player_transformed.get_width(),player_transformed.get_height()),(player_rect.x-scroll[0],player_rect.y-scroll[1]))
player_idle = Animation("player",resource_path("player_animations/idle/"),"",3,6,(player_transformed.get_width(),player_transformed.get_height()),(player_rect.x-scroll[0],player_rect.y-scroll[1]))

def load_animation(path,name,img_number,frames,size,location):
    global start_frame,idx
    
    imgs_loaded = [pygame.image.load(path+name+str(i)+".png").convert() for i in range(img_number)]
    transformed_images = []
    for i in range(len(imgs_loaded)):
        imgs_loaded[i].set_colorkey((255,255,255))
        transformed_images.append(pygame.transform.scale(imgs_loaded[i],size))
    start_frame += 1
    if start_frame >= frames:
        idx = (idx +1)% len(transformed_images)
        start_frame = 0
    
    surf.blit(transformed_images[idx],location)

def collision_test(rect,tiles):
    hit_list = []
    for tile in tiles:
        
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect,movement,tiles):
    collision_types = {'top': False,'bottom' : False,'right' : False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect,tiles)
    for tile in hit_list:
        if movement[0]>0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect,tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect,collision_types

img_list = []
for i in range(31):
    img = pygame.image.load(resource_path(f"blocks/{i}.png")).convert()
    if i in [25,26,27,28,29,30]:
        
        if i ==  29:
            img = pygame.transform.scale(img,(tile_size,tile_size))
            img.set_colorkey((255,255,255))
            img_list.append(img)
        
        if i == 25:
            img = pygame.transform.scale(img,(tile_size*2.5,tile_size*4))
            img.set_colorkey((0,0,0))
            img_list.append(img)
        if i== 30:
            img = pygame.transform.scale(img,(tile_size,tile_size))
            img.set_colorkey((255,255,255))
            img_list.append(img)
        
        if i == 28:
            
            img = pygame.transform.scale(img,(tile_size,tile_size*1.2))
            img.set_colorkey((255,255,255))
            img_list.append(img)
        
        if i in[26,27]:
            
            img = pygame.transform.scale(img,(tile_size*2.5,tile_size*3))
            img.set_colorkey((255,255,255))
            img_list.append(img)
    elif i not in [25,26,27,28,29,30]:
        

        img = pygame.transform.scale(img,(tile_size,tile_size))
        img.set_colorkey((255,255,255))
        img_list.append(img)




def draw_world():
    for y,row in enumerate(data_as_list):
        for x,tile in enumerate(row):
            if tile >= 0:
                surf.blit(img_list[tile],(x*tile_size-scroll[0],y*tile_size-scroll[1]))
                
                if tile not in [25,26,27,28,30]:
                    
                    
                    
                    
                    
                    tiles.append(pygame.Rect(x* tile_size , y*tile_size,transformation_size,transformation_size))

vx,vy = 0,0

flip_right = False
flip_left = False
moving_up_flag = False
emit = False
acll = 0
total_momentum = 12


first_change_time = random.randint(30000, 90000)
second_change_time = first_change_time
while second_change_time == first_change_time:
    second_change_time = random.randint(30000, 90000)

key_state_first_change = False
key_state_second_change = False
message_text = ""
message_start_time = 0

def stop_music():
    """Stops the background music if it is currently playing."""
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

while True:
    
    if game_state == "PLAYING":
        elapsed_time = pygame.time.get_ticks() - start_time
        remaining_time = max(0, countdown_duration - elapsed_time)
        if remaining_time <= 0:
            game_state = "GAME_OVER"

        if player_rect.x > 12000 and game_state == "PLAYING":
            message_text = "The Witch is Near!"
            message_start_time = pygame.time.get_ticks()
            game_state = "BOSS_FIGHT_NEAR"
        
        if not key_state_first_change and pygame.time.get_ticks() >= first_change_time:
            key_state_first_change = True
            message_text = "Movement Keys Reversed!"
            message_start_time = pygame.time.get_ticks()

        if not key_state_second_change and key_state_first_change and pygame.time.get_ticks() >= second_change_time:
            key_state_second_change = True
            message_text = "Jump Key Changed!"
            message_start_time = pygame.time.get_ticks()

        if player_rect.x > 9500 and score < 1000:
            player_rect.x = 9500

    elif game_state == "BOSS_FIGHT_NEAR":
        distance_to_witch = math.hypot(player_rect.x - WITCH_SPAWN_X, player_rect.y - WITCH_SPAWN_Y)
        if distance_to_witch <= BOSS_ACTIVATION_DISTANCE:
            game_state = "BOSS_FIGHT"
            witch = Witch(WITCH_SPAWN_X, WITCH_SPAWN_Y)
            boss_fight_start_time = pygame.time.get_ticks()
            
    elif game_state == "BOSS_FIGHT":
        current_time = pygame.time.get_ticks()
        player_health_current = max(0, player_health_bar_duration - (current_time - boss_fight_start_time))
        if player_health_current <= 0:
            game_state = "GAME_OVER"
    
    if player_rect.y > 10000:
        game_state = "GAME_OVER"
            
    if game_state in ["PLAYING", "BOSS_FIGHT_NEAR", "BOSS_FIGHT"]:
        current_time = pygame.time.get_ticks()
        if current_time - last_enemy_spawn_time > enemy_spawn_interval and game_state != "BOSS_FIGHT":
            spawn_x = player_rect.x + (random.choice([-1, 1]) * 1000)
            if spawn_x > MAX_ENEMY_X:
                spawn_x = MAX_ENEMY_X - 100
            spawn_y = player_rect.y - 100
            enemies.append(Enemy(spawn_x, spawn_y, (50, 50)))
            last_enemy_spawn_time = current_time

        surf = pygame.transform.scale(screen,(1000,700))
        surf.fill((146,244,255))
        
        tiles = []
        draw_world()

        player_movement = [0,0]
        mx,my = pygame.mouse.get_pos()
        
        scroll[0] += (player_rect.x - scroll[0]-500)/30
        scroll[1] += (player_rect.y - scroll[1]-350)/30

        player_y_momentum += 1
        player_movement[1] += player_y_momentum
        player_movement[0] += vx
        vx -= 0.4
        if vx <=0:
            vx = 0

        if pygame.mouse.get_pressed()[0]== 1:
            if recoil == True:
                vx = -total_momentum*math.cos(angle_radian)
                vy = total_momentum*math.sin(angle_radian)
                player_y_momentum = vy
            
        if moving_right:
            player_movement[0] += 8
        
        if moving_left:
            player_movement[0] -= 8

        if player_y_momentum > 35:
            player_y_momentum = 35
        
        if moving_left or moving_right:
            current_anim = player_run
        else:
            current_anim = player_idle

        if game_state != "BOSS_FIGHT":
            for enemy in enemies[:]:
                enemy.move_towards_player(player_rect, 4)
                enemy.draw(surf, scroll)
            
            for enemy in enemies:
                if player_rect.colliderect(enemy.rect):
                    game_state = "GAME_OVER"
                    break
        else:
            if witch:
                witch.draw(surf, scroll)
        
        current_anim.update()
        player_image_to_blit = current_anim.get_image()
        
        if not player_facing_right:
            player_image_to_blit = pygame.transform.flip(player_image_to_blit, True, False)
            
        surf.blit(player_image_to_blit, (player_rect.x - scroll[0], player_rect.y - scroll[1]))

        player_rect,collisions= move(player_rect,player_movement,tiles)
        
        if collisions['bottom']:
            if moving_up_flag:
                player_y_momentum = -20
            else:
                player_y_momentum = 0
        
        screen.blit(surf,(0,0))
        
        score_text = score_font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        
        if game_state in ["PLAYING", "BOSS_FIGHT_NEAR"]:
            timer_text = score_font.render(f"Time: {remaining_time // 1000}", True, (0, 0, 0))
            screen.blit(timer_text, (WINDOW_SIZE[0] - timer_text.get_width() - 10, 10))
        
        if message_text and pygame.time.get_ticks() - message_start_time < 3000:
            message_surface = font.render(message_text, True, (255, 0, 0))
            message_rect = message_surface.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 4))
            screen.blit(message_surface, message_rect)
            
        if game_state == "BOSS_FIGHT":
            player_health_bar_width = 200
            player_health_bar_height = 20
            player_health_bar_x = 10
            player_health_bar_y = 50
            
            pygame.draw.rect(screen, (0, 0, 0), (player_health_bar_x - 2, player_health_bar_y - 2, player_health_bar_width + 4, player_health_bar_height + 4))
            pygame.draw.rect(screen, (255, 0, 0), (player_health_bar_x, player_health_bar_y, player_health_bar_width, player_health_bar_height))
            
            health_rect = pygame.Rect(player_health_bar_x, player_health_bar_y, player_health_bar_width * (player_health_current / player_health_bar_duration), player_health_bar_height)
            pygame.draw.rect(screen, (0, 255, 0), health_rect)
            
            player_health_text = score_font.render(f"Health: {player_health_current // 100}", True, (0, 0, 0))
            screen.blit(player_health_text, (player_health_bar_x, player_health_bar_y + 30))
        
        ps.update_and_draw()

        gun_img_rect = gun_img.get_rect(center = (player_rect.x-scroll[0]+60,player_rect.y-scroll[1]+80))
    
        if mx - gun_img_rect.x == 0:
            if my < gun_img_rect.y:
                angle_radian = math.pi / 2 
            else:
                angle_radian = -math.pi / 2
        elif mx - gun_img_rect.x > 0:
            angle_radian = math.atan((-my+gun_img_rect.y)/(mx-gun_img_rect.x))
        else: 
            angle_radian = math.pi- math.atan((+my-gun_img_rect.y)/(mx-gun_img_rect.x))       
            
        angle_degrees = math.degrees(angle_radian)
    
        gun_rotate_img = pygame.transform.rotate(gun_img,angle_degrees)
        screen.blit(gun_rotate_img,(gun_img_rect.x-(gun_img.get_width())/2,gun_img_rect.y -(gun_img.get_height())/2))

    elif game_state == "GAME_OVER":
        stop_music()
        screen.fill((200, 200, 200))
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 50))
        screen.blit(game_over_text, game_over_rect)

        final_score_text = score_font.render(f"Final Score: {score}", True, (0, 0, 0))
        final_score_rect = final_score_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
        screen.blit(final_score_text, final_score_rect)
        
        instructions_text = score_font.render("Press any key to exit", True, (0, 0, 0))
        instructions_rect = instructions_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 50))
        screen.blit(instructions_text, instructions_rect)
        
    elif game_state == "VICTORY":
        stop_music()
        screen.fill((150, 200, 150))
        victory_text = font.render("VICTORY!", True, (0, 150, 0))
        victory_rect = victory_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 50))
        screen.blit(victory_text, victory_rect)

        final_score_text = score_font.render(f"Final Score: {score}", True, (0, 0, 0))
        final_score_rect = final_score_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
        screen.blit(final_score_text, final_score_rect)
        
        instructions_text = score_font.render("Press any key to exit", True, (0, 0, 0))
        instructions_rect = instructions_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 50))
        screen.blit(instructions_text, instructions_rect)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
        if game_state in ["PLAYING", "BOSS_FIGHT_NEAR", "BOSS_FIGHT"]:
            if event.type == KEYDOWN:
                if event.key == K_LSHIFT:
                    recoil = False      
                    
                
                if not key_state_first_change:
                    
                    if event.key == K_d:
                        moving_right = True
                        player_facing_right = True
                    if event.key == K_a:
                        moving_left = True
                        player_facing_right = False
                else:
                    
                    if event.key == K_a:
                        moving_right = True
                        player_facing_right = True
                    if event.key == K_d:
                        moving_left = True
                        player_facing_right = False

                if not key_state_second_change:
                    if event.key == K_w:
                        moving_up_flag = True
                else:
                    if event.key == K_SPACE:
                        moving_up_flag = True

            if event.type == KEYUP:
                if event.key == K_LSHIFT:
                    recoil = True
                if not key_state_first_change:
                    if event.key == K_LSHIFT:
                        recoil = True
                    if event.key == K_d:
                        moving_right = False
                    if event.key == K_a:
                        moving_left = False
                else:
                    if event.key == K_LSHIFT:
                        recoil = True
                    if event.key == K_a:
                        moving_right = False
                    if event.key == K_d:
                        moving_left = False

                if not key_state_second_change:
                    if event.key == K_w:
                        moving_up_flag = False
                else:
                    if event.key == K_SPACE:
                        moving_up_flag = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    ps.emit()
                    if gunshot_sound:
                        gunshot_sound.play()
                        
                    mouse_pos_world = (event.pos[0] + scroll[0], event.pos[1] + scroll[1])
                    if game_state == "BOSS_FIGHT":
                        if witch and witch.rect.collidepoint(mouse_pos_world):
                            if witch.take_damage():
                                game_state = "VICTORY"
                                witch = None
                            break
                    else:
                        for enemy in enemies[:]:
                            if enemy.rect.collidepoint(mouse_pos_world):
                                enemies.remove(enemy)
                                score += 100
                                break
        elif game_state in ["GAME_OVER", "VICTORY"]:
            if event.type == KEYDOWN:
                pygame.quit()
                sys.exit()
    
    pygame.display.update()
    clock.tick(70)
