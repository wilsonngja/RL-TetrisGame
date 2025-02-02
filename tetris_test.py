import pygame
from stable_baselines3 import PPO
from tetris_env import TetrisEnv

# Load trained model
model = PPO.load("checkpoints/ppo_tetris_300000_steps.zip")  # Ensure the model file exists

# Create the Tetris environment
env = TetrisEnv()
print("Observation space in TEST:", env.observation_space.shape)  # Should print (20, 10)

episodes = 10  # Number of games to play automatically

for episode in range(episodes):
    state = env.reset()
    done = False

    while not done:
        pygame.event.pump()  # Allow Pygame to process window events

        # 🔹 Use the trained model to predict the action
        action, _ = model.predict(state)  # Predict the next move based on the current state

        # Execute the action in the environment
        state, reward, done, _ = env.step(action)

        # Render the game to visualize the AI's gameplay
        env.render()

        # Delay to control speed of visualization (adjustable)
        pygame.time.delay(100)

    print(f"Game Over! Episode {episode+1} finished with final reward: {reward}")

# Close the environment after all episodes
env.close()
