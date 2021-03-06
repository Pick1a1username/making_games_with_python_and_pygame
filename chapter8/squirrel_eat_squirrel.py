# Squirrel Eat Squirrel (a 2D Katamari Damacy clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Creative Commons BY-NC-SA 3.0 US

import random, sys, time, math, pygame
from pygame.locals import *

FPS = 30
WINWIDTH = 640
WINHEIGHT = 480
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

GRASSCOLOR = ( 24, 255, 0)
WHITE      = (255, 255, 255)
RED        = (255,   0,   0)

CAMERASLACK = 90 # how far from the center the squirrel moves before
MOVERATE = 9 # how fast the player moves
BOUNCERATE = 6 # how fast the player bounces (large is slower)
BOUNCEHEIGHT = 30 # how high the player bounces
STARTSIZE = 25 # how big the player starts off
WINSIZE = 300 # how big the player needs to be to win
INVULNTIME = 2 # how long the player is invulnerable after being hit in seconds
GAMEOVERTIME = 4 # how long the "game over" text stays on the screen in seconds
MAXHEALTH = 3 # how much health the player starts with
NUMGRASS = 80 # number of grass objects in the active area
NUMSQUIRRELS = 30 # number of squirrels in the active area
SQUIRRELMINSPEED = 3 # slowest squirrel speed
SQUIRRELMAXSPEED = 7 # fastest squirrel speed
DIRCHANGEFREQ = 2 # % chance of direction change per frame

LEFT = 'left'
RIGHT = 'right'

"""
This program has three data structures to represent the player, enemy squirrels, and grass background objects. The data structures are dictionaries with the following keys:

Keys used by all three data structures:
    'x' - the left edge coordinate of the object in the game world (not a pixel coordinate on the screen)
    'y' - the top edge coordinate of the object in the game world (not a pixel coordinate on the screen)
    'rect' - the pygame.Rect object representing where on the screen the object is located.

Player data structure keys:
    'surface' - the pygame.Surface object that stores the image of the squirrel which will be drawn to the screen.
    'facing' - either set to LEFT or RIGHT, stores which direction the player is facing.
    'size' - the width and height of the player in pixels. (The width & height are always the same.)
    'bounce' - represents at what point in a bounce the player is in. 0 means standing (no bounce), up to BOUNCERATE (the completion of the bounce)
    'health' - an integer showing how many more times the player can be hit by a larger squirrel before dying.

Enemy Squirrel data structure keys:
    'surface' - the pygame.Surface object that stores the image of the squirrel which will be drawn to the screen.
    'movex' - how many pixels per frame the squirrel moves horizontally. A negative integer is moving to the left, a positive to the right.
    'movey' - how many pixels per frame the squirrel moves vertically. A negative integer is moving up, a positive moving down.
    'width' - the width of the squirrel's image, in pixels
    'height' - the height of the squirrel's image, in pixels
    'bounce' - represents at what point in a bounce the player is in. 0 means standing (no bounce), up to BOUNCERATE (the completion of the bounce)
    'bouncerate' - how quickly the squirrel bounces. A lower number means a quicker bounce.
    'bounceheight' - how high (in pixels) the squirrel bounces

Grass data structure keys:
    'grass_image' - an integer that refers to the index of the pygame.Surface object in GRASSIMAGES used for this grass object

"""

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_SQUIR_IMG, R_SQUIR_IMG, GRASSIMAGES

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('gameicon.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Squirrel Eat Squirrel')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    # load the image files
    L_SQUIR_IMG = pygame.image.load('squirrel.png')
    R_SQUIR_IMG = pygame.transform.flip(L_SQUIR_IMG, True, False)
    GRASSIMAGES = []
    for i in range(1, 5):
        GRASSIMAGES.append(pygame.image.load('grass%s.png' % i))

    while True:
        run_game()

def run_game():
    # set up variables for the start of a new game
    invulnerable_mode = False # if the player is invulnerable
    invulnerable_start_time = 0 # time the player became invulnerable
    game_over_mode = False # if the player has lost
    game_over_start_time = 0 # time the player lost
    win_mode = False # if the player has won

    # create the surfaces to hold game text
    game_over_surf = BASICFONT.render('Game Over', True, WHITE)
    game_over_rect = game_over_surf.get_rect()
    game_over_rect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    win_surf = BASICFONT.render('You have achieved OMEGA SQUIRREL!', True, WHITE)
    win_rect = win_surf.get_rect()
    win_rect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    win_surf2 = BASICFONT.render('(Press "r" to restart.)', True, WHITE)
    win_rect2 = win_surf2.get_rect()
    win_rect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

    # camerax and cameray are where the middle of the camera view is
    camerax = 0
    cameray = 0

    grass_objs = [] # stores all the grass objects in the game
    squirrel_objs = [] # stores all the non-player squirrel objects
    # stores the player object:
    player_obj = {'surface': pygame.transform.scale(L_SQUIR_IMG, (STARTSIZE, STARTSIZE)),
                  'facing': LEFT,
                  'size': STARTSIZE,
                  'x': HALF_WINWIDTH,
                  'y': HALF_WINHEIGHT,
                  'bounce': 0,
                  'health': MAXHEALTH}
    
    move_left = False
    move_right = False
    move_up = False
    move_down = False

    # start off with some random grass images on the screen
    for i in range(10):
        grass_objs.append(make_new_grass(camerax, cameray))
        grass_objs[i]['x'] = random.randint(0, WINWIDTH)
        grass_objs[i]['y'] = random.randint(0, WINHEIGHT)

    while True: # main game loop
        # Check if we should turn off invulnerability
        if invulnerable_mode and time.time() - invulnerable_start_time > INVULNTIME:
            invulnerable_mode = False

        # move all the squirrels
        for s_obj in squirrel_objs:
            # move the squirrel, and adjust for their bounce
            s_obj['x'] += s_obj['movex']
            s_obj['y'] += s_obj['movey']
            s_obj['bounce'] += 1
            if s_obj['bounce'] > s_obj['bouncerate']:
                s_obj['bounce'] = 0 # reset bounce amount # ????

            # random change they change direction
            if random.randint(0, 99) < DIRCHANGEFREQ:
                s_obj['movex'] = get_random_velocity()
                s_obj['movey'] = get_random_velocity()
                if s_obj['movex'] > 0: # faces right
                    s_obj['surface'] = pygame.transform.scale(R_SQUIR_IMG,
                        (s_obj['width'], s_obj['height']))
                else:
                    s_obj['surface'] = pygame.transform.scale(L_SQUIR_IMG,
                        (s_obj['width'], s_obj['height']))

        # go through all the objects and see if any need to be deleted.
        # The iteration is done in a reverse order so that index error doesn't occur.
        for i in range(len(grass_objs) - 1, -1, -1):
            if is_outside_active_area(camerax, cameray, grass_objs[i]):
                del grass_objs[i]
        for i in range(len(squirrel_objs) - 1, -1, -1):
            if is_outside_active_area(camerax, cameray, squirrel_objs[i]):
                del squirrel_objs[i]
                    
        # add more grass & squirrels if we don't have enough.
        while len(grass_objs) < NUMGRASS:
            grass_objs.append(make_new_grass(camerax, cameray))
        while len(squirrel_objs) < NUMSQUIRRELS:
            squirrel_objs.append(make_new_squirrel(camerax, cameray))

        # adjust camerax and cameray if beyond the "camera slack"
        player_centerx = player_obj['x'] + int(player_obj['size'] / 2)
        player_centery = player_obj['y'] + int(player_obj['size'] / 2)
        if (camerax + HALF_WINWIDTH) - player_centerx > CAMERASLACK: # Too left
            camerax = player_centerx + CAMERASLACK - HALF_WINWIDTH
        elif player_centerx - (camerax + HALF_WINWIDTH) > CAMERASLACK:
            camerax = player_centerx - CAMERASLACK - HALF_WINWIDTH
        if (cameray + HALF_WINHEIGHT) - player_centery > CAMERASLACK:
            cameray = player_centery + CAMERASLACK - HALF_WINHEIGHT
        elif player_centery - (cameray + HALF_WINHEIGHT) > CAMERASLACK:
            cameray = player_centery - CAMERASLACK - HALF_WINHEIGHT

        # draw the green background
        DISPLAYSURF.fill(GRASSCOLOR)
        
        # draw all the grass objects on the screen
        for g_obj in grass_objs:
            g_rect = pygame.Rect( (g_obj['x'] - camerax,
                g_obj['y'] - cameray,
                g_obj['width'],
                g_obj['height']) )
            DISPLAYSURF.blit(GRASSIMAGES[g_obj['grass_image']], g_rect)

        # draw the other squirrels
        for s_obj in squirrel_objs:
            s_obj['rect'] = pygame.Rect( (s_obj['x'] - camerax,
                    s_obj['y'] - cameray - get_bounce_amount(s_obj['bounce'],
                        s_obj['bouncerate'], s_obj['bounceheight']),
                        s_obj['width'],
                        s_obj['height']) )
            DISPLAYSURF.blit(s_obj['surface'], s_obj['rect'])

        # draw the player squirrel
        flash_is_on = round(time.time(), 1) * 10 % 2 == 1
        if not game_over_mode and not (invulnerable_mode and flash_is_on):
            player_obj['rect'] = pygame.Rect( (player_obj['x'] - camerax,
                player_obj['y'] - cameray - get_bounce_amount(player_obj['bounce'],
                    BOUNCERATE,
                    BOUNCEHEIGHT),
                player_obj['size'],
                player_obj['size']) ) # ????
            DISPLAYSURF.blit(player_obj['surface'], player_obj['rect'])

        # draw the health meter
        draw_health_meter(player_obj['health'])

        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    move_down = False
                    move_up = True
                elif event.key in (K_DOWN, K_s):
                    move_up = False
                    move_down = True
                elif event.key in (K_LEFT, K_a):
                    move_right = False
                    move_left = True
                    if player_obj['facing'] == RIGHT: # change player image
                        player_obj['surface'] = pygame.transform.scale(L_SQUIR_IMG,
                            (player_obj['size'], player_obj['size']))
                    player_obj['facing'] = LEFT
                elif event.key in (K_RIGHT, K_d):
                    move_left = False
                    move_right = True
                    if player_obj['facing'] == LEFT: # change player image
                        player_obj['surface'] = pygame.transform.scale(R_SQUIR_IMG,
                            (player_obj['size'], player_obj['size']))
                    player_obj['facing'] = RIGHT
                elif win_mode and event.key == K_r:
                    return # if you won and press r, restart the game

            elif event.type == KEYUP:
                # stop moving the player's squirrel
                if event.key in (K_LEFT, K_a):
                    move_left = False
                elif event.key in (K_RIGHT, K_d):
                    move_right = False
                elif event.key in (K_UP, K_w):
                    move_up = False
                elif event.key in (K_DOWN, K_s):
                    move_down = False
                elif event.key == K_ESCAPE:
                    terminate()

        if not game_over_mode:
            # actually move the player
            if move_left:
                player_obj['x'] -= MOVERATE
            if move_right:
                player_obj['x'] += MOVERATE
            if move_up:
                player_obj['y'] -= MOVERATE
            if move_down:
                player_obj['y'] += MOVERATE
            if (move_left or move_right or move_up or move_down) or player_obj['bounce'] != 0:
                player_obj['bounce'] += 1 # ????
            if player_obj['bounce'] > BOUNCERATE:
                player_obj['bounce'] = 0 # reset bounce amount # ????

            # check if the player has collided with any squirrels
            for i in range(len(squirrel_objs)-1, -1, -1):
                sq_obj = squirrel_objs[i]
                if 'rect' in sq_obj and player_obj['rect'].colliderect(sq_obj['rect']):
                    # a player/squirrel collision has occurred
                    if sq_obj['width'] * sq_obj['height'] <= player_obj['size']**2:
                        # player is larger and eats the squirrel
                        player_obj['size'] += int( (sq_obj['width'] * sq_obj['height'])**0.2 ) + 1
                        del squirrel_objs[i]

                        if player_obj['facing'] == LEFT:
                            player_obj['surface'] = pygame.transform.scale(L_SQUIR_IMG,
                                (player_obj['size'], player_obj['size']))
                        if player_obj['facing'] == RIGHT:
                            player_obj['surface'] = pygame.transform.scale(R_SQUIR_IMG,
                                (player_obj['size'], player_obj['size']))
                        if player_obj['size'] > WINSIZE:
                            win_mode = True # turn on "win mode"

                    elif not invulnerable_mode:
                        # player is smaller and takes damage
                        invulnerable_mode = True
                        invulnerable_start_time = time.time()
                        player_obj['health'] -= 1
                        if player_obj['health'] == 0:
                            game_over_mode = True # turn on "game over mode"
                            game_over_start_time = time.time()
        else:
            # game is over, show "game over" text
            DISPLAYSURF.blit(game_over_surf, game_over_rect)
            if time.time() - game_over_start_time > GAMEOVERTIME:
                return # end the current game

        # check if the player has won
        if win_mode:
            DISPLAYSURF.blit(win_surf, win_rect)
            DISPLAYSURF.blit(win_surf2, win_rect2)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def draw_health_meter(current_health):
    for i in range(current_health): # draw red health bars
        pygame.draw.rect(DISPLAYSURF, RED, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10))
    for i in range(MAXHEALTH): # draw the white outlines
        pygame.draw.rect(DISPLAYSURF, WHITE, (15, 5 + (10 * MAXHEALTH) - i * 10, 20, 10), 1)

def terminate():
    pygame.quit()
    sys.exit()

def get_bounce_amount(current_bounce, bounce_rate, bounce_height):
    # Returns the number of pixels to offset based on the bounce.
    # Larger bounce_rate means a slower bounce.
    # Larger bounce_height means a higher bounce.
    # current_bounce will always be less than bounce_rate
    return int(math.sin( (math.pi / float(bounce_rate)) * current_bounce) * bounce_height)

def get_random_velocity():
    speed = random.randint(SQUIRRELMINSPEED, SQUIRRELMAXSPEED)
    if random.randint(0, 1) == 0:
        return speed
    else:
        return -speed

def get_random_off_camera_pos(camerax, cameray, obj_width, obj_height):
    # Returns a position of the object outside of the camera view.

    # create a Rect of the camera view
    camera_rect = pygame.Rect(camerax, cameray, WINWIDTH, WINHEIGHT)
    while True:
        x = random.randint(camerax - WINWIDTH, camerax + (2 * WINWIDTH))
        y = random.randint(cameray - WINHEIGHT, cameray + (2 * WINHEIGHT))
        # create a Rect object with the random coordinates and use colliderect()
        # to make sure the right edge isn't in the camera view.
        obj_rect = pygame.Rect(x, y, obj_width, obj_height)
        if not obj_rect.colliderect(camera_rect):
            return x, y

def make_new_squirrel(camerax, cameray):
    sq = {}
    general_size = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    sq['width'] = (general_size + random.randint(0, 10)) * multiplier
    sq['height'] = (general_size + random.randint(0, 10)) * multiplier
    sq['x'], sq['y'] = get_random_off_camera_pos(camerax, cameray, sq['width'], sq['height'])
    sq['movex'] = get_random_velocity()
    sq['movey'] = get_random_velocity()
    if sq['movex'] < 0: # squirrel is facing left
        sq['surface'] = pygame.transform.scale(L_SQUIR_IMG, (sq['width'], sq['height']))
    else: # squirrel is facing right
        sq['surface'] = pygame.transform.scale(R_SQUIR_IMG, (sq['width'], sq['height']))
    sq['bounce'] = 0
    sq['bouncerate'] = random.randint(10, 18)
    sq['bounceheight'] = random.randint(10, 50)
    return sq

def make_new_grass(camerax, cameray):
    gr = {}
    gr['grass_image'] = random.randint(0, len(GRASSIMAGES) - 1)
    gr['width'] = GRASSIMAGES[0].get_width()
    gr['height'] = GRASSIMAGES[0].get_height()
    gr['x'], gr['y'] = get_random_off_camera_pos(camerax, cameray, gr['width'], gr['height'])
    gr['rect'] = pygame.Rect( (gr['x'], gr['y'], gr['width'], gr['height']) )
    return gr

def is_outside_active_area(camerax, cameray, obj):
    # Return False if camerax and cameray are more than
    # a half-window length beyond the edge of the window.
    bounds_left_edge = camerax - WINWIDTH
    bounds_top_edge = cameray - WINHEIGHT
    bounds_rect = pygame.Rect(bounds_left_edge, bounds_top_edge, WINWIDTH * 3, WINHEIGHT * 3)
    obj_rect = pygame.Rect(obj['x'], obj['y'], obj['width'], obj['height'])
    return not bounds_rect.colliderect(obj_rect)

if __name__ == '__main__':
    main()

