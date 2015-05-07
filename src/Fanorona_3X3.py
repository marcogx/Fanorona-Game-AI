# Copyright 2014 by Guang XIONG  gx239@nyu.edu  N17366328
# Fanorona on 3X3 grid played by one human player and one AI player.


import random
import sys
import time
import copy
import pygame
from pygame.locals import *

FPS = 20  # frames per second to update the screen
WINDOW_WIDTH = 800  # width of the program's window, in pixels
WINDOW_HEIGHT = 800  # height in pixels
GRID_SIZE = 80  # width & height of each position on the grid, in pixels
GRID_WIDTH = 3  # how many columns of grid on the game board
GRID_HEIGHT = 3  # how many rows of spaces on the game board

#color         R    G    B
WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
GREEN      = (  0, 155,   0)
BROWN      = (174,  94,   0)
EMPTY      = 'EMPTY'  # nothing to draw on the grid


def main():
    pygame.init()
    pygame.display.set_caption('Fanorona 3X3 by Guang XIONG')

    global main_clock, WINDOW_SURF, FONT, BIG_FONT, BG_IMAGE
    main_clock = pygame.time.Clock()
    WINDOW_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    FONT = pygame.font.Font('freesansbold.ttf', 20)
    BIG_FONT = pygame.font.Font('freesansbold.ttf', 25)
    BG_IMAGE = pygame.image.load('../images/ThreeByThree.png')
    BG_IMAGE = pygame.transform.smoothscale(
        BG_IMAGE,
        (int(WINDOW_WIDTH*0.5),int(WINDOW_HEIGHT*0.5)))

    while True:
        if run_fanorona_3X3() == False:
            break





def run_fanorona_3X3():
    """Plays a round of game Fanorona each time this function is called.
    """
    main_grid = get_new_grid_3X3()  # 2-dimensional array to stores information of all tokens
    draw_grid(main_grid)
    global difficulty
    difficulty = enter_player_difficulty()
    draw_grid(main_grid)

    global human_token, AI_token
    human_token, AI_token = enter_player_token()
    if human_token == WHITE:  # decide whose turn to move first
        turn = 'Human'
    else:
        turn = 'AI'
    print human_token, AI_token, turn
    print '\n', '\n'
    draw_grid(main_grid)

    global AI_current_action  # a table hashes max_value to according action (start_coord, end_coord)
    global is_cutoff, depth_of_game_tree, total_node_generated, pruning_in_max_value, pruning_in_min_value
    AI_current_action = {}
    is_cutoff = False
    depth_of_game_tree = 0
    total_node_generated = 0
    pruning_in_max_value = 0
    pruning_in_min_value = 0

    while True:  # main game loop
        if turn == 'Human':  # Keep looping for player and computer's turns.
            print "You Human's turn"
            human_movable_token_table = get_movable_token_information(human_token, main_grid)
            if human_movable_token_table == {}:
                show_game_results('AI', 'You Human')
            check_for_draw(main_grid, turn)

            click_grid_coord = None
            move_grid_coord = None
            while move_grid_coord == None:
                show_statistics()
                while click_grid_coord == None:
                    main_clock.tick(FPS)
                    for event in pygame.event.get(): # event handling loop
                        main_clock.tick(FPS)
                        if event.type == MOUSEBUTTONDOWN and event.button == 1:
                            mouse_x, mouse_y = event.pos
                            click_grid_coord = get_grid_clicked((mouse_x, mouse_y))
                            if click_grid_coord not in human_movable_token_table:
                                click_grid_coord = None

                        if event.type == QUIT:
                            pygame.quit()
                            sys.exit()

                # when grid got clicked, extra green circle shows it.
                pygame.draw.circle(
                    WINDOW_SURF,
                    GREEN,
                    translate_grid_to_pixel_coord(click_grid_coord),
                    int(GRID_SIZE*0.5),
                    10)

                main_clock.tick(FPS)
                pygame.display.update()
                main_clock.tick(FPS)

                # when a valid movable token got clicked, its accordingly available empty grid
                # coordinates start being detected.

                for event in pygame.event.get():
                    if event.type == QUIT:
                            pygame.quit()
                            sys.exit()

                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        mouse_x, mouse_y = event.pos
                        move_grid_coord = get_grid_clicked((mouse_x, mouse_y))
                        if move_grid_coord not in human_movable_token_table[click_grid_coord]:
                            if move_grid_coord in human_movable_token_table:
                                click_grid_coord = move_grid_coord
                                move_grid_coord = None

                                draw_grid(main_grid)
                                pygame.draw.circle(
                                    WINDOW_SURF,
                                    GREEN,
                                    translate_grid_to_pixel_coord(click_grid_coord),
                                    int(GRID_SIZE*0.5),
                                    10)

                                main_clock.tick(FPS)
                                pygame.display.update()
                                main_clock.tick(FPS)
                            else:
                                move_grid_coord = None

            make_move(human_token, main_grid, click_grid_coord, move_grid_coord, True)
            draw_grid(main_grid)
            turn = 'AI'

        elif turn == 'AI':
            AI_current_action = {}
            is_cutoff = False
            depth_of_game_tree = 0
            total_node_generated = 0
            pruning_in_max_value = 0
            pruning_in_min_value = 0
            print "AI's turn\n"
            print "AI_state: \n", main_grid,'\n\n'

            AI_movable_token_table = get_movable_token_information(AI_token, main_grid, False)
            if AI_movable_token_table == {}:
                show_game_results('You Human', 'AI')
            check_for_draw(main_grid, turn)

            if difficulty == 'r':
                start_grid_coord = AI_movable_token_table.keys()[0]
                end_grid_coord = AI_movable_token_table[start_grid_coord].keys()[0]
            else:
                start_grid_coord, end_grid_coord = alpha_beta_search(main_grid, -1, 1)

            make_move(AI_token, main_grid, start_grid_coord, end_grid_coord)
            draw_grid(main_grid)


            print "after make_move from ", start_grid_coord, " to ", end_grid_coord, '\n'
            print "AI_state: \n", main_grid, '\n\n'
            turn = 'Human'

    return True


def enter_player_difficulty():
    text_surf = BIG_FONT.render('Welcome to Fanorona~! Which level would you choose', True, BLACK)
    text_rect = text_surf.get_rect()
    text_rect.center = (int(WINDOW_WIDTH*0.5), int(WINDOW_HEIGHT*0.875))

    white_surf = BIG_FONT.render('1 (random move)', True, BLACK)
    white_rect = white_surf.get_rect()
    white_rect.center = (int(WINDOW_WIDTH*0.25), int(WINDOW_HEIGHT*0.9375))

    grey_surf = BIG_FONT.render('2 (one depth)', True, BLACK)
    grey_rect = grey_surf.get_rect()
    grey_rect.center = (int(WINDOW_WIDTH*0.5), int(WINDOW_HEIGHT*0.9375))

    black_surf = BIG_FONT.render('3 (deep depth)', True, BLACK)
    black_rect = black_surf.get_rect()
    black_rect.center = (int(WINDOW_WIDTH*0.75), int(WINDOW_HEIGHT*0.9375))

    while True:  # keep looping until the player has clicked on a color
        main_clock.tick(FPS)  # CPU is too fast that slowing down is needed
        for event in pygame.event.get(): # event handling loop
            main_clock.tick(FPS)
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # print 'click'
                mouse_x, mouse_y = event.pos
                if white_rect.collidepoint((mouse_x, mouse_y)):
                    # print 'white'
                    return 'r'
                elif grey_rect.collidepoint((mouse_x, mouse_y)):
                    return '1'
                elif black_rect.collidepoint((mouse_x, mouse_y)):
                    # print 'black'
                    return '15'

        WINDOW_SURF.blit(text_surf, text_rect)
        WINDOW_SURF.blit(white_surf, white_rect)
        WINDOW_SURF.blit(grey_surf, grey_rect)
        WINDOW_SURF.blit(black_surf, black_rect)
        main_clock.tick(FPS)
        pygame.display.update()
        main_clock.tick(FPS)


def show_statistics():
    global is_cutoff, depth_of_game_tree, total_node_generated, pruning_in_max_value, pruning_in_min_value

    if is_cutoff:
        text_surf1 = FONT.render('Cut-off was used', True, BLACK)
    else:
        text_surf1 = FONT.render('Cut-off was NOT used', True, BLACK)

    text_surf2 = FONT.render('maximum depth of game tree is  ' + str(depth_of_game_tree), True, BLACK)
    text_surf3 = FONT.render('total nodes generated are  ' + str(total_node_generated), True, BLACK)
    text_surf4 = FONT.render('pruning within max_value  ' + str(pruning_in_max_value), True, BLACK)
    text_surf5 = FONT.render('pruning within min_value  ' + str(pruning_in_min_value), True, BLACK)

    text_rect1 = text_surf1.get_rect()
    text_rect1.center = (int(WINDOW_WIDTH*0.5), int(WINDOW_HEIGHT*0.09375))
    text_rect2 = text_surf2.get_rect()
    text_rect2.center = (int(WINDOW_WIDTH*0.3), int(WINDOW_HEIGHT*0.0625))
    text_rect3 = text_surf3.get_rect()
    text_rect3.center = (int(WINDOW_WIDTH*0.75), int(WINDOW_HEIGHT*0.0625))
    text_rect4 = text_surf4.get_rect()
    text_rect4.center = (int(WINDOW_WIDTH*0.3), int(WINDOW_HEIGHT*0.125))
    text_rect5 = text_surf5.get_rect()
    text_rect5.center = (int(WINDOW_WIDTH*0.75), int(WINDOW_HEIGHT*0.125))



    # while True:
    #     for event in pygame.event.get():
    #         if event.type == QUIT:
    #             pygame.quit()
    #             sys.exit()

    WINDOW_SURF.blit(text_surf1, text_rect1)
    WINDOW_SURF.blit(text_surf2, text_rect2)
    WINDOW_SURF.blit(text_surf3, text_rect3)
    WINDOW_SURF.blit(text_surf4, text_rect4)
    WINDOW_SURF.blit(text_surf5, text_rect5)

    main_clock.tick(FPS)
    pygame.display.update()


def check_for_draw(AI_state, turn):
    """check for draw in 3X3 grid by whether the state matches certain patterns
    """
    AI_token_remain_grid_coord = []
    human_token_remain_grid_coord = []
    AI_token_non_central_displacement = ()
    human_token_non_central_displacement = ()

    for column in range(GRID_WIDTH):
        for row in range(GRID_HEIGHT):
            if AI_state[column][row]['token_color'] == AI_token:
                AI_token_remain_grid_coord.append((column, row))
            if AI_state[column][row]['token_color'] == human_token:
                human_token_remain_grid_coord.append((column, row))

    # pattern 1
    if turn == 'AI' and AI_state[1][1]['token_color'] == AI_token and \
        len(AI_token_remain_grid_coord) == 2 and len(human_token_remain_grid_coord) == 1:
        for (column, row) in AI_token_remain_grid_coord:
            if column != 1 and row != 1:
                AI_token_non_central_displacement = (column - 1, row - 1)
        for (column, row) in human_token_remain_grid_coord:
            human_token_non_central_displacement = (1 - column, 1 - row)

        if AI_token_non_central_displacement == human_token_non_central_displacement:
            show_game_results('', '', True)


    # pattern 2
    if turn == 'Human' and AI_state[1][1]['token_color'] == human_token and \
        len(AI_token_remain_grid_coord) == 1 and len(human_token_remain_grid_coord) == 2:
        for (column, row) in human_token_remain_grid_coord:
            if column != 1 and row != 1:
                human_token_non_central_displacement = (column - 1, row - 1)
        for (column, row) in AI_token_remain_grid_coord:
            AI_token_non_central_displacement = (1 - column, 1 - row)

        if AI_token_non_central_displacement == human_token_non_central_displacement:
            show_game_results('', '', True)



def alpha_beta_search(AI_state, minimum_utility, maximum_utility):
    global AI_current_action
    v = max_value(AI_state, minimum_utility, maximum_utility, 0)
    print AI_current_action
    return AI_current_action[v]


def max_value(AI_state, alpha, beta, depth):
    print "\nin max_value body, called ", depth, " levels, current state:\n ", AI_state, '\n'
    global total_node_generated, pruning_in_max_value
    total_node_generated += 1
    global AI_current_action
    global depth_of_game_tree
    if depth >= depth_of_game_tree:
        depth_of_game_tree = depth

    current_alpha = alpha
    current_beta = beta


    # if depth_of_game_tree >= 3:
    #     is_cutoff = True
    #     return evaluate_current_state(AI_state)
    if terminal_test(AI_state):
        print "return since max_value terminated "
        return utility(AI_state)

    AI_movable_token_table = get_movable_token_information(AI_token, AI_state, False)
    current_v = float('-inf')
    for start_grid_coord in AI_movable_token_table.keys():
        for end_grid_coord in AI_movable_token_table[start_grid_coord].keys():
            print "in max_value body, action is choose from ", start_grid_coord, end_grid_coord, '\n\n'

            current_AI_state = copy.deepcopy(AI_state)
            result_state = make_move(AI_token, current_AI_state, start_grid_coord, end_grid_coord)

            v = min_value(result_state, current_alpha, current_beta, depth+1)
            if v > current_v:
                current_v = v
                if depth == 0:
                    AI_current_action[current_v] = (start_grid_coord, end_grid_coord)

                if current_v >= beta:
                    pruning_in_max_value += 1
                    print "return since max_value pruning: ", current_v
                    return current_v
                current_alpha = max(alpha, current_v)
    print "return since all level done in max_value: ", current_v
    return current_v


def min_value(AI_state, alpha, beta, depth):
    print "in min_value body, called ", depth, " level, current state:\n\n ", AI_state, '\n\n'
    global total_node_generated, is_cutoff, pruning_in_min_value, difficulty
    total_node_generated += 1

    global depth_of_game_tree
    if depth > depth_of_game_tree:
        depth_of_game_tree = depth

    current_alpha = alpha
    current_beta = beta


    if depth > int(difficulty):   # cutoff setting, maximum level AI can search through
    # if depth_of_game_tree >= 500:
        is_cutoff = True
        return evaluate_current_state(AI_state)
    if terminal_test(AI_state):
        print "return since terminated"
        return utility(AI_state)


    AI_movable_token_table = get_movable_token_information(human_token, AI_state, False)

    current_v = float('inf')
    for start_grid_coord in AI_movable_token_table.keys():
        for end_grid_coord in AI_movable_token_table[start_grid_coord].keys():
            print "in min_value body, action is choose from ", start_grid_coord, end_grid_coord, '\n\n'

            current_human_state = copy.deepcopy(AI_state)
            result_state = make_move(human_token, current_human_state, start_grid_coord, end_grid_coord)

            v = max_value(result_state, current_alpha, current_beta, depth+1)
            if v < current_v:

                current_v = v

                if current_v <= alpha:
                    pruning_in_min_value += 1
                    print "return since min_value pruning: ", current_v
                    return current_v
                current_beta = min(beta, current_v)

    print "return since all level done in min_value: ", current_v
    return current_v


def terminal_test(AI_state):
    print "terminal_test is called, the current state is: \n", AI_state, '\n'

    AI_token_remain = 0
    human_token_remain = 0

    for column in range(GRID_WIDTH):
        for row in range(GRID_HEIGHT):
            if AI_state[column][row]['token_color'] == AI_token:
                AI_token_remain += 1
            if AI_state[column][row]['token_color'] == human_token:
                human_token_remain += 1

    print "within terminaltest\n ", AI_token_remain, human_token_remain, '\n'

    if AI_token_remain == 0 or human_token_remain == 0:
        return True
    else:
        return False


def utility(AI_state):
    print "when utility is called, AI_state is terminated to results.\n"
    print "before setting depth of game tree to zero, and store it in a collector\n"

    AI_token_remain = 0
    human_token_remain = 0

    for column in range(GRID_WIDTH):
        for row in range(GRID_HEIGHT):
            if AI_state[column][row]['token_color'] == AI_token:
                AI_token_remain += 1
            if AI_state[column][row]['token_color'] == human_token:
                human_token_remain += 1

    if AI_token_remain == 0:
        print "AI left nothing\n"
        return -1
    elif human_token_remain == 0:
        print "human left nothing"
        return 1


def evaluate_current_state(AI_state):
    print "when evalation function called, AI_state cutoff\n"
    AI_token_remain = 0
    human_token_remain = 0

    for column in range(GRID_WIDTH):
        for row in range(GRID_HEIGHT):
            if AI_state[column][row]['token_color'] == AI_token:
                AI_token_remain += 1
            if AI_state[column][row]['token_color'] == human_token:
                human_token_remain += 1

    # special grid coordinates that have position advantage
    for (column, row) in [(1, 1)]:
        if AI_state[column][row]['token_color'] == AI_token:
            AI_token_remain += 0.5
        if AI_state[column][row]['token_color'] == human_token:
            human_token_remain -= 0.5


    return (AI_token_remain-human_token_remain) * 1.0 / (AI_token_remain+human_token_remain)


def get_new_grid_3X3():
    """Returns a 2-dimensional array of token information.
    The first/second array index means column/row number that count from zero.
    Each token information is a hash table containing its token color and
    displacements of all adjacent grid positions.
    """
    grid = []
    for i in range(GRID_WIDTH):
        grid.append([])

    for coloumn in grid:
        for i in range(GRID_HEIGHT):
            coloumn.append({'token_color': EMPTY,
                            'displacements': []})

    # initialize grid positions with different displacements of
    # all adjacent grid positions

    # first column

    grid[0][0]['token_color'] = BLACK
    for displacement in [(1, 0), (0, 1), (1, 1)]:
        grid[0][0]['displacements'].append(displacement)

    grid[0][1]['token_color'] = BLACK
    for displacement in [(1, 0), (0, 1), (0, -1)]:
        grid[0][1]['displacements'].append(displacement)

    grid[0][2]['token_color'] = WHITE
    for displacement in [(1, -1), (1, 0), (0, -1)]:
        grid[0][2]['displacements'].append(displacement)

    # second column

    grid[1][0]['token_color'] = BLACK
    for displacement in [(1, 0), (0, 1), (-1, 0)]:
        grid[1][0]['displacements'].append(displacement)

    grid[1][1]['token_color'] = EMPTY
    for displacement in [(1, 0), (0, 1), (-1, 0), (0, -1),
                         (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        grid[1][1]['displacements'].append(displacement)


    grid[1][2]['token_color'] = WHITE
    for displacement in [(-1, 0), (0, -1), (1, 0)]:
        grid[1][2]['displacements'].append(displacement)

    # third column

    grid[2][0]['token_color'] = BLACK
    for displacement in [(-1, 0), (0, 1), (-1, 1)]:
        grid[2][0]['displacements'].append(displacement)

    grid[2][1]['token_color'] = WHITE
    for displacement in [(-1, 0), (0, 1), (0, -1)]:
        grid[2][1]['displacements'].append(displacement)

    grid[2][2]['token_color'] = WHITE
    for displacement in [(-1, 0), (0, -1), (-1, -1)]:
        grid[2][2]['displacements'].append(displacement)

    print grid
    return grid


def draw_grid(grid):
    WINDOW_SURF.fill(WHITE)
    WINDOW_SURF.blit(
        BG_IMAGE,
        (int(WINDOW_WIDTH*0.25), int(WINDOW_HEIGHT*0.25)))

    for column in range(GRID_WIDTH):
        for row in range(GRID_HEIGHT):
            center_pixel_coord = translate_grid_to_pixel_coord((column, row))
            # draw token with outline
            if grid[column][row]['token_color'] != EMPTY:
                pygame.draw.circle(
                    WINDOW_SURF,
                    grid[column][row]['token_color'],
                    center_pixel_coord,
                    int(GRID_SIZE*0.5))

                pygame.draw.circle(
                    WINDOW_SURF,
                    BLACK,
                    center_pixel_coord,
                    int(GRID_SIZE*0.5),
                    5)

    main_clock.tick(FPS)
    pygame.display.update()
    main_clock.tick(FPS)


def translate_grid_to_pixel_coord((grid_cloumn, grid_row)):
    return grid_cloumn * int(WINDOW_HEIGHT*0.25) + int(WINDOW_HEIGHT*0.25),\
           grid_row * int(WINDOW_WIDTH*0.25) + int(WINDOW_WIDTH*0.25)


def get_grid_clicked((mouse_x, mouse_y)):
    """ Return a tuple of two integers of the grid space coordinates where
    the mouse was clicked. (Or returns None not in any space.)
    """
    # print 'mouse pixel click received in get_grid_clicked', mouse_x, mouse_y
    # print '\n'
    for column in range(GRID_WIDTH):
        for row in range(GRID_HEIGHT):
            (center_x, center_y) = translate_grid_to_pixel_coord((column, row))
            if (mouse_x > center_x - int(GRID_SIZE*0.5) and
                mouse_x < center_x + int(GRID_SIZE*0.5) and
                mouse_y > center_y - int(GRID_SIZE*0.5) and
                mouse_y < center_y + int(GRID_SIZE*0.5)):
                return (column, row)
    return None


def get_movable_token_information(token_color, grid, is_prompt_bi_direct_capture=True):
    """returns a hash table that hashes each movable token
    coordinate to its own hash table consisting of each accordingly available
    empty grid coordinates to move hashing to its move type.
    """
    capture_move_table = {}
    paika_move_table = {}
    has_capture = False  # a flag shows which table to return

    for column in range(GRID_WIDTH):
        for row in range(GRID_HEIGHT):
            if grid[column][row]['token_color'] == token_color:
                paika_move_table[(column, row)] = {}
                capture_move_table[(column, row)] = {}
                for (delta_x, delta_y) in grid[column][row]['displacements']:

                    # when a token's neighbor is EMPTY, it at least eligible for Paika move
                    # only after a token in Paika list, it will be test for what kind of
                    # capture it fits within the boundary of grid.

                    if grid[column + delta_x][row + delta_y]['token_color'] == EMPTY:
                        paika_move_table[(column, row)][(column + delta_x, row + delta_y)] = 'paika'

                        if is_within_grid(column + 2*delta_x, row + 2*delta_y) and \
                            grid[column + 2*delta_x][row + 2*delta_y]['token_color']\
                                != token_color and \
                                    grid[column + 2*delta_x][row + 2*delta_y]['token_color']\
                                        != EMPTY:
                            capture_move_table[(column, row)][(column + delta_x, row + delta_y)]\
                                = 'approach'
                            has_capture = True

                            if  is_prompt_bi_direct_capture and \
                                    is_within_grid(column - delta_x, row - delta_y) and \
                                        grid[column - delta_x][row - delta_y]['token_color']\
                                            != token_color and \
                                                grid[column - delta_x][row - delta_y]\
                                                    ['token_color'] != EMPTY:
                                capture_move_table[(column, row)][(column + delta_x, row + delta_y)]\
                                    = 'bi-direction'

                        elif is_within_grid(column - delta_x, row - delta_y) and \
                                grid[column - delta_x][row - delta_y]['token_color']\
                                    != token_color and \
                                        grid[column - delta_x][row - delta_y]['token_color']\
                                            != EMPTY:
                            capture_move_table[(column, row)][(column + delta_x, row + delta_y)]\
                                    = 'withdraw'
                            has_capture = True

    if has_capture:
        result_table = clean_table(capture_move_table)
        print 'get from movable token information\ncapture table  ', result_table, '\n'
        return result_table

    else:
        result_table = clean_table(paika_move_table)
        print 'get from movable token information\npaika table  ', result_table, '\n'
        return result_table


def clean_table(move_table):
    """return a cleaned move table that only consists of valid move.
    """
    new_table = {k: v for k, v in move_table.iteritems() if v != {} }
    return new_table


def make_move(token_color, grid, (click_x, click_y), (move_x, move_y), prompt_bi_direct=False):
    if token_color == human_token:
        movable_token_table = get_movable_token_information(token_color, grid)
    else:
        movable_token_table = get_movable_token_information(token_color, grid, False)



    grid[click_x][click_y]['token_color'] = EMPTY
    grid[move_x][move_y]['token_color'] = token_color

    if prompt_bi_direct and movable_token_table[(click_x, click_y)][(move_x, move_y)] == 'bi-direction':
        text_surf = BIG_FONT.render('Do you choose to approach or withdraw~?', True, BLACK)
        text_rect = text_surf.get_rect()
        text_rect.center = (int(WINDOW_WIDTH*0.5), int(WINDOW_HEIGHT*0.875))

        approach_surf = BIG_FONT.render('Approach', True, BLACK)
        approach_rect = approach_surf.get_rect()
        approach_rect.center = (int(WINDOW_WIDTH*0.375), int(WINDOW_HEIGHT*0.9375))

        withdraw_surf = BIG_FONT.render('Withdraw', True, BLACK)
        withdraw_rect = withdraw_surf.get_rect()
        withdraw_rect.center = (int(WINDOW_WIDTH*0.625), int(WINDOW_HEIGHT*0.9375))

        is_chosen = False
        while not is_chosen:  # prompt the Human player to choose between approach or withdraw capture
            main_clock.tick(FPS)
            for event in pygame.event.get():
                main_clock.tick(FPS)
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if approach_rect.collidepoint((mouse_x, mouse_y)):
                        movable_token_table[(click_x, click_y)][(move_x, move_y)] = 'approach'
                        is_chosen = True
                        break
                    elif withdraw_rect.collidepoint((mouse_x, mouse_y)):
                        movable_token_table[(click_x, click_y)][(move_x, move_y)] = 'withdraw'
                        is_chosen = True
                        break

            WINDOW_SURF.blit(text_surf, text_rect)
            WINDOW_SURF.blit(approach_surf, approach_rect)
            WINDOW_SURF.blit(withdraw_surf, withdraw_rect)
            main_clock.tick(FPS)
            pygame.display.update()
            main_clock.tick(FPS)

    delta_x, delta_y = (move_x - click_x, move_y - click_y)

    # there exist other opponent's token consecutively along on the same direction,
    # they also will be capture, in a 5X5 grid, maximally THREE in a roll.

    if movable_token_table[(click_x, click_y)][(move_x, move_y)] == 'approach':  # approach capture
        grid[click_x + 2*delta_x][click_y + 2*delta_y]['token_color'] = EMPTY

        # if is_within_grid(click_x + 3*delta_x, click_y + 3*delta_y) and \
        #     grid[click_x + 3*delta_x][click_y + 3*delta_y]['token_color'] != token_color and \
        #         grid[click_x + 3*delta_x][click_y + 3*delta_y]['token_color']!= EMPTY:
        #     grid[click_x + 3*delta_x][click_y + 3*delta_y]['token_color'] = EMPTY
        #
        #     if is_within_grid(click_x + 4*delta_x, click_y + 4*delta_y) and \
        #         grid[click_x + 4*delta_x][click_y + 4*delta_y]['token_color'] != token_color and \
        #             grid[click_x + 4*delta_x][click_y + 4*delta_y]['token_color']!= EMPTY:
        #         grid[click_x + 4*delta_x][click_y + 4*delta_y]['token_color'] = EMPTY

    if movable_token_table[(click_x, click_y)][(move_x, move_y)] == 'withdraw':  # withdraw capture
        grid[click_x - delta_x][click_y - delta_y]['token_color'] = EMPTY

        # if is_within_grid(click_x - 2*delta_x, click_y - 2*delta_y) and \
        #     grid[click_x - 2*delta_x][click_y - 2*delta_y]['token_color'] != token_color and \
        #         grid[click_x - 2*delta_x][click_y - 2*delta_y]['token_color']!= EMPTY:
        #     grid[click_x - 2*delta_x][click_y - 2*delta_y]['token_color'] = EMPTY
        #
        #     if is_within_grid(click_x - 3*delta_x, click_y - 3*delta_y) and \
        #         grid[click_x - 3*delta_x][click_y - 3*delta_y]['token_color'] != token_color and \
        #             grid[click_x - 3*delta_x][click_y - 3*delta_y]['token_color']!= EMPTY:
        #         grid[click_x - 3*delta_x][click_y - 3*delta_y]['token_color'] = EMPTY

    print "Make move from ", (click_x, click_y), ' to ',  (move_x, move_y)
    print '\n', '\n','\n'
    return grid


def is_within_grid(x, y):
    return x >= 0 and x < GRID_WIDTH and y >= 0 and y < GRID_HEIGHT



def enter_player_token():
    """Draws the text and handles the mouse click events for letting
    the player choose which color they want to be.
    Returns [WHITE_TOKEN, BLACK_TOKEN] if the player chooses to be White,
    [BLACK_TOKEN, WHITE_TOKEN] if Black.
    """

    text_surf = BIG_FONT.render('White always goes first. Do you want to be white or black?', True, BLACK)
    text_rect = text_surf.get_rect()
    text_rect.center = (int(WINDOW_WIDTH*0.5), int(WINDOW_HEIGHT*0.875))

    white_surf = BIG_FONT.render('White', True, BLACK)
    white_rect = white_surf.get_rect()
    white_rect.center = (int(WINDOW_WIDTH*0.375), int(WINDOW_HEIGHT*0.9375))

    black_surf = BIG_FONT.render('Black', True, BLACK)
    black_rect = black_surf.get_rect()
    black_rect.center = (int(WINDOW_WIDTH*0.625), int(WINDOW_HEIGHT*0.9375))

    while True:  # keep looping until the player has clicked on a color
        main_clock.tick(FPS)  # CPU is too fast that slowing down is needed
        for event in pygame.event.get(): # event handling loop
            main_clock.tick(FPS)
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # print 'click'
                mouse_x, mouse_y = event.pos
                if white_rect.collidepoint((mouse_x, mouse_y)):
                    # print 'white'
                    return [WHITE, BLACK]
                elif black_rect.collidepoint((mouse_x, mouse_y)):
                    # print 'black'
                    return [BLACK, WHITE]

        WINDOW_SURF.blit(text_surf, text_rect)
        WINDOW_SURF.blit(white_surf, white_rect)
        WINDOW_SURF.blit(black_surf, black_rect)
        main_clock.tick(FPS)
        pygame.display.update()
        main_clock.tick(FPS)


def show_game_results(winner_str, loser_str, draw=False):
    global total_node_generated
    global depth_of_game_tree
    print "\n\nfinally,  level is, nodes are ", depth_of_game_tree, '\n\n', total_node_generated
    if draw:
        text_surf = BIG_FONT.render('The game is draw', True, BLACK)
        text_rect = text_surf.get_rect()
        text_rect.center = (int(WINDOW_WIDTH*0.5), int(WINDOW_HEIGHT*0.875))

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            WINDOW_SURF.blit(text_surf, text_rect)
            main_clock.tick(FPS)
            pygame.display.update()

    else:
        text_surf = BIG_FONT.render('The game is over', True, BLACK)
        text_rect = text_surf.get_rect()
        text_rect.center = (int(WINDOW_WIDTH*0.5), int(WINDOW_HEIGHT*0.875))

        winner_surf = BIG_FONT.render(winner_str + '  Win~!', True, BLACK)
        winner_rect = winner_surf.get_rect()
        winner_rect.center = (int(WINDOW_WIDTH*0.25), int(WINDOW_HEIGHT*0.9375))
    
        loser_surf = BIG_FONT.render(loser_str + '  Lose~~', True, BLACK)
        loser_rect = loser_surf.get_rect()
        loser_rect.center = (int(WINDOW_WIDTH*0.75), int(WINDOW_HEIGHT*0.9375))

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            WINDOW_SURF.blit(text_surf, text_rect)
            WINDOW_SURF.blit(winner_surf, winner_rect)
            WINDOW_SURF.blit(loser_surf, loser_rect)
            show_statistics()
            main_clock.tick(FPS)
            pygame.display.update()


if __name__ == '__main__':
    main()
