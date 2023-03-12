import random
import pygame
import vars

"""
    This is the main file for the Tetris game. It contains the main game loop and
    the main function.

    The board size will be 10x24 squares. The top 4 rows are hidden in order to allow
    for pieces to spawn without immediately colliding with the ground.
"""

class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = vars.shapes_to_color[shape]
        self.rotation = 0

def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for x in range(vars.num_cols)] for x in range(vars.num_rows)]
    for y in range(vars.num_rows):
        for x in range(vars.num_cols):
            if (x, y) in locked_pos:
                color = locked_pos[
                    (x, y)]
                grid[y][x] = color
    return grid

def convert_shape_format(piece):
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]
    for i in range(len(shape_format)):
        for j in range(len(shape_format[i])):
            if shape_format[i][j] == '0':
                x = piece.x + j
                y = piece.y + i
                positions.append((x, y))
    positions = [(x - 2, y - 4) for (x, y) in positions]
    return positions

def valid_space(piece, grid):
    formatted_shape = convert_shape_format(piece)
    for pos in formatted_shape:
        x, y = pos
        if not (0 <= x < len(grid[0]) and 0 <= y < len(grid)):
            return False
        if grid[y][x] != (0, 0, 0):
            return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def draw_text_middle(text, size, color, surface):
    pygame.font.init()
    font = pygame.font.Font(vars.fontpath, size)
    label = font.render(text, 1, color)
    surface.blit(label, (vars.board_start_x + vars.play_width/2 - (label.get_width()/2), vars.board_start_y + vars.play_height/2 - (label.get_height()/2)))

def draw_grid(surface):
    r = g = b = 0
    grid_color = (r, g, b)
    for i in range(vars.num_rows):
        pygame.draw.line(surface, grid_color, (vars.board_start_x, vars.board_start_y + i * vars.block_size),
                         (vars.board_start_x + vars.play_width, vars.board_start_y + i * vars.block_size))
        for j in range(vars.num_cols):
            pygame.draw.line(surface, grid_color, (vars.board_start_x + j * vars.block_size, vars.board_start_y),
                             (vars.board_start_x + j * vars.block_size, vars.board_start_y + vars.play_height))

def clear_rows(grid, locked):
    num_cleared = 0
    for row in range(len(grid)):
        if all(cell != (0, 0, 0) for cell in grid[row]):
            # Clear the row by moving all the rows above it down by 1
            for r in range(row, 0, -1):
                grid[r] = grid[r - 1].copy()
                for c in range(len(grid[r])):
                    if (c, r - 1) in locked:
                        locked[(c, r)] = locked[(c, r - 1)]
                        del locked[(c, r - 1)]
            # Set the top row to be empty
            grid[0] = [(0, 0, 0) for _ in range(len(grid[0]))]
            num_cleared += 1
    return num_cleared

def draw_next_shape(piece, surface):
    font = pygame.font.Font(vars.fontpath, 30)
    label = font.render('Next shape', 1, (255, 255, 255))

    start_x = vars.board_start_x + vars.play_width + 50
    start_y = vars.board_start_y + (vars.play_height / 2 - 100)

    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                x = start_x + j * vars.block_size + 10
                y = start_y + i * vars.block_size + 10
                pygame.draw.rect(surface, piece.color, (x, y, vars.block_size, vars.block_size), 0)

    surface.blit(label, (start_x + 10, start_y - 30))


def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))

    # Draw the "TETRIS" label
    font = pygame.font.Font(vars.fontpath, 65)
    label = font.render('TETRIS', True, (255, 255, 255))
    label_rect = label.get_rect(center=(vars.board_start_x + vars.play_width / 2, 50))
    surface.blit(label, label_rect)

    # Draw the score labels
    font = pygame.font.Font(vars.fontpath, 30)
    score_label = font.render('SCORE: ' + str(score), True, (255, 255, 255))
    score_rect = score_label.get_rect(midtop=(vars.board_start_x + vars.play_width + 100, vars.board_start_y + 20))
    surface.blit(score_label, score_rect)

    highscore_label = font.render('HIGH SCORE: ' + str(score), True, (255, 255, 255))
    highscore_rect = highscore_label.get_rect(midtop=(vars.board_start_x - 100, vars.board_start_y + 20))
    surface.blit(highscore_label, highscore_rect)

    # Draw the blocks on the grid
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            block_rect = pygame.Rect(vars.board_start_x + j * vars.block_size, vars.board_start_y + i * vars.block_size, vars.block_size, vars.block_size)
            pygame.draw.rect(surface, cell, block_rect)

    # Draw the grid lines
    draw_grid(surface)

    # Draw the border around the play area
    border_rect = pygame.Rect(vars.board_start_x - 2, vars.board_start_y - 2, vars.play_width + 4, vars.play_height + 4)
    border_color = (255, 255, 255)
    pygame.draw.rect(surface, border_color, border_rect, 4)

def main(window):
    locked_positions = {}
    create_grid(locked_positions)

    change_piece = False
    run = True
    # random piece
    current_piece = Piece(5, 0, random.choice(vars.shape_letters))
    next_piece = Piece(5, 0, random.choice(vars.shape_letters))
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.35
    level_time = 0
    score = 0
    last_score = 0

    while run:
        # need to constantly make new grid as locked positions always change
        grid = create_grid(locked_positions)

        # helps run the same on every computer
        # add time since last tick() to fall_time
        fall_time += clock.get_rawtime()  # returns in milliseconds
        level_time += clock.get_rawtime()

        clock.tick()  # updates clock

        if level_time/1000 > 5:    # make the difficulty harder every 10 seconds
            level_time = 0
            if fall_speed > 0.15:   # until fall speed is 0.15
                fall_speed -= 0.005

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                # since only checking for down - either reached bottom or hit another piece
                # need to lock the piece position
                # need to generate new piece
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1  # move x position left
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1  # move x position right
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1

                elif event.key == pygame.K_DOWN:
                    # move shape down
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

                elif event.key == pygame.K_UP:
                    # rotate shape
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)

        piece_pos = convert_shape_format(current_piece)

        # draw the piece on the grid by giving color in the piece locations
        for i in range(len(piece_pos)):
            x, y = piece_pos[i]
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:  # if the piece is locked
            for pos in piece_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color       # add the key and value in the dictionary
            current_piece = next_piece
            next_piece = Piece(5, 0, random.choice(vars.shape_letters))
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10    # increment score by 10 for every row cleared

            if last_score < score:
                last_score = score

        draw_window(window, grid, score)
        draw_next_shape(next_piece, window)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    draw_text_middle('You Lost', 40, (255, 255, 255), window)
    pygame.display.update()
    pygame.time.delay(2000)  # wait for 2 seconds
    pygame.quit()


def main_menu(window):
    run = True
    while run:
        draw_text_middle('Press any key to begin', 50, (255, 255, 255), window)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                main(window)

    pygame.quit()

if __name__ == '__main__':

    win = pygame.display.set_mode((vars.screen_width, vars.screen_height))
    pygame.display.set_caption('Tetris')

    main_menu(win)  # start game