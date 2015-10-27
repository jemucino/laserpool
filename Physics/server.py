import OSC
import numpy as np

from physics import Table

# /laser/bg/begin
# /laser/set/color (0.0, 1.0, 0.0)
# /laser/line x, y, x, y
# /laser/bg/end

LASER_HOST = '192.168.0.200'
LASER_PORT = 7780

class Handler(object):
  def __init__(self):
    self.client = OSC.OSCClient()
    self.client.connect((LASER_HOST, LASER_PORT))
    self.balls = []
    self.count = 0

  def handle_begin(self, *args):
    self.count += 1
    self.balls.append([])

  def handle_ball(self, path, type_, coords, source):
    print 'RECEIVING - ', path, type_, coords, source
    if len(self.balls[-1]) < 16:
        self.balls[-1].append(coords)

  def handle_end(self, *args):
    print 'RECEIVING - ', args
    if len(self.balls) >= 20:
      print len(self.balls), self.balls
      by_ball = zip(*self.balls)
      print 'BY BALL -', len(by_ball), by_ball
      avg_balls = []
      for b in by_ball:
        xs, ys = zip(*b)
        avg_balls.append((np.average(xs), np.average(ys)))
      print 'AVG BALLS -', len(avg_balls), avg_balls
      ball_coordinates = [b + ((0, 0) if i else (-3, 0)) for i, b in enumerate(avg_balls)]
      print 'FINAL BALLS -', ball_coordinates
      table = Table(ball_coordinates=ball_coordinates)
      table.propagate_state()
      self.send_message('/laser/bg/begin')
      self.send_message('/laser/set/color', 0.0, 1.0, 0.0)
      translate = 1.143 / 2
      for v in table.ball_vectors:
        print 'DRAWING - ', v
        if len(v) > 1:
          for i, c in enumerate(v[:-1]):
            self.send_message('/laser/line', c[0], c[1] + translate, v[i+1][0], v[i+1][1] + translate)
        elif len(v) is 1:
          self.send_message('/laser/circle', v[0][0], v[0][1] + translate, 0.026)
      self.send_message('/laser/bg/end')
      self.balls = []
      self.count = 0

  def send_message(self, path, *args):
    m = OSC.OSCMessage(path)
    for a in args:
      m.append(a)
    self.client.send(m)
      

handler = Handler()
server = OSC.OSCServer(('0.0.0.0', 5006))
server.addMsgHandler('/begin_balls', handler.handle_begin)
server.addMsgHandler('/ball', handler.handle_ball)
server.addMsgHandler('/end_balls', handler.handle_end)
server.serve_forever()

