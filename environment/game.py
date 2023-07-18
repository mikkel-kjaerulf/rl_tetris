import pygame
import puzzle_env 

class TetrisRenderer:
    def __init__(self, board):
        self.board = board
        self.block_size = 30
        self.window_width = self.board.width * self.block_size
        self.window_height = self.board.height * self.block_size

        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Tetris")

        self.colors = {
            0: (0, 0, 0),      # Empty block
            1: (255, 0, 0),    # Locked piece
            2: (0, 255, 0)     # Active piece
        }

    def run(self):
        game_over = False
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.board.move('left')
                    elif event.key == pygame.K_RIGHT:
                        self.board.move('right')
                    elif event.key == pygame.K_DOWN:
                        self.board.move('down')
                    elif event.key == pygame.K_UP:
                        self.board.rotate('right')

            self.board.move('down')

            self.screen.fill((0, 0, 0))

            for i in range(self.board.height):
                for j in range(self.board.width):
                    block_type = self.board.field[i, j]
                    color = self.colors[block_type]
                    pygame.draw.rect(self.screen, color, (j * self.block_size, i * self.block_size, self.block_size, self.block_size))

            pygame.display.flip()
            self.clock.tick(10)

        pygame.quit()


# Create an instance of the Board and TetrisRenderer classes
board = puzzle_env.Board()
renderer = TetrisRenderer(board)

# Run the game
renderer.run()
