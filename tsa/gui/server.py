from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import cgi
import random
import itertools
import math
from urllib.parse import urlparse
import webbrowser

import tsa

SYSTEM = []


class Server(BaseHTTPRequestHandler):

    def circ_lay(self, num_nodes):
      step = math.pi * 2 / num_nodes
      theta = [step * i for i in range(num_nodes)]
      layout = [[math.cos(t), math.sin(t)] for t in theta]
      return layout

    def random_graph_json(self, num_nodes=None, num_edges=None):
      if num_nodes is None:
        num_nodes = max(int(random.random() * 10), 3)
      node_lst = [i for i in range(num_nodes)]
      all_edges = list(itertools.permutations(node_lst, 2)) + [(i,i) for i in node_lst]
      if num_edges is None:
        num_edges = max(int(random.random() * len(all_edges)), 2)
      print(len(all_edges), num_edges)
      edge_lst = random.sample(all_edges, num_edges)
      edge_lst = [list(e) for e in edge_lst]

      edge_lst = [ {'from': e[0], 'to': e[1], 'parameters': []} for e in edge_lst]
      node_lst = [ {'id': n, 'parameters': []} for n in node_lst]
      layout_lst = self.circ_lay(num_nodes)
      d = {'rank': 0, 'dist':10, 'nodes': node_lst, 'edges': edge_lst, 'layout': layout_lst}
      return json.dumps(d)

    def system_stats(self):
      d = {}
      d['num-graphs'] = len(SYSTEM)
      return d;

    def occ_mat(self, topx=-1):
      if topx < 0:
        topx = len(SYSTEM)
      num_nodes = len(SYSTEM[0]['nodes'])
      mat = [[0 for i in range(num_nodes)] for j in range(num_nodes)]
      for g in SYSTEM[:topx]:
        for e in g['edges']:
          mat[e['from']][e['to']] += 1
      return mat



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

    def serve_css(self, path):
      self.send_response(200)
      self.send_header('Content-type', 'text/css')
      self.end_headers()
      with open(path, 'rb') as css:
        self.wfile.write(css.read())

    def serve_html(self, path):
      self.send_response(200)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      with open(path, 'rb') as html:
        self.wfile.write(html.read())

   
    def do_GET(self):
        print('GET {}'.format(self.path));
        path = self.path;
        fpath = path;
        if len(path) > 1:
          fpath = path[1:];

        # named pages:
        if path == '/':
          self.serve_index();
        elif path[-13:] == '/graph/random':
          gj = self.random_graph_json();
          jbytes = bytes(gj, 'utf8');
          self.serve_fake_json(jbytes);
        elif path[-13:] == '/inspect.html':
          self.serve_html('inspect.html')
        elif path[-11:] == '/index.html':
          self.serve_html('index.html')
        elif path[-13:] == '/summary.html':
          self.serve_html('summary.html')
        elif path[-16:] == '/prevalence.html':
          self.serve_html('prevalence.html')

        elif path[-13:] == '/test.html':
          self.serve_html('test.html')

        elif '/graph/' in path:
          i = path.find('/graph/')
          print(path[i+7 : ])
          num = int(path[i+7 : ])
          if num >= 0 and num < len(SYSTEM):
            gj = json.dumps(SYSTEM[num])
            jbytes = bytes(gj, 'utf-8');
            self.serve_fake_json(jbytes);

        elif '/load/' in path:
          i = path.find('/load/')
          lpath = path[i+6:]
          print('lpath = ' + lpath)
          self.load_system_json(lpath)

        elif path[-6:] == '/stats':
          gj = json.dumps(self.system_stats())
          jbytes = bytes(gj, 'utf-8')
          self.serve_fake_json(jbytes)

        elif path[-12:] == '/occ-mat/all':
          gj = json.dumps(self.occ_mat())
          jbytes = bytes(gj, 'utf-8')
          self.serve_fake_json(jbytes)
        elif '/occ-mat/' in path:
          i = path.find('/occ-mat/')
          topx = int(path[i+9 : ])
          gj = json.dumps(self.occ_mat(topx))
          jbytes = bytes(gj, 'utf-8');
          self.serve_fake_json(jbytes);
        elif path[-11:] == '/num-graphs':
          num = len(SYSTEM)
          gj = json.dumps(num)
          jbytes = bytes(gj, 'utf-8')
          self.serve_fake_json(jbytes);




        # generic pages
        else:
          if path[-3:] == '.js':
            self.serve_js(fpath);
          elif path[-5:] == '.json':
            self.serve_json(fpath);
          elif path[-4:] == '.css':
            print('asked for css at path: ' + fpath)
            self.serve_css(fpath)
          elif path[-5] == '.html':
            self.serve_html(fpath)
          else:
            self._set_headers();
            self.wfile.write(bytes(json.dumps({'hello': 'world', 'received': 'ok'}), 'utf8'));
          
    # POST echoes the message adding a JSON field
    def do_POST(self):
        print('POST')
        print(self.path)
        ctype, pdict = cgi.parse_header(self.headers['content-type'])

      
        # if ctype == 'multipart/form-data':
        #   pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        #   postvars = cgi.parse_multipart(self.rfile, pdict)
        #   print (postvars.keys())

        # # refuse to receive non-json content
        # if ctype != 'application/json':
        #     self.send_response(400)
        #     self.end_headers()
        #     return
            
        # # read the message and convert it into a python dictionary
        # length = int(self.headers['content-length'])
        # print(length)
        # data = self.rfile.read(length)
        # data = data.decode('utf-8')
        # message = json.loads(data)

        print(form)
        print('file' in form)
      
        
        # add a property to the object, just to mess with data
        message['received'] = 'ok'
        
        # send the message back
        self._set_headers()
        self.wfile.write(bytes(json.dumps(message), 'utf8'))

        
def run(server_class=HTTPServer, handler_class=Server, port=8081):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    webbrowser.open_new_tab('http://localhost:' + str(port))
    
    print ('Starting httpd on port %d...' % port)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print ('^C received, shutting down the web server')
        httpd.socket.close()
    
if __name__ == "__main__":
    from sys import argv
    
    print('argv' + str(argv))
    if len(argv) == 2:
        run(port=int(argv[1]))
    elif len(argv) == 3:
        opt = argv[1]
        val = argv[2]
        if opt == '-l':
          with open(val, 'r') as f:
            SYSTEM = json.load(f)
          run()


    else:
        run()
