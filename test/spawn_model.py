import mujoco as mj
import numpy as np
from mujoco.glfw import glfw

import os
import sys
sys.path.insert(0, 'Mujoco-Tutorial/')
from mujocobase import MuJoCoBase
import argparse




class spawn(MuJoCoBase):
    def __init__(self, xml_path):
        super().__init__(xml_path)
        self.simend = 60.0

    def reset(self):
        # Set camera configuration
        self.cam.azimuth = 89.608063
        self.cam.elevation = -11.588379
        self.cam.distance = 5.0
        self.cam.lookat = np.array([0.0, 0.0, 1.5])

    def controller(self, model, data):
        pass

    def simulate(self):
        while not glfw.window_should_close(self.window):
            simstart = self.data.time

            while (self.data.time - simstart < 1.0/60.0):
                # Step simulation environment
                mj.mj_step(self.model, self.data)

            if self.data.time >= self.simend:
                break

            # get framebuffer viewport
            viewport_width, viewport_height = glfw.get_framebuffer_size(
                self.window)
            viewport = mj.MjrRect(0, 0, viewport_width, viewport_height)

            # Update scene and render
            mj.mjv_updateScene(self.model, self.data, self.opt, None, self.cam,
                               mj.mjtCatBit.mjCAT_ALL.value, self.scene)
            mj.mjr_render(viewport, self.scene, self.context)

            # swap OpenGL buffers (blocking call due to v-sync)
            glfw.swap_buffers(self.window)

            # process pending GUI events, call GLFW callbacks
            glfw.poll_events()

        glfw.terminate()


def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--xml_path', type=str, default='my_envs/hexapod-rl/descriptions/spiderbot.xml')
    args = parser.parse_args()
    xml_path = args.xml_path
  
    sim = spawn(xml_path)
    print(sim.model.ngeom)
    sim.reset()
    sim.simulate()


if __name__ == "__main__":
    main()
