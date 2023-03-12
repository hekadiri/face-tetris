import random
import pygame
import cv2

pygame.font.init()

col = 10
row = 20
s_width = 800
s_height = 750
play_width = 300
play_height = 600
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

filepath = './highscore.txt'
fontpath = './tsuki.ttf'
fontpath_mario = './tsuki.ttf'

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['.....',
      '..0..',
      '..0..',
      '..0..',
      '..0..'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# index represents the shape
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]

class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]  # choose color from the shape_color list
        self.rotation = 0  # chooses the rotation according to index

def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for x in range(col)] for y in range(row)]  # grid represented rgb tuples
    for y in range(row):
        for x in range(col):
            if (x, y) in locked_pos:
                color = locked_pos[
                    (x, y)]
                grid[y][x] = color
    return grid

def convert_shape_format(piece):
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j, piece.y + i))
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)
    return positions

def valid_space(piece, grid):
    accepted_pos = [[(x, y) for x in range(col) if grid[y][x] == (0, 0, 0)] for y in range(row)]
    accepted_pos = [x for item in accepted_pos for x in item]
    formatted_shape = convert_shape_format(piece)
    for pos in formatted_shape:
        if pos not in accepted_pos:
            if pos[1] >= 0:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Piece(5, 0, random.choice(shapes))

def draw_text_middle(text, size, color, surface):
    font = pygame.font.Font(fontpath, size)
    label = font.render(text, 1, color)
    surface.blit(label, (top_left_x + play_width/2 - (label.get_width()/2), top_left_y + play_height/2 - (label.get_height()/2)))

def draw_grid(surface):
    r = g = b = 0
    grid_color = (r, g, b)
    for i in range(row):
        pygame.draw.line(surface, grid_color, (top_left_x, top_left_y + i * block_size),
                         (top_left_x + play_width, top_left_y + i * block_size))
        for j in range(col):
            pygame.draw.line(surface, grid_color, (top_left_x + j * block_size, top_left_y),
                             (top_left_x + j * block_size, top_left_y + play_height))

def clear_rows(grid, locked):
    increment = 0
    for i in range(len(grid) - 1, -1, -1):
        grid_row = grid[i]
        if (0, 0, 0) not in grid_row:
            increment += 1
            index = i
            for j in range(len(grid_row)):
                try:
                    del locked[(j, i)]
                except ValueError:
                    continue
    if increment > 0:
        for key in sorted(list(locked), key=lambda a: a[1])[::-1]:
            x, y = key
            if y < index:
                new_key = (x, y + increment)
                locked[new_key] = locked.pop(key)
    return increment

def draw_next_shape(piece, surface):
    font = pygame.font.Font(fontpath, 30)
    label = font.render('Next shape', 1, (255, 255, 255))
    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100)
    shape_format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color, (start_x + j*block_size, start_y + i*block_size, block_size, block_size), 0)
    surface.blit(label, (start_x, start_y - 30))

def draw_window(surface, grid, score=0, last_score=0):
    surface.fill((0, 0, 0))
    pygame.font.init()
    font = pygame.font.Font(fontpath_mario, 65)
    label = font.render('TETRIS', 1, (255, 255, 255))
    surface.blit(label, ((top_left_x + play_width / 2) - (label.get_width() / 2), 30))

    font = pygame.font.Font(fontpath, 30)
    label = font.render('SCORE   ' + str(score) , 1, (255, 255, 255))
    start_x = top_left_x + play_width + 50
    start_y = top_left_y + (play_height / 2 - 100)
    surface.blit(label, (start_x, start_y + 200))

    label_hi = font.render('HIGHSCORE   ' + str(last_score), 1, (255, 255, 255))

    start_x_hi = top_left_x - 240
    start_y_hi = top_left_y + 200

    surface.blit(label_hi, (start_x_hi + 20, start_y_hi + 200))

    for i in range(row):
        for j in range(col):
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    draw_grid(surface)
    border_color = (255, 255, 255)
    pygame.draw.rect(surface, border_color, (top_left_x, top_left_y, play_width, play_height), 4)

def update_score(new_score):
    score = get_max_score()
    with open(filepath, 'w') as file:
        if new_score > score:
            file.write(str(new_score))
        else:
            file.write(str(score))

def get_max_score():
    with open(filepath, 'r') as file:
        lines = file.readlines()
        score = int(lines[0].strip())
    return score

def main(window):
    locked_positions = {}
    create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 1
    level_time = 0
    score = 0
    last_score = get_max_score()

    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    delay = 1
    frame_count=0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()

        clock.tick()

        if level_time/1000 > 5:
            level_time = 0
            if fall_speed > 0.15:
                fall_speed -= 0.005

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        ret, frame = cap.read()
        if frame is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Draw box around middle of the video feed
            box_thickness = 4
            box_color = (0, 0, 255) # Blue color
            frame_height, frame_width, _ = frame.shape
            box_height = frame_height // 2 -450# Bit taller than half the frame height
            box_width = box_height +25 # Square box
            box_y = (frame_height - box_height) // 2
            box_x = (frame_width - box_width) // 2

            # Draw the box bounds of the middle of the video feed
            cv2.rectangle(frame, (box_x, box_y), (box_x+box_width-1, box_y+box_height-1), box_color, box_thickness)

            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            # Find the largest face
            max_area = 0
            max_face = None
            for (x, y, w, h) in faces:
                if w*h > max_area:
                    max_area = w*h
                    max_face = (x, y, w, h)

            # Track only the largest face
            if max_face is not None:
                x, y, w, h = max_face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) # Draws the rectangle around the face

                face_center_x = x + w // 2
                face_center_y = y + h // 2

                if frame_count >= delay:
                    if face_center_y < box_y:
                        frame_count=0
                        current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                        if not valid_space(current_piece, grid):
                            current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)
                        print('Move up')

                    elif face_center_y > box_y + box_height:
                        frame_count=0
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1
                        print('Move down')

                    elif face_center_x < box_x:
                        frame_count=0
                        current_piece.x += 1  # move x position right
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1
                        print('Move right')

                    elif face_center_x > box_x + box_width:
                        frame_count=0
                        current_piece.x -= 1  # move x position left
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1
                        print('Move left')
                else:
                    frame_count += 1

                # Flip the frame horizontally
                flipped_frame = cv2.flip(frame, 1)
                cv2.imshow('frame', flipped_frame)

                if cv2.waitKey(1) == ord('q'):
                    break

        piece_pos = convert_shape_format(current_piece)

        for i in range(len(piece_pos)):
            x, y = piece_pos[i]
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in piece_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10
            update_score(score)

            if last_score < score:
                last_score = score

        draw_window(window, grid, score, last_score)
        draw_next_shape(next_piece, window)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    draw_text_middle('You Lost', 40, (255, 255, 255), window)
    pygame.display.update()
    pygame.time.delay(2000)
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
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')

    main_menu(win)