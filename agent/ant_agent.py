import os
os.path.insert(0, )
from env.gym_ant.ant_env_v4 import AntEnv


env = AntEnv(render_mode="human")
print("The observation space is %i" %(env.observation_space.shape))
print("The action space is %i" %(env.action_space.shape))

observation, info = env.reset()

for _ in range(1000):
    action = env.action_space.sample()
    print(action)  # agent policy that uses the observation and info
    observation, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        observation, info = env.reset()

env.close()