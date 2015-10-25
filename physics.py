import math
import random

g = 9.81
friction = 0.28

class Ball:

  def __init__(self, number, state):
    ''' Defines the state of a single ball'''
    self.number = number
    self.s = state
#     self.x = s[0]
#     self.y = s[1]
#     self.u = s[2]
#     self.v = s[3]

    self.mass = .17
    self.radius = .026

  def move(self, s, t):
    ds = [0,0,0,0]

    if s[2] < 1e-3:
      s[2] = 0

    if s[3] < 1e-3:
      s[3] = 0

    ds[0] = s[2]
    ds[1] = s[3]
    ds[2] = -friction*self.mass*g if s[2] else 0
    ds[3] = -friction*self.mass*g if s[3] else 0

    return ds

  def propagate_state(self, timestep = 1e-1):
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
    state = [random.uniform(-self.length/2, self.length/2), random.uniform(-self.width/2, self.width/2), random.random(), random.random()]
    self.next_ball += 1
    return {'number': number, 'state': state}

  def detect_collision(self):
    for i, first_ball in enumerate(self.balls):
      for second_ball in self.balls[i+1:]:
        distance = math.sqrt((first_ball.s[0]-second_ball.s[0])**2 + (first_ball.s[1]-second_ball.s[1])**2)
        if distance < 2*first_ball.radius:
          print 'collision: ', first_ball.number, second_ball.number

  def propagate_state(self, timestep = 1e-1):
    for i in range(100):
      for ball in self.balls:
          ball.propagate_state(timestep)
          print ball.number, ': ', ball.s

      self.detect_collision()


if __name__ == '__main__':
  from scipy.integrate import odeint

  table = Table(16)
  table.propagate_state()