# PyMJCF
from dm_control import mjcf
from dm_control import mujoco

import numpy as np

# Graphics-related
import matplotlib
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from IPython.display import HTML
import PIL.Image

class Leg(object):
  """A 2-DoF leg with position actuators."""
  def __init__(self, length, rgba):
    self.model = mjcf.RootElement()

    # Defaults:
    self.model.default.joint.damping = 2
    self.model.default.joint.type = 'hinge'
    self.model.default.geom.type = 'capsule'
    self.model.default.geom.rgba = rgba  # Continued below...

    # Thigh:
    self.thigh = self.model.worldbody.add('body')
    self.hip = self.thigh.add('joint', axis=[0, 0, 1])
    self.thigh.add('geom', fromto=[0, 0, 0, length, 0, 0], size=[length/4])

    # Hip:
    self.shin = self.thigh.add('body', pos=[length, 0, 0])
    self.knee = self.shin.add('joint', axis=[0, 1, 0])
    self.shin.add('geom', fromto=[0, 0, 0, 0, 0, -length], size=[length/5])

    # Position actuators:
    self.model.actuator.add('position', joint=self.hip, kp=10)
    self.model.actuator.add('position', joint=self.knee, kp=10)

BODY_RADIUS = 0.1
BODY_SIZE = (BODY_RADIUS, BODY_RADIUS, BODY_RADIUS / 2)
random_state = np.random.RandomState(42)

def make_creature(num_legs):
  """Constructs a creature with `num_legs` legs."""
  rgba = random_state.uniform([0, 0, 0, 1], [1, 1, 1, 1])
  model = mjcf.RootElement()
  model.compiler.angle = 'radian'  # Use radians.

  # Make the torso geom.
  model.worldbody.add(
      'geom', name='torso', type='ellipsoid', size=BODY_SIZE, rgba=rgba)

  # Attach legs to equidistant sites on the circumference.
  for i in range(num_legs):
    theta = 2 * i * np.pi / num_legs
    hip_pos = BODY_RADIUS * np.array([np.cos(theta), np.sin(theta), 0])
    hip_site = model.worldbody.add('site', pos=hip_pos, euler=[0, 0, theta])
    leg = Leg(length=BODY_RADIUS, rgba=rgba)
    hip_site.attach(leg.model)

  return model

# def display_video(frames, framerate=30):
#   height, width, _ = frames[0].shape
#   dpi = 70
#   orig_backend = matplotlib.get_backend()
#   matplotlib.use('Agg')  # Switch to headless 'Agg' to inhibit figure rendering.
#   fig, ax = plt.subplots(1, 1, figsize=(width / dpi, height / dpi), dpi=dpi)
#   matplotlib.use(orig_backend)  # Switch back to the original backend.
#   ax.set_axis_off()
#   ax.set_aspect('equal')
#   ax.set_position([0, 0, 1, 1])
#   im = ax.imshow(frames[0])
#   def update(frame):
#     im.set_data(frame)
#     return [im]
#   interval = 1000/framerate
#   anim = animation.FuncAnimation(fig=fig, func=update, frames=frames,
#                                  interval=interval, blit=True, repeat=False)
#   anim.save('video.mp4')

def display_video(video_frames, framerate):
  fig = plt.figure()
  ax = fig.add_subplot(111)
  ax.set_aspect('equal')
  def animate(frame):
      ax.clear()
      ax.imshow(video_frames[frame])
      ax.axis('off')
  ani = animation.FuncAnimation(fig, animate, frames=len(video_frames), interval=1000 / framerate)
  plt.show()
if __name__ == '__main__':
    
    arena = mjcf.RootElement()
    chequered = arena.asset.add('texture', type='2d', builtin='checker', width=300,
                                height=300, rgb1=[.2, .3, .4], rgb2=[.3, .4, .5])
    grid = arena.asset.add('material', name='grid', texture=chequered,
                           texrepeat=[5, 5], reflectance=.2)
    arena.worldbody.add('geom', type='plane', size=[2, 2, .1], material=grid)
    for x in [-2, 2]:
      arena.worldbody.add('light', pos=[x, -1, 3], dir=[-x, 1, -2])

    spiderbot = make_creature(num_legs=6)

    # Place spawn sites on a grid.
    spawn_pos = (-0.5, 0.0, 0.15)
    spawn_site = arena.worldbody.add('site', pos=spawn_pos, group=3)
    # Attach to the arena at the spawn sites, with a free joint.
    spawn_site.attach(spiderbot).add('freejoint')

    # Instantiate the physics and render.
    physics = mjcf.Physics.from_mjcf_model(arena)
    
    with open('model.xml', 'w') as xml_file:
      xml_file.write(spiderbot.to_xml_string())

    print('Total number of DoFs in the model:', physics.model.nv)
    print('Generalized positions:', physics.data.qpos)
    print('Generalized velocities:', physics.data.qvel)
    print('time', physics.data.time)
    print('joints', physics.data.ctrl) #this is the control input
    print('timestep', physics.model.opt.timestep)
    print('energy', physics.data.energy)
   
   
    mjcf.export_with_assets(arena, 'model')
    # PIL.Image.fromarray(physics.render()).show()

    # duration = 10   # (Seconds)
    # framerate = 30  # (Hz)
    # video = []
    # pos_x = []
    # pos_y = []
    # actuators = []  # List of actuator elements.
    # actuators.extend(spiderbot.find_all('actuator'))
    # print(actuators[0])

    # freq = 5
    # phase = 2 * np.pi * random_state.rand(len(actuators))
    # amp = 0.9

    # # Simulate, saving video frames and torso locations.
    # physics.reset()
    # while physics.data.time < duration:
    #   # Inject controls and step the physics.
    #   physics.bind(actuators).ctrl = amp * np.sin(freq * physics.data.time + phase)
    #   physics.step()

    #   # Save video frames.
    #   if len(video) < physics.data.time * framerate:
    #     pixels = physics.render()
    #     video.append(pixels.copy())

    # display_video(video, framerate)
   
