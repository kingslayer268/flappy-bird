import pygame
import sys
import random
import json
from pygame import display as display
pygame.init()

#game functions

def floor_func():
    screen.blit(floor, (floor_x, 450))
    screen.blit(floor,(floor_x+288, 450))

def create_pipe():
    pipey = random.choice(pipe_height)
    bottompipe = pipe.get_rect(midtop=(400, pipey))
    toppipe = pipe.get_rect(midbottom=(400, pipey-150))
    return bottompipe, toppipe

def pipe_movement(pipe_list):
    for single_pipe in pipe_list:
        single_pipe.centerx -= 2.5
    return pipe_list

def place_pipe(pipe_list):
    for singlepipe in pipe_list:
        if singlepipe.bottom > 512:
            screen.blit(pipe, singlepipe)
        else:
            flip_pipe = pygame.transform.flip(pipe, False, True)
            screen.blit(flip_pipe, singlepipe)

def remove_extra_pipes(pipe_list):
    pipe_list = [singlepipe for singlepipe in pipe_list if singlepipe.centerx >= -2.5]
    return pipe_list

def check_collisons(pipe_list):
    if bird_rect.top <= -100 or bird_rect.bottom >= 450:
        die_sound.play()
        return False
    for singlepipe in pipe_list:
        if bird_rect.colliderect(singlepipe):
            die_sound.play()
            return False
    return True

def update_score(pipe_list, passed_pipes):
    for singlepipe in pipe_list:
        if singlepipe.centerx <= 144 and singlepipe not in passed_pipes:
            passed_pipes.append(singlepipe)
            point_sound.play()
    return int(len(passed_pipes)/2)

def bird_rotation(bird_surface):
    rotated_surface = pygame.transform.rotozoom(bird_surface, -bird_movement*10, 1)
    return rotated_surface

def bird_animation():
    new_bird = bird_frames[bird_index]
    new_rect = new_bird.get_rect(center=(bird_rect.centerx, bird_rect.centery))
    return new_bird, new_rect

def display_score(game_state:str):
    if game_state == 'running':
        score_surface = game_font.render(f'Score: {str(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center = (144, 50))
        screen.blit(score_surface, score_rect)
    elif game_state == "ended":
        with open('high_score.json') as data:
            file = json.load(data)
            high_score_from_json = file["high_score"]
        high_score_surface = game_font.render(f'High Score: {str(high_score_from_json)}', True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(144, 412))
        screen.blit(high_score_surface, high_score_rect)
def update_high_score(score, high_score):
    if score > high_score:
        high_score = score
        with open('high_score.json', 'w') as data:
            dict_to_write = {"high_score": high_score}
            json.dump(dict_to_write, data)
    return high_score


#game resources 
screen = display.set_mode((288, 512))

display.set_caption("Flappy Bird")

clock = pygame.time.Clock()

game_font = pygame.font.Font('04B_19.TTF', 40)

game_over = pygame.transform.rotozoom(pygame.image.load('assets/gameover.png'), 0, 1.4)

over_rect = game_over.get_rect(center=(144, 256))

bg = pygame.image.load('assets/background-day.png').convert()

floor = pygame.image.load('assets/base.png')


bird_surface1 = pygame.image.load('assets/yellowbird-upflap.png').convert_alpha()

bird_surface2 = pygame.image.load('assets/yellowbird-midflap.png').convert_alpha()

bird_surface3 = pygame.image.load('assets/yellowbird-downflap.png').convert_alpha()

bird_frames = [bird_surface1, bird_surface2, bird_surface3]

bird_index = 0

bird_surface = bird_frames[bird_index]

bird_rect = bird_surface.get_rect(center=(50, 256))

BIRD_ANIMATION = pygame.USEREVENT + 1

pygame.time.set_timer(BIRD_ANIMATION, 200)

pipe = pygame.image.load('assets/pipe-green.png')

pipe_list = []

passed_pipes = []

pipe_height = [200,300,400]

SPAWNPIPE = pygame.USEREVENT

pygame.time.set_timer(SPAWNPIPE, 1000)

jump_sound = pygame.mixer.Sound('sound/sfx_swooshing.wav')

die_sound = pygame.mixer.Sound('sound/sfx_hit.wav')

point_sound = pygame.mixer.Sound('sound/sfx_point.wav')

wing_sound = pygame.mixer.Sound('sound/sfx_wing.wav')

with open('high_score.json') as data:
    file = json.load(data)
    high_score_from_json = file["high_score"]

# Game Variables
floor_x = 0

gravity = 0.125

bird_movement = 0

game_running = True

score = 0

high_score = 0

invincibility = False

invincibility_on_cooldown = False

last_used = 0


# Game loop 
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_running == True:
                bird_movement = 0
                bird_movement -= 4
                wing_sound.play()

            if event.key == pygame.K_SPACE and game_running == False:
                bird_rect.center = (50, 256)
                pipe_list.clear()
                bird_movement = 0
                game_running = True  
                passed_pipes.clear()
                invincibility = False
                last_used = 0
            
            if event.key == pygame.K_LCTRL and game_running==True:
                if pygame.time.get_ticks() - last_used > 15000 or last_used == 0:
                    invincibility = True
                    last_used = pygame.time.get_ticks()
                    print('hit')

        if event.type == SPAWNPIPE and game_running == True:
            pipe_list.extend(create_pipe())  
        if event.type == BIRD_ANIMATION and game_running:
            
            if bird_index < 2:
                bird_index += 1

            else:
                bird_index = 0

            bird_surface, bird_rect = bird_animation()

    #Main elements        

    screen.blit(bg, (0,0))
    floor_x -= 0.5
    if floor_x <= -288:
        floor_x = 0
    floor_func()
    display_score("running")

    if game_running:
        #bird
        bird_movement += gravity
        bird_rect.centery += bird_movement
        bird_rotated = bird_rotation(bird_surface)
        screen.blit(bird_rotated, bird_rect)
        
        #pipe
        score = update_score(pipe_list, passed_pipes)
        pipe_list = pipe_movement(pipe_list=pipe_list)
        place_pipe(pipe_list)
        pipe_list = remove_extra_pipes(pipe_list=pipe_list)
        if invincibility == False:
            game_running = check_collisons(pipe_list)
        else:
            game_running = True
            inv_surface = game_font.render(
                f'INVINCIBLE! {int(6-(pygame.time.get_ticks()-last_used)/1000)}', True, (255, 0, 0))
            inv_rect = inv_surface.get_rect(center=(144, 475))
            screen.blit(inv_surface, inv_rect)
        if last_used > 0 and pygame.time.get_ticks()-last_used > 5000:
            invincibility = False
        if last_used == 0 or pygame.time.get_ticks() - last_used > 15000:
            inv_surface = game_font.render(
                f'Press L-CTRL', True, (255, 0, 0))
            inv_rect = inv_surface.get_rect(center=(144, 475))
            screen.blit(inv_surface, inv_rect)

    else:
        with open('high_score.json') as data:
            file = json.load(data)
            high_score_from_json = file["high_score"]
        high_score = update_high_score(score, high_score_from_json)
        display_score("ended")
        screen.blit(game_over, over_rect)

    display.update()
    clock.tick(120)
