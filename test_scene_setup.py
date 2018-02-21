#!/usr/bin/env python3
import sys, os

from math import pi, sin, cos

import pprint

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3

# TODO: move to settings
cam_speed = 0.2

class TestGame(ShowBase):
    """TestGame

    Credit: Skyboxing code borrowed from skybox sample code by CheapestPixels
    on GitHub
    """

    # Bookkeeping for the rotation around the model
    angle        = 0.0
    pitch        = 0.0
    adjust_angle = 0
    adjust_pitch = 0
    last_time    = 0.0
    wiresky = False

    def __init__(self):
        ShowBase.__init__(self)

        # Load the environment model.
        self.surfdog = self.loader.loadModel("models/surfdog")
        # Reparent the model to render.
        self.surfdog.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.surfdog.setScale(5.0, 0.1, 5.0)
        self.surfdog.setPos(-8, 22, -2)

        # Add the spinCameraTask procedure to the task manager
        # self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

        self.loadStarfield()
        self.loadSkybox()
# -actor-         # Load and transform the panda actor.
# -actor-         self.pandaActor = Actor("models/panda-model",
# -actor-                                 {"walk": "models/panda-walk4"})
# -actor-         self.pandaActor.setScale(0.005, 0.005, 0.005)
# -actor-         self.pandaActor.reparentTo(self.render)
# -actor-         # Loop its animation.
# -actor-         self.pandaActor.loop("walk")
# -actor- 
# -actor-         # Create the four lerp intervals needed for the panda to
# -actor-         # walk back and forth.
# -actor-         pandaPosInterval1 = self.pandaActor.posInterval(13,
# -actor-             Point3(0, -10, 0),
# -actor-             startPos=Point3(0, 10, 0))
# -actor-         pandaPosInterval2 = self.pandaActor.posInterval(13,
# -actor-             Point3(0, 10, 0),
# -actor-             startPos=Point3(0, -10, 0))
# -actor-         pandaHprInterval1 = self.pandaActor.hprInterval(3,
# -actor-             Point3(180, 0, 0),
# -actor-             startHpr=Point3(0, 0, 0))
# -actor-         pandaHprInterval2 = self.pandaActor.hprInterval(3,
# -actor-             Point3(0, 0, 0),
# -actor-             startHpr=Point3(180, 0, 0))
# -actor- 
# -actor-         # Create and play the sequence that coordinates the intervals.
# -actor-         self.pandaPace = Sequence(pandaPosInterval1,
# -actor-                                   pandaHprInterval1,
# -actor-                                   pandaPosInterval2,
# -actor-                                   pandaHprInterval2,
# -actor-                                   name="pandaPace")
# -actor-         self.pandaPace.loop()


        # Accept keypresses for looking around
        self.camera.set_pos(sin(self.angle)*20,-cos(self.angle)*20,0)
        self.camera.look_at(0,0,0)
        # Key events and camera movement task
        self.accept("arrow_left", self.adjust_turning, [-1.0, 0.0])
        self.accept("arrow_left-up", self.adjust_turning, [1.0, 0.0])
        self.accept("arrow_right", self.adjust_turning, [1.0, 0.0])
        self.accept("arrow_right-up", self.adjust_turning, [-1.0, 0.0])
        self.accept("arrow_up", self.adjust_turning, [0.0, 1.0])
        self.accept("arrow_up-up", self.adjust_turning, [0.0, -1.0])
        self.accept("arrow_down", self.adjust_turning, [0.0, -1.0])
        self.accept("arrow_down-up", self.adjust_turning, [0.0, 1.0])

        # swap skybox/skysphere
        self.accept("s", self.swap_background)
        self.accept("w", self.toggle_sky_wireframe)

        self.accept("escape", sys.exit)
        self.taskMgr.add(self.update_camera, 'adjust camera', sort = 10)

    def adjust_turning(self, heading, pitch):
        self.adjust_angle += heading
        self.adjust_pitch += pitch

    def update_camera(self, task):
        if task.time != 0.0:
            dt = task.time - self.last_time
            self.last_time = task.time
            self.angle += pi * dt * self.adjust_angle * cam_speed
            self.pitch += pi * dt * self.adjust_pitch * cam_speed
            # Why /2.001 and not an even 2.0? Because then we'd have to set_Hpr
            # explicitly, as look_at can't deduce the heading when the camera is
            # exactly above/below the spheres center.
            if self.pitch > pi/2.001:
                self.pitch = pi/2.001
            if self.pitch < -pi/2.001:
                self.pitch = -pi/2.001
            self.camera.set_pos(sin(self.angle)*cos(abs(self.pitch))*20,
                                -cos(self.angle)*cos(abs(self.pitch))*20,
                                sin(self.pitch)*20)
            self.camera.look_at(0,0,0)
        return Task.cont

    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont

    def loadStarfield(self):
        self.sky = 'starfield'
        self.starfield = self.loader.loadModel("models/starfield.egg")
        self.starfield.reparentTo(self.camera)
        self.starfield.setScale(0.0015, 0.0015, 0.0015)
        self.starfield.set_two_sided(True)
        self.starfield.set_bin("background", 0)
        self.starfield.set_depth_write(False)
        self.starfield.set_compass()

    def loadSkybox(self):
        # The skybox part
        self.skybox = self.loader.loadModel("models/skybox_1024")
        self.skybox.reparentTo(self.camera)
        #self.skybox.set_render_mode_wireframe()
        self.skybox.set_two_sided(True)
        self.skybox.set_bin("background", 0)
        self.skybox.set_depth_write(False)
        self.skybox.set_compass()
        self.skybox.hide()

    def toggle_sky_wireframe(self):
        if self.wiresky:
            self.skybox.clearRenderMode()
            self.starfield.clearRenderMode()
            self.wiresky = False
        else:
            self.skybox.set_render_mode_wireframe()
            self.starfield.set_render_mode_wireframe()
            self.wiresky = True

    def swap_background(self):
        if self.sky == 'skybox':
            self.skybox.hide()
            self.starfield.show()
            self.sky = 'starfield'
        else:
            self.skybox.show()
            self.starfield.hide()
            self.sky = 'skybox'

if __name__ == '__main__':
    app = TestGame()
    app.run()