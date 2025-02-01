from stable_baselines3 import PPO
import gymnasium as gym

# Create the environment
env = gym.make("CartPole-v1", render_mode="human")

# Initialize PPO model with a neural network policy
model = PPO("MlpPolicy", env, verbose=1)

# Train the model
model.learn(total_timesteps=10000)

# Save the trained model
model.save("ppo_cartpole")
env.close()
