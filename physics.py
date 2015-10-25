from __future__ import division

import sys
import math
import random

import numpy as np
from scipy.integrate import odeint
from matplotlib import lines
import matplotlib.pyplot as plt


g = 9.81
friction = 0.28

colors = ['black', 'yellow', 'blue', 'red', 'purple', 'orange', 'green', 'brown',
          'black', 'lightyellow', 'lightblue', 'pink', 'fuchsia', 'salmon', 'teal', 'maroon']

class Ball:

  def __init__(self, number, color, state):
    ''' Defines the state of a single ball'''
    self.number = number
    self.color = color

    self.s = state

    self.mass = .17
    self.radius = .026

  def move(self, s, t):
    ds = [0,0,0,0]
    velocity = np.array([s[2], s[3]])
    velocity_norm = np.linalg.norm(velocity)
    velocity_unit = velocity/velocity_norm if velocity_norm else np.zeros(2)
    force_friction = -velocity_unit*friction*self.mass*g

    if velocity_norm < 1e-3:
      s[2] = 0
      s[3] = 0

    ds[0] = s[2]
    ds[1] = s[3]
    ds[2] = force_friction[0] if s[2] else 0
    ds[3] = force_friction[1] if s[3] else 0

    return ds

  def propagate_state(self, timestep = 1e-3):
    self.s = odeint(self.move, self.s, [0,timestep])[1]


class Pocket:

  def __init__(self, coordinates):
    self.x = coordinates[0]
    self.y = coordinates[1]
    self.radius = 0.050


class Table:

  def __init__(self, num_balls=16, ball_coordinates=[], cue_stick={}):
    '''Define the state of the pool table'''
    self.next_ball = 0

    self.length = 2.231#2.235
    self.width = 1.121#1.143

    self.t = 0

    self.pockets = [(-self.length/2, -self.width/2),
                    (-self.length/2, self.width/2),
                    (self.length/2, -self.width/2),
                    (self.length/2, self.width/2),
                    (0, -self.width/2),
                    (0, self.width/2),
                   ]
    for i, coordinates in enumerate(self.pockets):
      self.pockets[i] = Pocket(coordinates)

    self.balls = ball_coordinates if ball_coordinates else range(num_balls)
    for i, coordinates in enumerate(self.balls):
      ball_data = self._initialize_ball(i, coordinates) if ball_coordinates else self._initialize_ball(i)
      second_ball = Ball(**ball_data)
      for first_ball in self.balls[:i]:
        distance = math.sqrt((first_ball.s[0]-second_ball.s[0])**2 + (first_ball.s[1]-second_ball.s[1])**2)
        if distance <= 2*first_ball.radius:
          self._prevent_ball_overlap(first_ball, second_ball)
        self._prevent_ball_out_of_bounds(second_ball)
      self.balls[i] = second_ball

    self.trajectories = []
    self.ball_vectors = self.trajectories

  def _initialize_ball(self, number, coordinates=None):
    if not coordinates:
      x = -self.length/2 + .100 if not number else random.uniform(-self.length/2, self.length/2)
      y = -self.width/2 + .100 if not number else random.uniform(-self.width/2, self.width/2)
      u = 1.5 if not number else 0
      v = 1.5 if not number else 0
      state = [x,y,u,v]
    else:
      state = coordinates

    color = colors[number]
    return {'number': number, 'state': state, 'color': color}

  def _detect_collision(self):
    self._detect_wall_collision()
    self._detect_ball_collision()

  def _detect_wall_collision(self):
    for i, ball in enumerate(self.balls):
      # stop ball if in pocket
      for pocket in self.pockets:
        if math.sqrt((ball.s[0]-pocket.x)**2 + (ball.s[1]-pocket.y)**2) < pocket.radius:
          ball.s = [pocket.x, pocket.y, 0, 0]
          return

      if abs(self.length / 2 - ball.s[0]) < ball.radius and ball.s[2] > 0:
        print 'colliding right', ball.number, 'at', self.t
        self.trajectories[i].append(ball.s[:2])
        ball.s[2] = -ball.s[2]
      if abs(-self.length / 2 - ball.s[0]) < ball.radius and ball.s[2] < 0:
        print 'colliding left', ball.number, 'at', self.t
        self.trajectories[i].append(ball.s[:2])
        ball.s[2] = -ball.s[2]
      if abs(self.width / 2 - ball.s[1]) < ball.radius and ball.s[3] > 0:
        print 'colliding top', ball.number, 'at', self.t
        self.trajectories[i].append(ball.s[:2])
        ball.s[3] = -ball.s[3]
      if abs(-self.width / 2 - ball.s[1]) < ball.radius and ball.s[3] < 0:
        print 'colliding bottom', ball.number, 'at', self.t
        self.trajectories[i].append(ball.s[:2])
        ball.s[3] = -ball.s[3]

  def _detect_ball_collision(self):
    for i, first_ball in enumerate(self.balls):
      for j, second_ball in enumerate(self.balls[i+1:]):
        distance = math.sqrt((first_ball.s[0]-second_ball.s[0])**2 + (first_ball.s[1]-second_ball.s[1])**2)
        if distance <= 2*first_ball.radius:
          if first_ball.s[2] > 0.01 or first_ball.s[3] > 0.01:
            self.trajectories[i].append(first_ball.s[:2])
          if second_ball.s[2] > 0.01 or second_ball.s[3] > 0.01:
            self.trajectories[i+j+1].append(second_ball.s[:2])
          print 'collision ', first_ball.number, second_ball.number, ' at ', self.t
          new_states = self.simulate_collision(first_ball, second_ball)
          self._update_ball_state(first_ball, new_states[0], second_ball, new_states[1])

  def _update_ball_state(self, first_ball, first_state, second_ball, second_state):
    first_ball.s = first_state
    second_ball.s = second_state

  def _prevent_ball_overlap(self, first_ball, second_ball):
    # calculate minimum recoil distance
    delta_position = np.array([first_ball.s[0]-second_ball.s[0], first_ball.s[1]-second_ball.s[1]])
    distance = np.linalg.norm(delta_position)
    min_recoil = delta_position/distance*(2*first_ball.radius-distance)

    # move balls by minimum recoil distance
    position1 = np.array([first_ball.s[0], first_ball.s[1]]) + 1/2*min_recoil
    position2 = np.array([second_ball.s[0], second_ball.s[1]]) - 1/2*min_recoil

    first_ball.s[0:2] = position1
    second_ball.s[0:2] = position2

  def _prevent_ball_out_of_bounds(self, ball):
    if ball.s[0] - ball.radius < -1/2*self.length:
      ball.s[0] += -1/2*self.length - (ball.s[0] - ball.radius)
    elif ball.s[0] + ball.radius > 1/2*self.length:
      ball.s[0] += 1/2*self.length - (ball.s[0] + ball.radius)

    if ball.s[1] - ball.radius < -1/2*self.width:
      ball.s[1] += -1/2*self.width - (ball.s[1] - ball.radius)
    elif ball.s[1] + ball.radius > 1/2*self.width:
      ball.s[1] += 1/2*self.width - (ball.s[1] + ball.radius)

  def simulate_collision(self, first_ball, second_ball):
    # calculate minimum recoil distance
    delta_position = np.array([first_ball.s[0]-second_ball.s[0], first_ball.s[1]-second_ball.s[1]])
    distance = np.linalg.norm(delta_position)
    min_recoil = delta_position/distance*(2*first_ball.radius-distance)

    # move balls by minimum recoil distance
    position1 = np.array([first_ball.s[0], first_ball.s[1]]) + 1/2*min_recoil
    position2 = np.array([second_ball.s[0], second_ball.s[1]]) - 1/2*min_recoil

    # impact speed
    delta_velocity = np.array([first_ball.s[2]-second_ball.s[2], first_ball.s[3]-second_ball.s[3]])
    velocity1 = np.array(first_ball.s[2:4]) - 1/2*np.dot(delta_velocity, min_recoil/np.linalg.norm(min_recoil))*min_recoil/np.linalg.norm(min_recoil)
    velocity2 = np.array(second_ball.s[2:4]) + 1/2*np.dot(delta_velocity, min_recoil/np.linalg.norm(min_recoil))*min_recoil/np.linalg.norm(min_recoil)

    return (np.concatenate([position1, velocity1]), np.concatenate([position2, velocity2]))

  def propagate_state(self, timestep = 1e-2, plot=False):
    self.trajectories = [[ball.s[:2]] for ball in self.balls]
    for i in range(200):
      for ball in self.balls:
        ball.propagate_state(timestep)

      self.t += timestep
      self._detect_collision()

    for i, v in enumerate(self.trajectories):
      if len(v) > 1:
        v.append(self.balls[i].s[:2])
        print self.balls[i].s[:2]

    if plot:
      self.draw_state()

  def draw_state(self):
    # draw the pool table
    fig = plt.figure(1)
    fig.gca().add_artist(plt.Rectangle((-self.length/2, -self.width/2),self.length,self.width,color='lightgreen'))

    # draw the pool table pockets
    for pocket in self.pockets:
      fig.gca().add_artist(plt.Circle((pocket.x, pocket.y),pocket.radius,color='gray'))

    # draw the pool balls
    for ball in self.balls:
      if ball.number and i%5 == 0:
        fig.gca().add_artist(plt.Circle((ball.s[0],ball.s[1]),ball.radius,color=ball.color,alpha=0.5))
      elif i%5 == 0:
        fig.gca().add_artist(plt.Circle((ball.s[0],ball.s[1]),ball.radius,color=ball.color,alpha=0.5,fill=0))

    # draw the ball trajectories
    for v in self.trajectories:
      xs = [x for x, y in v]
      ys = [y for x, y in v]
      fig.gca().add_artist(lines.Line2D(xs, ys, color='black'))

    # show the plot
    plt.axis([-2, 2, -2, 2])
    plt.show()



if __name__ == '__main__':
  seed = random.randint(0, 10000000)
  if len(sys.argv) > 1:
    seed = int(sys.argv[1])
  print 'SEED', seed
  random.seed(seed)

  length = 2.235
  width = 1.143

  coordinates = range(16)
  for i, coodinate in enumerate(coordinates):
    x = -length/2 + .100 if not i else random.uniform(-length/2, length/2)
    y = -width/2 + .100 if not i else random.uniform(-width/2, width/2)
    u = 1.5 if not i else 0
    v = 1.5 if not i else 0
    coordinates[i] = [x,y,u,v]

  table = Table(ball_coordinates=coordinates)
#   table = Table(16)
  table.propagate_state(plot=True)
