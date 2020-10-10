# Simulate (a Simon clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Creative Commons BY-NC-SA 3.0 US

import random, sys, time, pygame
from pygame.locals import *

FPS = 60
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FLASHSPEED = 1000 # in milliseconds
FLASHDELAY = 200 # in milliseconds
BUTTONSIZE = 200
BUTTONGAPSIZE = 20
TIMEOUT = 4 # seconds before game over if no button is pushed.

# RGB
WHITE        = (255, 255, 255)
BLACK        = (  0,   0,   0)
BRIGHTRED    = (255,   0,   0)
RED          = (155,   0,   0)
BRIGHTGREEN  = (  0, 255,   0)
GREEN        = (  0, 155,   0)
BRIGHTBLUE   = (  0,   0, 255)
BLUE         = (  0,   0, 155)
BRIGHTYELLOW = (255, 255,   0)
YELLOW       = (155, 155,   0)
DARKGRAY     = ( 40,  40,  40)

bg_color = BLACK

XMARGIN = int((WINDOWWIDTH - (2 * BUTTONSIZE) - (BUTTONGAPSIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (2 * BUTTONSIZE) - (BUTTONGAPSIZE)) / 2)

# Rect objects for each of the four buttons
YELLOWRECT = pygame.Rect(XMARGIN, YMARGIN, BUTTONSIZE, BUTTONSIZE)
BLUERECT = pygame.Rect(XMARGIN + BUTTONSIZE + BUTTONGAPSIZE, YMARGIN, BUTTONSIZE, BUTTONSIZE)
REDRECT = pygame.Rect(XMARGIN, YMARGIN + BUTTONSIZE + BUTTONGAPSIZE, BUTTONSIZE, BUTTONSIZE)
GREENRECT = pygame.Rect(XMARGIN + BUTTONSIZE + BUTTONGAPSIZE, YMARGIN + BUTTONSIZE + BUTTONGAPSIZE, BUTTONSIZE, BUTTONSIZE)

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BEEP1, BEEP2, BEEP3, BEEP4
    
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Simulate')

    BASICFONT = pygame.font.Font('freesansbold.ttf', 16)

    info_surf = BASICFONT.render('Match the pattern by clicking on the button or using the Q, W, A, S keys.', 1, DARKGRAY)
    info_rect = info_surf.get_rect()
    info_rect.topleft = (10, WINDOWHEIGHT - 25)

    # load the sound files
    BEEP1 = pygame.mixer.Sound('beep1.ogg')
    BEEP2 = pygame.mixer.Sound('beep2.ogg')
    BEEP3 = pygame.mixer.Sound('beep3.ogg')
    BEEP4 = pygame.mixer.Sound('beep4.ogg')

    # initialize some variables for a new game
    pattern = [] # stores the pattern of colors
    current_step = 0 # the color the player must push next
    last_click_time = 0 # timestamp of the player's last button push
    score = 0
    # when False, the pattern is playing.
    # when True, waiting for the player to click a colored button.
    waiting_for_input = False

    while True: # main game loop
        clicked_button = None # button that was clicked (set to YELLOW, RED, GREEN, or BLUE)
        DISPLAYSURF.fill(bg_color)
        draw_buttons()

        score_surf = BASICFONT.render('Score: ' + str(score), 1, WHITE)
        score_rect = score_surf.get_rect()
        score_rect.topleft = (WINDOWWIDTH - 100, 10)
        DISPLAYSURF.blit(score_surf, score_rect)
        DISPLAYSURF.blit(info_surf, info_rect)

        check_for_quit()

        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                clicked_button = get_button_clicked(mousex, mousey)
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    clicked_button = YELLOW
                elif event.key == K_w:
                    clicked_button = BLUE
                elif event.key == K_a:
                    clicked_button = RED
                elif event.key == K_s:
                    clicked_button = GREEN
        
        if not waiting_for_input:
            # play the pattern
            pygame.display.update()
            pygame.time.wait(1000)
            pattern.append(random.choice((YELLOW, BLUE, RED, GREEN)))

            for button in pattern:
                flash_button_animation(button)
                pygame.time.wait(FLASHDELAY)

            waiting_for_input = True
        else:
            # wait for the player to enter buttons
            if clicked_button and clicked_button == pattern[current_step]:
                # pushed the currect button
                flash_button_animation(clicked_button)
                current_step += 1
                last_click_time = time.time()

                if current_step == len(pattern):
                    # pushed the last button in the pattern
                    change_background_animation()
                    score += 1
                    waiting_for_input = False
                    current_step = 0 # reset back to first step
            elif (clicked_button and clicked_button != pattern[current_step]) or (current_step != 0 and time.time() - TIMEOUT > last_click_time):
                # pushed the incorrect button, or has timed out
                game_over_animation()
                # reset the variables for a new game
                pattern = []
                current_step = 0
                waiting_for_input = False
                score = 0
                pygame.time.wait(1000)
                change_background_animation()

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def terminate():
    pygame.quit()
    sys.exit()

def check_for_quit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back

def flash_button_animation(color, animation_speed = 50):
    if color == YELLOW:
        sound = BEEP1
        flash_color = BRIGHTYELLOW
        rectangle = YELLOWRECT
    elif color == BLUE:
        sound = BEEP2
        flash_color = BRIGHTBLUE
        rectangle = BLUERECT
    elif color == RED:
        sound = BEEP3
        flash_color = BRIGHTRED
        rectangle = REDRECT
    elif color == GREEN:
        sound = BEEP4
        flash_color = BRIGHTGREEN
        rectangle = GREENRECT

    orig_surf = DISPLAYSURF.copy()
    flash_surf = pygame.Surface((BUTTONSIZE, BUTTONSIZE))
    flash_surf = flash_surf.convert_alpha()
    r, g, b = flash_color

    sound.play()

    for start, end, step in ((0, 255, 1), (255, 0, -1)): # animation loop
        for alpha in range(start, end, animation_speed * step):
            check_for_quit()
            DISPLAYSURF.blit(orig_surf, (0, 0))
            flash_surf.fill((r, g, b, alpha))
            DISPLAYSURF.blit(flash_surf, rectangle.topleft)
            pygame.display.update()
            FPSCLOCK.tick(FPS)

    DISPLAYSURF.blit(orig_surf, (0, 0))

def draw_buttons():
    pygame.draw.rect(DISPLAYSURF, YELLOW, YELLOWRECT)
    pygame.draw.rect(DISPLAYSURF, BLUE, BLUERECT)
    pygame.draw.rect(DISPLAYSURF, RED, REDRECT)
    pygame.draw.rect(DISPLAYSURF, GREEN, GREENRECT)

def change_background_animation(animation_speed=20):
    global bg_color
    new_bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    new_bg_surf = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))
    new_bg_surf = new_bg_surf.convert_alpha()
    r, g, b = new_bg_color

    for alpha in range(0, 255, animation_speed): # animation loop
        check_for_quit()
        DISPLAYSURF.fill(bg_color)

        new_bg_surf.fill((r, g, b, alpha))
        DISPLAYSURF.blit(new_bg_surf, (0, 0))

        draw_buttons() # redraw the buttons on top of the tint

        pygame.display.update()
        FPSCLOCK.tick(FPS)
    bg_color = new_bg_color

def game_over_animation(color=WHITE, animation_speed=25):
    # play all beeps at once, then flash the background
    orig_surf = DISPLAYSURF.copy()
    flash_surf = pygame.Surface(DISPLAYSURF.get_size())
    flash_surf = flash_surf.convert_alpha()
    BEEP1.play() # play all four beeps at the same time, roughly.
    BEEP2.play()
    BEEP3.play()
    BEEP4.play()

    r, g, b = color

    for i in range(3): # do the flash 3 times
        for start, end, step in ((0, 255, 1), (255, 0, -1)):
            # the first iteration in this loop sets the following for loop
            # to go from 0 to 255, the second from 255 to 0.
            for alpha in range(start, end, animation_speed * step): # animation loop
                # alpha means transparency. 255 is opaque, 0 is invisible
                check_for_quit()
                flash_surf.fill((r, g, b, alpha))
                DISPLAYSURF.blit(orig_surf, (0, 0))
                DISPLAYSURF.blit(flash_surf, (0, 0))
                draw_buttons()
                pygame.display.update()
                FPSCLOCK.tick(FPS)

def get_button_clicked(x, y):
    if YELLOWRECT.collidepoint( (x, y) ):
        return YELLOW
    elif BLUERECT.collidepoint( (x, y) ):
        return BLUE
    elif REDRECT.collidepoint( (x, y) ):
        return RED
    elif GREENRECT.collidepoint( (x, y) ):
        return GREEN
    return None

if __name__ == '__main__':
    main()
