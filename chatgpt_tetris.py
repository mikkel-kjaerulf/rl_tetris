import pygame
import random

# Initialize Pygame
pygame.init()

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)

# Set the width and height of the game window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Set the size of each grid square
GRID_SIZE = 25

# Set the number of rows and columns on the game grid
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Set the initial position of the falling piece
INITIAL_POSITION = (GRID_WIDTH // 2, 0)

# Define the shapes of the Tetris pieces
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

# Define the colors of the Tetris pieces
COLORS = [CYAN, YELLOW, GREEN, RED, BLUE, ORANGE, PURPLE]

# Create the game window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tetris")

clock = pygame.time.Clock()

def draw_grid():
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(window, WHITE, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
        pygame.draw.line(window, WHITE, (0, y), (WINDOW_WIDTH, y))

def draw_piece(piece, position):
    shape = SHAPES[piece]
    color = COLORS[piece]
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x] == 1:
                pygame.draw.rect(window, color, (position[0] * GRID_SIZE + x * GRID_SIZE, position[1] * GRID_SIZE + y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def is_collision(piece, position, grid):
    shape = SHAPES[piece]
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x] == 1:
                if position[0] + x < 0 or position[0] + x >= GRID_WIDTH or position[1] + y >= GRID_HEIGHT or grid[position[1] + y][position[0] + x] != -1:
                    return True
    return False

def clear_rows(grid):
    full_rows = []
    for y in range(GRID_HEIGHT):
        if all(cell != -1 for cell in grid[y]):
            full_rows.append(y)
    for row in full_rows:
        del grid[row]
        grid.insert(0, [-1] * GRID_WIDTH)
    return len(full_rows)

def draw_game_over():
    font = pygame.font.Font(None, 48)
    text = font.render("Game Over", True, WHITE)
    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    window.blit(text, text_rect)

def tetris():
    grid = [[-1] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    piece = random.randint(0, len(SHAPES) - 1)
    position = list(INITIAL_POSITION)
    score = 0
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    position[0] -= 1
                    if is_collision(piece, position, grid):
                        position[0] += 1
                elif event.key == pygame.K_RIGHT:
                    position[0] += 1
                    if is_collision(piece, position, grid):
                        position[0] -= 1
                elif event.key == pygame.K_DOWN:
                    position[1] += 1
                    if is_collision(piece, position, grid):
                        position[1] -= 1
                elif event.key == pygame.K_UP:
                    rotated_piece = SHAPES[piece][::-1]
                    if not is_collision(piece, position, grid):
                        SHAPES[piece] = rotated_piece

        if not is_collision(piece, (position[0], position[1] + 1), grid):
            position[1] += 1
        else:
            shape = SHAPES[piece]
            for y in range(len(shape)):
                for x in range(len(shape[y])):
                    if shape[y][x] == 1:
                        grid[position[1] + y][position[0] + x] = piece
            piece = random.randint(0, len(SHAPES) - 1)
            position = list(INITIAL_POSITION)
            if is_collision(piece, position, grid):
                game_over = True

            score += clear_rows(grid)

        window.fill(BLACK)
        draw_grid()
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if grid[y][x] != -1:
                    pygame.draw.rect(window, COLORS[grid[y][x]], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        draw_piece(piece, position)

        if game_over:
            draw_game_over()

        pygame.display.update()
        clock.tick(5)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

if __name__ == '__main__':
    tetris()
