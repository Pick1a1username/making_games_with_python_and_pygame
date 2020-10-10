# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Creative Commons BY-NC-SA 3.0 US

import random, pygame, sys
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

# RGB
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (0  , 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR   = BLACK

UP    = 'up'
DOWN  = 'down'
LEFT  = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    show_start_screen()
    while True:
        run_game()
        show_game_over_screen()

def run_game():
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    worm_coords = [
        {'x': startx, 'y': starty},
        {'x': startx - 1, 'y': starty},
        {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    # Start the apple in a random place.
    apple = get_random_location()

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_a) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()
        # check if the worm has hit itself or the edge
        if worm_coords[HEAD]['x'] == -1 or worm_coords[HEAD]['x'] == CELLWIDTH or worm_coords[HEAD]['y'] == -1 or worm_coords[HEAD]['y'] == CELLHEIGHT:
            return # game over
        for worm_body in worm_coords[1:]:
            if worm_body['x'] == worm_coords[HEAD]['x'] and worm_body['y'] == worm_coords[HEAD]['y']:
                return # game over

        # check if worm has eaten an apple
        if worm_coords[HEAD]['x'] == apple['x'] and worm_coords[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            apple = get_random_location() # set a new aple somewhere
        else:
            # remove worm's tail segment
            del worm_coords[-1]

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            new_head = {'x': worm_coords[HEAD]['x'], 'y': worm_coords[HEAD]['y'] - 1}
        elif direction == DOWN:
            new_head = {'x': worm_coords[HEAD]['x'], 'y': worm_coords[HEAD]['y'] + 1}
        elif direction == LEFT:
            new_head = {'x': worm_coords[HEAD]['x'] - 1, 'y': worm_coords[HEAD]['y']}
        elif direction == RIGHT:
            new_head = {'x': worm_coords[HEAD]['x'] + 1, 'y': worm_coords[HEAD]['y']}
        worm_coords.insert(0, new_head)
        
        DISPLAYSURF.fill(BGCOLOR)
        draw_grid()
        draw_worm(worm_coords)
        draw_apple(apple)
        draw_score(len(worm_coords) - 3)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def draw_press_key_msg():
    press_key_surf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    press_key_rect = press_key_surf.get_rect()
    press_key_rect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(press_key_surf, press_key_rect)

def check_for_key_press():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    key_up_events = pygame.event.get(KEYUP)
    if len(key_up_events) == 0:
        return None
    if key_up_events[0].key == K_ESCAPE:
        terminate()
    return key_up_events[0].key

def show_start_screen():
    title_font = pygame.font.Font('freesansbold.ttf', 100)
    title_surf1 = title_font.render('Wormy!', True, WHITE, DARKGREEN)
    title_surf2 = title_font.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0

    while True:
        DISPLAYSURF.fill(BGCOLOR)

        rotated_surf1 = pygame.transform.rotate(title_surf1, degrees1)
        rotated_rect1 = rotated_surf1.get_rect()
        rotated_rect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotated_surf1, rotated_rect1)

        rotated_surf2 = pygame.transform.rotate(title_surf2, degrees2)
        rotated_rect2 = rotated_surf2.get_rect()
        rotated_rect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotated_surf2, rotated_rect2)

        draw_press_key_msg()

        if check_for_key_press():
            pygame.event.get() # clear event queue
            return

        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame

def terminate():
    pygame.quit()
    sys.exit()

def get_random_location():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}

def show_game_over_screen():
    game_over_font = pygame.font.Font('freesansbold.ttf', 150)
    game_surf = game_over_font.render('Game', True, WHITE)
    over_surf = game_over_font.render('Over', True, WHITE)
    game_rect = game_surf.get_rect()
    over_rect = over_surf.get_rect()
    game_rect.midtop = (WINDOWWIDTH / 2, 10)
    over_rect.midtop = (WINDOWWIDTH / 2, game_rect.height + 10 + 25)

    DISPLAYSURF.blit(game_surf, game_rect)
    DISPLAYSURF.blit(over_surf, over_rect)
    draw_press_key_msg()
    pygame.display.update()
    pygame.time.wait(500)
    check_for_key_press() # clear out any key presses in the event queue

    while True:
        if check_for_key_press():
            pygame.event.get() # clear event queue
            return

def draw_score(score):
    score_surf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    score_rect = score_surf.get_rect()
    score_rect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(score_surf, score_rect)

def draw_worm(worm_coords):
    for coord in worm_coords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        worm_segment_rect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, worm_segment_rect)
        worm_inner_segment_rect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, worm_inner_segment_rect)

def draw_apple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    apple_rect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, apple_rect)

def draw_grid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

if __name__ == '__main__':
    main()
