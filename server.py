import OSC

from physics import Table

LASER_HOST = 'localhost'
LASER_PORT = 7780

class Handler(object):
  def __init__(self):
    self.client = OSC.OSCClient()
    self.client.connect((LASER_HOST, LASER_PORT))

  def handle_begin(self, *args):
    self.balls = []

  def handle_ball(self, path, type_, coords, source):
    self.balls.append(coords + [0,0])

  def handle_end(self, *args):
    table = Table(ball_coordinates=self.balls)
    table.propagate_state()
    self.send_message('/begin_lines')
    for v in table.ball_vectors:
      self.send_message('/line', v)
    self.send_message('/end_lines')

  def send_message(path, value=None):
    m = OSC.OSCMessage(path)
    if value is not None:
      m.append(value)
    self.client.send(m)
      

handler = Handler()
server = OSC.OSCServer(('0.0.0.0', 5006))
server.addMsgHandler('/begin_balls', handler.handle_begin)
server.addMsgHandler('/ball', handler.handle_ball)
server.addMsgHandler('/end_balls', handler.handle_end)
server.serve_forever()

