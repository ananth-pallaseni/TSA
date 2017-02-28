from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import cgi
import random
import itertools
import math

class Server(BaseHTTPRequestHandler):

    def circ_lay(self, num_nodes):
      step = math.pi * 2 / num_nodes
      theta = [step * i for i in range(num_nodes)]
      layout = [[math.cos(t), math.sin(t)] for t in theta]
      return layout

    def random_graph_json(self, num_nodes=None, num_edges=None):
      if num_nodes is None:
        num_nodes = max(int(random.random() * 10), 2)
      node_lst = [i for i in range(num_nodes)]
      all_edges = list(itertools.permutations(node_lst, 3))
      if num_edges is None:
        num_edges = max(int(random.random() * len(all_edges)), 2)
      print(num_edges, all_edges)
      edge_lst = random.sample(all_edges, num_edges)
      edge_lst = [list(e) for e in edge_lst]
      layout_lst = self.circ_lay(num_nodes)
      d = {'nodes': node_lst, 'edges': edge_lst, 'layout': layout_lst}
      return json.dumps(d)

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()

    def serve_index(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open('index.html', 'rb') as index:
          self.wfile.write(index.read())

    def serve_js(self, path):
      print('JS : asking for {}'.format(path));
      self.send_response(200)
      self.send_header('Content-type', 'text/javascript')
      self.end_headers()
      with open(path, 'rb') as js:
        self.wfile.write(js.read())

    def serve_json(self, path):
      self.send_response(200)
      self.send_header('Content-type', 'application/json')
      self.end_headers()
      with open(path, 'rb') as js:
        self.wfile.write(js.read())

    def serve_fake_json(self, json_data):
      self.send_response(200)
      self.send_header('Content-type', 'application/json')
      self.end_headers()
      self.wfile.write(json_data)

    # GET sends back a Hello world message
    def do_GET(self):
        print('GET {}'.format(self.path));
        path = self.path;
        fpath = path;
        if len(path) > 1:
          fpath = path[1:];
        if path == '/':
          self.serve_index();
        elif path[-3:] == '.js':
          self.serve_js(fpath);
        elif path[-5:] == '.json':
          self.serve_json(fpath);
        elif path[-6:] == '/graph':
          gj = self.random_graph_json();
          jbytes = bytes(gj, 'utf8');
          self.serve_fake_json(jbytes);

        else:
          self._set_headers();
          self.wfile.write(bytes(json.dumps({'hello': 'world', 'received': 'ok'}), 'utf8'));
        
    # POST echoes the message adding a JSON field
    def do_POST(self):
        print('POST')
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # read the message and convert it into a python dictionary
        length = int(self.headers.getheader('content-length'))
        message = json.loads(self.rfile.read(length))
        
        # add a property to the object, just to mess with data
        message['received'] = 'ok'
        
        # send the message back
        self._set_headers()
        self.wfile.write(bytes(json.dumps(message), 'utf8'))
        
def run(server_class=HTTPServer, handler_class=Server, port=8081):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    print ('Starting httpd on port %d...' % port)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print ('^C received, shutting down the web server')
        httpd.socket.close()
    
if __name__ == "__main__":
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
