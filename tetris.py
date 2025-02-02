import pygame
import numpy as np

from copy import deepcopy
from random import choice


HEIGHT = 20
WIDTH = 10
GRID_SIZE = 45
GAME_RES = WIDTH * GRID_SIZE, HEIGHT * GRID_SIZE
RES = 750, 940

# Tetris Shape
SHAPES = [[(-1, -1), (-2, -1), (0, -1), (1, -1)],             # Horizontal Line
            [(0, -1), (0, 0), (0, 1), (0, 2)],                # Vertical Line
            [(0, -1), (-1, -1), (-1, 0), (0, 0)],             # Square
            [(-2, 0), (-2, -1), (-1, -1), (0, -1)],           # |--
            [(-2, -1), (-1, -1), (0, -1), (-1, 0)],           # T
            [(-2, -1), (-1, -1), (0, -1), (0, 0)],            # ---|
            [(0, -1), (-1, -1), (-1, 0), (-2, 0)],            # S
            [(-2, -1), (-1, -1), (-1, 0), (0, 0)]]            # Z


# COLORS
monokai_foreground_colors = [
    (248, 248, 242),  # Foreground (Text)
    (102, 217, 239),  # Cyan
    (166, 226, 46),   # Green
    (253, 151, 31),   # Orange
    (249, 38, 114),   # Pink/Red
    (174, 129, 255),  # Purple
    (230, 219, 116)   # Yellow
]



class Tetris:
    
    @staticmethod
    def get_color():
        return choice(monokai_foreground_colors)


    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(GAME_RES)
        pygame.display.set_caption("Tetris")

        self.figure_rect = pygame.Rect(0, 0, GRID_SIZE - 2, GRID_SIZE - 2)
        self.field = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

        self.grid = [pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE) 
                 for x in range(WIDTH) for y in range(HEIGHT)]
        
        self.grid = [pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE) for x in range(WIDTH) for y in range(HEIGHT)]
        self.game_over = False
        
        self.piece_x, self.piece_y = 3, 0
        self.anim_count, self.anim_speed, self.anim_limit = 0, 10, 2000
        self.running = True
        self.dx, self.is_rotating = 0, False

        self.figures = [[pygame.Rect(x + WIDTH // 2, y + 1, 1, 1) for x, y in SHAPE] for SHAPE in SHAPES]
        self.figure, self.next_figure = deepcopy(choice(self.figures)), deepcopy(choice(self.figures))
        self.figure_old = deepcopy(self.figure)
        self.color, self.next_color = self.get_color(), self.get_color()

        self.clock = pygame.time.Clock()

        # Scores
        self.score, self.lines = 0, 0
        self.scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

    def get_grid(self):
        """Return the current grid as a NumPy array, encoding occupied spaces and active piece."""
        grid = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
        
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.field[y][x]:
                    grid[y][x] = 1.0  # Mark occupied cells
        
        # Encode the current falling piece
        for block in self.figure:
            if 0 <= block.y < HEIGHT:  
                grid[block.y][block.x] = 0.5  # Encode falling piece distinctly
                
        return grid

    def generate_new_piece(self):
        """Generate a new Tetris piece and check if it results in game over."""
        self.figure = self.next_figure  # Set the next piece as the current piece
        self.color = self.next_color  # Assign its color
        self.next_figure = deepcopy(choice(self.figures))  # Choose a new upcoming piece
        self.next_color = self.get_color()  # Assign new color
        self.piece_x, self.piece_y = 3, 0  # Reset piece position to the top

        self.anim_count = 0  # Reset animation counter
        self.anim_limit = 2000  # Reset the normal drop speed

        # 🔹 Check for Game Over: If the new piece is blocked at the top, the game ends
        if any(self.field[self.figure[i].y][self.figure[i].x] for i in range(4) if self.figure[i].y >= 0):
            print("Game Over!")  # Debug message
            self.running = False  # Stop the game


    def draw(self):
        """Render the Tetris grid using pygame."""
        self.screen.fill('black')

        # Draw grid lines
        for rect in self.grid:
            pygame.draw.rect(self.screen, (40, 40, 40), rect, 1)

        # Draw existing blocks
        for y, row in enumerate(self.field):
            for x, cell in enumerate(row):
                if cell:
                    self.figure_rect.x, self.figure_rect.y = x * GRID_SIZE, y * GRID_SIZE
                    pygame.draw.rect(self.screen, cell, self.figure_rect)

        # Draw active falling piece
        for i in range(4):
            self.figure_rect.x = self.figure[i].x * GRID_SIZE
            self.figure_rect.y = self.figure[i].y * GRID_SIZE
            pygame.draw.rect(self.screen, self.color, self.figure_rect)

        # Update display
        # self.sc.blit(self.screen, (0, 0))
        pygame.display.flip()  # Ensure changes are visible


    def reset(self):
        """Reset the Tetris game state."""
        self.field = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]  # Clear the grid
        self.figure = deepcopy(choice(self.figures))  # Get a new random piece
        self.next_figure = deepcopy(choice(self.figures))
        self.color, self.next_color = self.get_color(), self.get_color()
        self.piece_x, self.piece_y = 3, 0  # Reset piece position
        self.running = True
        self.score = 0
        self.anim_speed = 10
        self.anim_limit = 2000


    def is_within_boundary(self, i):
        """Check if the piece is within boundaries and does not overlap."""
        if self.figure[i].x < 0 or self.figure[i].x >= WIDTH:  # Horizontal boundary
            return False
        if self.figure[i].y >= HEIGHT:  # Vertical boundary
            return False
        if self.figure[i].y >= 0 and self.field[self.figure[i].y][self.figure[i].x]:  # Overlap with existing tiles
            return False
        return True
    
    def display_figure(self):
        # Draw the grid with landed pieces
        for y, row in enumerate(self.field):
            for x, col in enumerate(row):
                if col:
                    self.figure_rect.x, self.figure_rect.y = x * GRID_SIZE, y * GRID_SIZE
                    pygame.draw.rect(self.screen, col, self.figure_rect)

        # Draw the active falling piece
        for i in range(4):
            self.figure_rect.x = self.figure[i].x * GRID_SIZE
            self.figure_rect.y = self.figure[i].y * GRID_SIZE
            pygame.draw.rect(self.screen, self.color, self.figure_rect)


    
            
    
    def move_horizontally(self):
        # Moving the figure Horizontally
        for i in range(4):
            self.figure[i].x += self.dx
            if not self.is_within_boundary(i):
                self.figure = deepcopy(self.figure_old)
                break

    def move_vertically(self):
        """Moves the current piece down. Ends the game if a piece is blocked at the top."""
        self.anim_count += self.anim_speed

        if self.anim_count > self.anim_limit:
            self.anim_count = 0
            self.figure_old = deepcopy(self.figure)

            for i in range(4):
                self.figure[i].y += 1  # Move down

                if not self.is_within_boundary(i):
                    # 🔹 Place piece on board
                    for j in range(4):
                        self.field[self.figure_old[j].y][self.figure_old[j].x] = self.color
                    
                    # 🔹 Generate new piece
                    # self.figure, self.color = self.next_figure, self.next_color
                    # self.next_figure, self.next_color = deepcopy(choice(self.figures)), self.get_color()
                    # self.anim_limit = 2000  # Reset drop speed
                    self.generate_new_piece()

                    # 🔹 Check for **Game Over Condition**
                    if any(self.field[0][x] for x in range(WIDTH)):  # If top row has a block
                        self.running = False  # **Game Over**
                        print("Game Over!")  # Debug message
                        return

                    return  # Exit function after placing a block
            
            # If movement is valid, continue to the next frame
            self.figure_old = deepcopy(self.figure)

 
    def rotate_figure(self):
        self.is_rotating = True

        if not self.is_rotating:
            return  # No rotation requested

        # Check if the figure is a square (2x2 block)
        if self.is_square():
            self.is_rotating = False  # Reset the rotation flag
            return  # Do not rotate squares

        print("Rotating Figure")
        center = self.figure[0]  # Pivot block
        figure_old = deepcopy(self.figure)  # Save original state before rotating

        # Perform rotation (standard Tetris rotation logic)
        for i in range(4):
            x = self.figure[i].y - center.y
            y = self.figure[i].x - center.x
            self.figure[i].x = center.x - x
            self.figure[i].y = center.y + y

        # Check if the new rotation is valid
        if all(self.is_within_boundary(i) for i in range(4)):
            self.is_rotating = False  # Reset the rotation flag after successful rotation
            return  # Rotation is valid, exit

        # If invalid, attempt wall kick by shifting in multiple directions
        shift_offsets = [(-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1), (0, 1)]

        for dx, dy in shift_offsets:
            for block in self.figure:
                block.x += dx
                block.y += dy

            if all(self.is_within_boundary(i) for i in range(4)):
                self.is_rotating = False  # Reset flag after successful shift
                return  # Successfully adjusted position, exit

            # Undo shift if not valid
            for block in self.figure:
                block.x -= dx
                block.y -= dy

        # If no valid position is found, revert to old state
        self.figure = deepcopy(figure_old)
        self.is_rotating = False  # Reset flag to avoid continuous rotation attempts

    def is_square(self):
        """Check if the current piece is a 2x2 square."""
        return all(
            (block.x - self.figure[0].x, block.y - self.figure[0].y) in [(-1, -1), (0, -1), (-1, 0), (0, 0)]
            for block in self.figure
        )

    def check_lines(self):
        """Check and remove complete lines, then return the number of lines cleared."""
        lines_cleared = 0
        self.line = HEIGHT - 1

        for row in range(HEIGHT - 1, -1, -1):
            self.count = 0
            for i in range(WIDTH):
                if self.field[row][i]:
                    self.count += 1
                self.field[self.line][i] = self.field[row][i]
            
            if self.count < WIDTH:
                self.line -= 1  # Move the line down
            else:
                self.anim_speed += 3
                lines_cleared += 1  # Count cleared lines

        # Compute Score
        self.score += self.scores[lines_cleared]

        return lines_cleared  # 🔹 Now it returns the number of lines cleared


    def move_left(self):
        print("Move Left Figure")
        self.dx = -1
        self.move_horizontally()

    def move_right(self):
        print("Move Right Figure")
        self.dx = 1
        self.move_horizontally()

    def drop(self):
        """Make the piece drop immediately to the lowest available position."""
        print("Dropping Figure")
        while all(self.is_within_boundary(i) for i in range(4)):
            for i in range(4):
                self.figure[i].y += 1  # Move down

        # One extra move went out of bounds, so move back up
        for i in range(4):
            self.figure[i].y -= 1

        self.anim_limit = 100  # Speed up the animation so the next piece appears faster

    def check_collision(self, dx=0, dy=0, figure=None):
        """Check if a piece collides with the grid or boundaries after a move."""
        if figure is None:
            figure = self.figure

        for block in figure:
            x, y = block.x + dx, block.y + dy
            if x < 0 or x >= WIDTH or y >= HEIGHT or (y >= 0 and self.field[y][x]):
                return True
        return False

    def game_over(self):
        """Display Game Over screen and quit gracefully."""
        game_over_text = self.main_font.render("GAME OVER", True, pygame.Color('red'))
        self.sc.blit(game_over_text, (150, 400))  # Centered on screen
        pygame.display.flip()
        pygame.time.delay(3000)  # Wait 3 seconds
        self.running = False
        pygame.quit()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Press Esc to quit
                        self.running = False
                    elif event.key == pygame.K_LEFT:
                        self.move_left()
                        
                    elif event.key == pygame.K_RIGHT:
                        self.move_right()

                    elif event.key == pygame.K_DOWN:
                        self.drop()

                    elif event.key == pygame.K_UP:
                        self.rotate_figure()
                        
            self.move_vertically()
            self.check_lines()
            self.draw()