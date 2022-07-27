from http.server import BaseHTTPRequestHandler
import json
import fileManager as fm

BASE_URL = 'webapp/'

import os
class Server(BaseHTTPRequestHandler):
  manager:fm.fileManager = None
  def do_GET(self):
    if self.path == '/' or self.path == '/?':
      self.path = '/index.html'
    try:
      split_path = os.path.splitext(self.path)
      request_extension = split_path[1]
      if request_extension != ".py":
        f = open(os.path.join(BASE_URL,self.path[1:])).read()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(f, 'utf-8'))
      else:
        f = "File not found"
        self.send_error(404,f)
    except:
      f = "File not found"
      self.send_error(404,f)
      
  def do_POST(self):
    try:
      if self.path == '/newLabel':
        length = int(self.headers.get('content-length'))
        body = self.rfile.read(length)
        body = body.decode('utf-8')
        bodyObj = json.loads(body)
        try:
          self.manager.addLabel(fm.Label(bodyObj))
          self.send_response(200)
          self.end_headers()
        except Exception as e:
          self.send_error(400,e.message if hasattr(e, 'message') else e)
        return
      if self.path == '/getLabels':
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        labels = self.manager.getLabelsFromXML()
        imported = set([l['name'] for l in self.manager.getLabelsFromJS('AK')+self.manager.getLabelsFromJS('LZ')])
        for l in labels:
          l['imported'] = l['fullName'] in imported
        self.wfile.write(json.dumps(labels).encode(encoding='utf_8'))
        return
      f = "Service not found"
      self.send_error(404,f)
    except:
      self.send_error(500)
    