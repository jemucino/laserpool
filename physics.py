import sys
import math
import random

import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt


g = 9.81
friction = 0.28

colors = ['white', 'yellow', 'blue', 'red', 'purple', 'orange', 'green', 'brown',
          'black', 'lightyellow', 'lightblue', 'pink', 'fuchsia', 'salmon', 'lightgreen', 'maroon']

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


class Table:

  def __init__(self, num_balls):
    '''Define the state of the pool table'''
    self.balls = range(num_balls)
    self.next_ball = 0

    self.length = 2.235
    self.width = 1.143

    for _, i in enumerate(self.balls):
      ball_data = self._initialize_ball()
      self.balls[i] = Ball(**ball_data)

  def _initialize_ball(self):
    number = self.next_ball
    state = [random.uniform(-self.length/2, self.length/2), random.uniform(-self.width/2, self.width/2), random.uniform(-1,1), random.uniform(-1,1)]
    color = colors[number]
    self.next_ball += 1
    return {'number': number, 'state': state, 'color': color}

  def _detect_collision(self):
    self._detect_wall_collision()
    self._detect_ball_collision()

  def _detect_wall_collision(self):
    for i, ball in enumerate(self.balls):
      if abs(self.length / 2 - ball.s[0]) < ball.radius and ball.s[2] > 0:
        print 'colliding right', ball.s
        ball.s[2] = -ball.s[2]
      if abs(-self.length / 2 - ball.s[0]) < ball.radius and ball.s[2] < 0:
        print 'colliding left', ball.s
        ball.s[2] = -ball.s[2]
      if abs(self.width / 2 - ball.s[1]) < ball.radius and ball.s[3] > 0:
        print 'colliding top', ball.s
        ball.s[3] = -ball.s[3]
      if abs(-self.width / 2 - ball.s[1]) < ball.radius and ball.s[3] < 0:
        print 'colliding bottom', ball.s
        ball.s[3] = -ball.s[3]

  def _detect_ball_collision(self):
    for i, first_ball in enumerate(self.balls):
      for second_ball in self.balls[i+1:]:
        distance = math.sqrt((first_ball.s[0]-second_ball.s[0])**2 + (first_ball.s[1]-second_ball.s[1])**2)
        if distance <= 2*first_ball.radius:
          print 'collision: ', first_ball.number, second_ball.number
          new_states = self.simulate_collision(first_ball, second_ball)
          self._update_ball_state(first_ball, new_states[0], second_ball, new_states[1])

  def _update_ball_state(self, first_ball, first_state, second_ball, second_state):
    first_ball.s = first_state
    second_ball.s = second_state

  def simulate_collision(self, first_ball, second_ball):
    # calculate minimum recoil distance
    delta_position = np.array([first_ball.s[0]-second_ball.s[0], first_ball.s[1]-second_ball.s[1]])
    distance = np.linalg.norm(delta_position)
    min_recoil = delta_position*(2*first_ball.radius-distance)/distance

    # move balls by minimum recoil distance
    position1 = np.array([first_ball.s[0], first_ball.s[1]]) + 1/2*min_recoil
    position2 = np.array([second_ball.s[0], second_ball.s[1]]) - 1/2*min_recoil

    # impact speed
    delta_velocity = np.array([first_ball.s[2]-second_ball.s[2], first_ball.s[3]-second_ball.s[3]])
    velocity1 = np.array(first_ball.s[2:4]) - 1/2*np.dot(delta_velocity, np.linalg.norm(min_recoil))
    velocity2 = np.array(second_ball.s[2:4]) + 1/2*np.dot(delta_velocity, np.linalg.norm(min_recoil))

    print position1, velocity1
    print position2, velocity2

    return (np.concatenate([position1, velocity1]), np.concatenate([position2, velocity2]))

  def propagate_state(self, timestep = 1e-1):
    for i in range(100):
      fig = plt.figure(1)
      fig.gca().add_artist(plt.Rectangle((-self.length/2, -self.width/2),self.length,self.width,color='lightgreen',alpha=0.1))
      for ball in self.balls:
        ball.propagate_state(timestep)
#         print ball.number, ': ', ball.s
        fig.gca().add_artist(plt.Circle((ball.s[0],ball.s[1]),ball.radius,color=ball.color,alpha=0.5))
      self._detect_collision()

    plt.axis([-2, 2, -2, 2])
    plt.show()


if __name__ == '__main__':
  seed = random.randint(0, 10000000)
  if len(sys.argv) > 1:
    seed = int(sys.argv[1])
  print 'SEED', seed
  random.seed(seed)
  table = Table(16)
  table.propagate_state()
