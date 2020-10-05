# Slide Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Creative Commons BY-NC-SA 3.0 US

import pygame, sys, random
from pygame.locals import *

# Create the constants (go ahead and experiment with different values)
BOARDWIDTH = 4 # number of columns in the board
BOARDHEIGHT = 4 # number of rows in the board
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 60
BLANK = None

# RGB
BLACK         = (  0,   0,   0)
WHITE         = (255, 255, 255)
BRIGHTBLUE    = (  0,  50, 255)
DARKTURQUOISE = (  3,  54,  73)
GREEN         = (   0, 204,  0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = GREEN
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

BASICFONTSIZE = 20

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2) # (640 - ( 80 * 4 + (4 - 1))) /2 = 158
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

def main():
    global FPSCLOCK
    global DISPLAYSURF
    global BASICFONT
    global RESET_SURF
    global RESET_RECT
    global NEW_SURF
    global NEW_RECT
    global SOLVE_SURF
    global SOLVE_RECT

    pygame.init() 
    FPSCLOCK =  pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Slide Puzzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    # Store the option buttons and their rectangles in OPTIONS.
    RESET_SURF, RESET_RECT = make_text(
        'Reset',
        TEXTCOLOR,
        TILECOLOR,
        WINDOWWIDTH - 120,
        WINDOWHEIGHT - 90)
    NEW_SURF, NEW_RECT = make_text(
        'New Game',
        TEXTCOLOR,
        TILECOLOR,
        WINDOWWIDTH - 120,
        WINDOWHEIGHT - 60)
    SOLVE_SURF, SOLVE_RECT = make_text(
        'Solve',
        TEXTCOLOR,
        TILECOLOR,
        WINDOWWIDTH - 120,
        WINDOWHEIGHT - 30)
    
    main_board, solution_seq = generate_new_puzzle(80)
    SOLVEDBOARD = get_starting_board() # a solved board is the same as the board in a start state.
    all_moves = [] # list of moves made from the solved configuration

    while True: # main game loop
        slide_to = None # the direction, if any, a tile should slide
        msg = '' # contains the message to show in the upper left corner.

        if main_board == SOLVEDBOARD:
            msg = 'Solved!'
        
        draw_board(main_board, msg)

        check_for_quit()

        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = get_spot_clicked(main_board, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    # check if the user clicked on an option button
                    if RESET_RECT.collidepoint(event.pos):
                        reset_animation(main_board, all_moves) # clicked on Reset button
                        all_moves = []
                    elif NEW_RECT.collidepoint(event.pos):
                        main_board, solution_seq = generate_new_puzzle(80) # clicked on New Game button
                        all_moves = []
                    elif SOLVE_RECT.collidepoint(event.pos):
                        reset_animation(main_board, solution_seq + all_moves) # clicked on Solve button
                else:
                    # check if the clicked tile was next to the blank spot
                    blankx, blanky = get_blank_position(main_board)
                    if spotx == blankx + 1 and spoty == blanky:
                        slide_to = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slide_to = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slide_to = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slide_to = DOWN
            elif event.type == KEYUP:
                # check if the user pressed a key to slide a tile
                if event.key in (K_LEFT, K_a) and is_valid_move(main_board, LEFT):
                    slide_to = LEFT
                elif event.key in (K_RIGHT, K_d) and is_valid_move(main_board, RIGHT):
                    slide_to = RIGHT
                elif event.key in (K_UP, K_w) and is_valid_move(main_board, UP):
                    slide_to = UP
                elif event.key in (K_DOWN, K_s) and is_valid_move(main_board, DOWN):
                    slide_to = DOWN
        
        if slide_to:
            slide_animation(main_board, slide_to, 'Click tile or press arrow keys to slide.', 8) # show slide on screen
            make_move(main_board, slide_to)
            all_moves.append(slide_to) # record the slide
        
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
        pygame.event.post(event) # put the other KEYUP event objects back into Pygame's event queue
                
def get_starting_board():
    # Return a board data structure with tiles in the solved state.
    # For example, if BOARDWIDTH and BOARDHEIGHT are both 3, this function
    # returns [[1, 4, 7], [2, 5, 8], [3, 6, None]]
    counter = 1
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(counter)
            counter += BOARDWIDTH
        board.append(column)
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1
    
    board[BOARDWIDTH-1][BOARDHEIGHT-1] = None

    return board
                    
def get_blank_position(board):
    # Return the x and y of board coordinates of the blank space.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == None:
                return (x, y)

def make_move(board, move):
    # This function does not check if the move is valid.
    print('make_move() triggered!')
    print(f'move: {move}')
    print(f'board before: {board}')

    blankx, blanky = get_blank_position(board)

    print(f'blankx: {blankx}, blanky: {blanky}')

    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = \
            board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = \
            board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = \
            board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = \
            board[blankx - 1][blanky], board[blankx][blanky]

    print(f'board after: {board}')

def is_valid_move(board, move):
    blankx, blanky = get_blank_position(board)
    return (move == UP and blanky != len(board[0]) - 1) or \
        (move == DOWN and blanky != 0) or \
        (move == LEFT and blankx != len(board) - 1) or \
        (move == RIGHT and blankx != 0)
    
def get_random_move(board, last_move=None):
    # start with a full list of all four moves
    valid_moves = [UP, DOWN, LEFT, RIGHT]

    # remove moves from the list as they are disqualified
    if last_move == UP or not is_valid_move(board, DOWN):
        valid_moves.remove(DOWN)
    if last_move == DOWN or not is_valid_move(board, UP):
        valid_moves.remove(UP)
    if last_move == LEFT or not is_valid_move(board, RIGHT):
        valid_moves.remove(RIGHT)
    if last_move == RIGHT or not is_valid_move(board, LEFT):
        valid_moves.remove(LEFT)
    
    print('get_random_move() triggered!')
    print(f'board: {board}, last_move: {last_move}')
    print(f'is_valid_move(board, DOWN): {is_valid_move(board, DOWN)}')
    print(f'is_valid_move(board, UP): {is_valid_move(board, UP)}')
    print(f'is_valid_move(board, RIGHT): {is_valid_move(board, RIGHT)}')
    print(f'is_valid_move(board, LEFT): {is_valid_move(board, LEFT)}')

    # return a random move from the list of remaining moves
    return random.choice(valid_moves)

def get_left_top_of_tile(tilex, tiley):
    # tilex: 0 ~ (BOARDWIDTH - 1)
    # tiley: 0 ~ (BOARDHEIGHT - 1)
    left = XMARGIN + (tilex * TILESIZE) + (tilex - 1)
    top = YMARGIN + (tiley * TILESIZE) + (tiley - 1)

    # print('get_left_top_of_tile() triggered!')
    # print(f'tilex: {tilex}, tiley: {tiley}, left: {left}, top: {top} ')
    return (left, top)
    
def get_spot_clicked(board, x, y):
    # from the x & y pixel coordinates, get the x & y board coordinates
    print('get_spot_clicked() clicked')
    print(f'x: {x}, y: {y}')

    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            left, top = get_left_top_of_tile(tilex, tiley)
            print(f'left: {left}, top: {top}')
            tile_rect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tile_rect.collidepoint(x, y):
                return (tilex, tiley)
    return (None, None)

def draw_tile(tilex, tiley, number, adjx=0, adjy=0):
    # draw a tile at board coordinates tilex and tiley, optionally a few
    # pixels over (determined by adjx and adjy)
    left, top = get_left_top_of_tile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE))
    text_surf = BASICFONT.render(str(number), True, TEXTCOLOR)
    text_rect = text_surf.get_rect()
    text_rect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
    DISPLAYSURF.blit(text_surf, text_rect)

def make_text(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    text_surf = BASICFONT.render(text, True, color, bgcolor)
    text_rect = text_surf.get_rect()
    text_rect.topleft = (top, left)
    return (text_surf, text_rect)

def draw_board(board, message):
    DISPLAYSURF.fill(BGCOLOR)

    if message:
        text_surf, text_rect = make_text(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(text_surf, text_rect)
    
    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                draw_tile(tilex, tiley, board[tilex][tiley])
    
    left, top = get_left_top_of_tile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)

def slide_animation(board, direction, message, animation_speed):
    # Note: This function does not check if the move is valid.

    blankx, blanky = get_blank_position(board)
    if direction == UP:
        movex = blankx
        movey = blanky + 1
    elif direction == DOWN:
        movex = blankx
        movey = blanky - 1
    elif direction == LEFT:
        movex = blankx + 1
        movey = blanky
    elif direction == RIGHT:
        movex = blankx - 1
        movey = blanky

    # prepare the base surface
    draw_board(board, message)
    base_surf = DISPLAYSURF.copy()

    # draw a blank space over the moving tile on the base_surf Surface.
    move_left, move_top = get_left_top_of_tile(movex, movey)
    pygame.draw.rect(base_surf, BGCOLOR, (move_left, move_top, TILESIZE, TILESIZE))

    print('slide_animation triggered!')
    print(f'board: {board}, direction: {direction}')
    print(f'blankx: {blankx}, blanky: {blanky}, movex: {movex}, movey: {movey}')
    for i in range(0, TILESIZE, animation_speed):
        # animate the tile sliding over
        check_for_quit()
        DISPLAYSURF.blit(base_surf, (0, 0))

        if direction == UP:
            draw_tile(movex, movey, board[movex][movey], 0, -i)
        if direction == DOWN:
            draw_tile(movex, movey, board[movex][movey], 0, i)
        if direction == LEFT:
            draw_tile(movex, movey, board[movex][movey], -i, 0)
        if direction == RIGHT:
            draw_tile(movex, movey, board[movex][movey], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def generate_new_puzzle(num_slides):
    # from a starting configuration, make num_slides number of moves
    # (and animate these moves).
    sequence = []
    board = get_starting_board()
    draw_board(board, '')
    pygame.display.update()
    pygame.time.wait(500) # pause 500 milliseconds for effect
    last_move = None

    for i in range(num_slides):
        move = get_random_move(board, last_move)
        slide_animation(board, move, 'Generating new puzzle...', int(TILESIZE / 3))
        make_move(board, move)
        sequence.append(move)
        last_move = move

    return (board, sequence)

def reset_animation(board, all_moves):
    # make all of the moves in all_moves in reverse.
    rev_all_moves = all_moves[:] # gets a copy of the list
    rev_all_moves.reverse()

    for move in rev_all_moves:
        if move == UP:
            opposite_move = DOWN
        elif move == DOWN:
            opposite_move = UP
        elif move == RIGHT:
            opposite_move = LEFT
        elif move == LEFT:
            opposite_move = RIGHT

        slide_animation(board, opposite_move, '', int(TILESIZE / 2))
        make_move(board, opposite_move)

if __name__ == '__main__':
    main()

