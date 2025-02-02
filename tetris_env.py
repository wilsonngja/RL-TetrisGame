import gym
from gym import spaces
import numpy as np
import pygame
from tetris import HEIGHT, WIDTH, Tetris
from copy import deepcopy  # 🔹 Add this import
from random import choice  # 🔹 Ensure choice() is also imported



class TetrisEnv(gym.Env):
    def __init__(self):
        super(TetrisEnv, self).__init__()

        self.board = np.zeros((20, 10), dtype=np.int8)
        # Initialise the game
        self.game = Tetris()

        # Define the action space (Left, Right, Rotate and Drop)
        self.action_space = spaces.Discrete(4)

        # Observation Space
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(202, ), dtype=np.float32)


    
    def step(self, action):
        reward = 0
        done = False

        # Execute action
        if action == 0:
            self.game.move_left()
        elif action == 1:
            self.game.move_right()
        elif action == 2:
            self.game.rotate_figure()
        elif action == 3:
            self.game.drop()

        # Simulate gravity
        self.game.move_vertically()
        lines_cleared = self.game.check_lines()

        # Reward for clearing lines
        reward += lines_cleared * 10  

        reward -= 0.1  

        # Encourage keeping the board low
        max_height = max((y for x in range(WIDTH) for y in range(HEIGHT) if self.game.field[y][x]), default=0)
        reward -= max_height * 0.35  

        # Check game over
        if not self.game.running:
            done = True
            reward -= 50  

        # ✅ Fix observation shape (20, 10) → (20, 40)
        # grid = self.game.get_grid()
        observation = self.game.get_grid()

        # print("Observation shape in step:", observation.shape)  # Debugging

        return self.get_observation(), reward, done, {}
    
    # def reset(self):
    #     """Reset the environment and return the initial observation."""
    #     self.board = np.zeros((20, 10), dtype=np.int8)

    #     self.game.reset()  # Reset the game state

    #     # ✅ Return the grid as (20,10) without padding
    #     observation = self.game.get_grid()
    #     print("Observation shape in reset:", observation.shape)  # Debugging
    #     return observation  # Ensure correct shape (20,10)

    def reset(self):
        """Reset the environment and return the initial observation."""
        self.board = np.zeros((20, 10), dtype=np.int8)  # 🔹 Reset board state
        self.game.reset()  # 🔹 Reset the game state
        self.game.generate_new_piece()  # 🔹 Ensure the first piece is assigned
        return self.get_observation()



    def render(self, mode="human"):
        """Render the game using Pygame."""
        self.game.draw()

    def close(self):
        pygame.quit()
    
    def get_observation(self):
        """Get the current board state and active piece position as an observation."""
        board_state = self.game.get_grid().flatten()  # 🔹 Convert grid into a 1D array

        # Extract the active piece's position (first block of the piece)
        if self.game.figure:
            piece_info = np.array([self.game.figure[0].x, self.game.figure[0].y], dtype=np.float32)
        else:
            piece_info = np.array([0, 0], dtype=np.float32)  # Default if no piece exists

        return np.concatenate((board_state, piece_info))  # 🔹 Combine board + piece position

