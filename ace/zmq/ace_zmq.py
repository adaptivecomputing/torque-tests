import zmq, json, uuid, datetime

_context = None

def get_context():
  global _context
  if _context==None:
    raise Exception('The ZMQ context has not been initialized; this is typically done in the setup method (be sure to teardown the context as well)')
  return _context

def setup_context():
  global _context
  _context = zmq.Context.instance()

def teardown_context():
  global _context
  _context.destroy(linger=0)

def get_socket(socket_type):
  socket = get_context().socket(socket_type)
  socket.RCVTIMEO = 2000
  return socket

def create_message(message_type, message_body):
  return json.dumps({
      'message_id':str(uuid.uuid1()), 
      'sender_id':"system-tests@localhost", 
      'sent_date':datetime.datetime.now().isoformat(), 
      'ttl':10,
      'message_type':message_type,
      'body':message_body
    }, separators=(',',':'))

def get_response(socket):
  try:
    response_string = socket.recv()
    return json.loads(response_string)
  except zmq.ZMQError:
    raise Exception('Did not receive response from socket within the timeout, the other side of the socket is probably not running')
