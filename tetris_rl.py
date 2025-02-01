from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv

from sb3_contrib import RecurrentPPO  # ✅ Use SBX for LSTM support
from stable_baselines3 import DQN


from tetris_env import TetrisEnv

env = DummyVecEnv([lambda: TetrisEnv()])

print("Training Observation Space: ", env.observation_space.shape)

checkpoint_callback = CheckpointCallback(
    save_freq=10_000,  # Every 10,000 frames
    save_path="./checkpoints/",  # Directory to save models
    name_prefix="ppo_tetris"
)

eval_env = DummyVecEnv([lambda: TetrisEnv()])

eval_callback = EvalCallback(
    eval_env,
    best_model_save_path="./best_model/",
    log_path="./logs/",
    eval_freq=10_000,  # Evaluate every 10,000 steps
    deterministic=True,
    render=False
)

model = RecurrentPPO(
        "MlpLstmPolicy",
        env,
        verbose=1,
        n_steps=2048,
        batch_size=64,
        learning_rate=2.5e-4,
        gamma=0.99,
        gae_lambda=0.95,
        use_sde=False,
        vf_coef=0.4,
        ent_coef=0.005,
        policy_kwargs=dict(lstm_hidden_size=256),
    )


# Train for 1 million timesteps
model.learn(total_timesteps=1_000_000, callback=checkpoint_callback)


model.save("./best_model/ppo_tetris_final")
print("✅ Training complete. Best model saved as 'ppo_tetris_final'.")