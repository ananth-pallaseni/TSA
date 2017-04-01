from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import cgi
import random
import itertools
import math
from urllib.parse import urlparse
import webbrowser
import numpy as np

import tsa
import os

SYSTEM = []
SYSTEM_INFO = []
THIS_DIR = ''
THIS_FN = ''

MODEL_BAG = None

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

    def occ_mat(self, topx=-1):
      if topx < 0:
        topx = len(SYSTEM)
      num_nodes = len(SYSTEM[0]['nodes'])

      # Init matrix assuming no cplx edges
      mat = [[{'occurrences': 0} for i in range(num_nodes)] for j in range(num_nodes)]
      
      # cplx maps from hash->complex node id
      cplx = {}

      # next complex node id = num_nodes + new_offset
      new_offset = 0

      # iterate through all edges
      for g in SYSTEM[:topx]:
        for e in g['edges']:
          e_from = e['from']
          e_to = e['to']
          if type(e_from) != list:
            mat[e_from][e_to]['occurrences'] += 1
          else:
            # perform a basic hash on the edge
            fhash =  (3 + e_from[0])*3 + e_from[1]

            # if edge doesn't exist, add it and add a new row to the matrix
            if fhash not in cplx:
              cplx[fhash] = num_nodes + new_offset
              new_offset += 1
              mat = mat + [[{'occurrences': 0, 'complex': e_from} for i in range(num_nodes)]]

            # increment number of this edge found
            mat[cplx[fhash]][e_to]['occurrences'] += 1

      return mat, cplx

    def occ_graph(self, topx=-1):
      if topx < 0:
        topx = len(SYSTEM)
      preval_g = {'rank': 0, 'dist': 0}
      nodes = dict([(n['id'], n) for n in SYSTEM[0]['nodes']])
      edges = {}
      layout = []
      next_idx = len(nodes)
      for g in SYSTEM[:topx]:
        for e in g['edges']:
          e_from = e['from']
          if type(e_from) == list:
            e_from = tuple(e_from)
          e_to = e['to']
          if (e_from, e_to) not in edges:
            edges[(e_from, e_to)] = {'from': e_from,
              'to': e_to,
              'interaction': e['interaction'],
              'parameters': e['parameters'],
              'occurrences': 1}
          else:
            edges[(e_from, e_to)]['occurrences'] += 1

      step = 2*math.pi / len(nodes)
      layout = [[math.cos(step * i), math.sin(step * i)] for i in range(len(nodes))]

      nodes = list(nodes.values())
      edges = list(edges.values())
      return [nodes, edges, layout]

    def param_density(self, numtop, ptype, index):
      x, y = tsa.param_density(MODEL_BAG, numtop, ptype, index)
      return x, y



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
      realpath = os.path.join(THIS_DIR, path)
      with open(realpath, 'rb') as js:
        self.wfile.write(js.read())

    def serve_json(self, path):
      self.send_response(200)
      self.send_header('Content-type', 'application/json')
      self.end_headers()
      realpath = os.path.join(THIS_DIR, path)
      with open(realpath, 'rb') as js:
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
      realpath = os.path.join(THIS_DIR, path)
      with open(realpath, 'rb') as css:
        self.wfile.write(css.read())

    def serve_html(self, path):
      self.send_response(200)
      self.send_header('Content-type', 'text/html')
      self.end_headers()
      realpath = os.path.join(THIS_DIR, path)
      with open(realpath, 'rb') as html:
        self.wfile.write(html.read())

   
    def do_GET(self):
        print('GET {}'.format(self.path));
        path = self.path;
        fpath = path;
        if len(path) > 1:
          fpath = path[1:];

        # named pages:
        if path == '/':
          self.serve_html('summary.html')
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
        elif path[-13:] == '/welcome.html':
          self.serve_html('welcome.html')
        elif path[-12:] == '/mosaic.html':
          self.serve_html('mosaic.html')
        elif path[:] == '/density.html':
          self.serve_html('density.html')

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
          gj = json.dumps(SYSTEM_INFO)
          jbytes = bytes(gj, 'utf-8')
          self.serve_fake_json(jbytes)

        elif path[-12:] == '/occ-mat/all':
          gj = json.dumps(list(self.occ_mat()))
          jbytes = bytes(gj, 'utf-8')
          self.serve_fake_json(jbytes)
        elif path[-14:] == '/occ-graph/all':
          gj = json.dumps(self.occ_graph())
          jbytes = bytes(gj, 'utf-8')
          self.serve_fake_json(jbytes)
        elif '/occ-mat/' in path:
          i = path.find('/occ-mat/')
          topx = int(path[i+9 : ])
          gj = json.dumps(self.occ_mat(topx))
          jbytes = bytes(gj, 'utf-8');
          self.serve_fake_json(jbytes);
        elif '/occ-graph/' in path:
          i = path.find('/occ-graph/')
          topx = int(path[i+11 : ])
          gj = json.dumps(self.occ_graph(topx))
          jbytes = bytes(gj, 'utf-8');
          self.serve_fake_json(jbytes);
        elif path[-11:] == '/num-graphs':
          num = len(SYSTEM)
          gj = json.dumps(num)
          jbytes = bytes(gj, 'utf-8')
          self.serve_fake_json(jbytes);
        elif path[-7:] == '/mosaic':
          ntop = 100
          thrsh = 0.01
          mosaic_data = tsa.chi_edge(MODEL_BAG, num_top=ntop, threshold=thrsh)
          mosaic_data = [{'interactome1': e1, 'interactome2': e2, 'pVal':pval, 'contingency': [cc.tolist() if type(cc) == np.ndarray else cc for cc in ctab]} for (e1, e2, pval, ctab) in mosaic_data]

          gj = json.dumps(mosaic_data)
          jbytes = bytes(gj, 'utf-8');
          self.serve_fake_json(jbytes)
        elif path[-11:] == '/node_names':
          gj = json.dumps(SYSTEM_INFO['node_names'])
          jbytes = bytes(gj, 'utf-8');
          self.serve_fake_json(jbytes)
        elif '/pdensity/' in path:
          i = path.find('/pdensity/')
          args = path[i+10 : ].split('?')
          if len(args) != 3:
            raise ValueError('Need 3 arguments in path')
          try:
            numtop = int(args[0])
            ptype = args[1]
            index = int(args[2])
          except ValueError:
            raise ValueError
          x, y = self.param_density(numtop, ptype, index)
          x = list(x)
          y = list(y)
          gj = json.dumps({'x': x, 'y': y})
          jbytes = bytes(gj, 'utf-8');
          self.serve_fake_json(jbytes)
        elif path[-7:] == '/ptypes':
          ptypes = SYSTEM_INFO['node_ptypes'] + SYSTEM_INFO['edge_ptypes']
          gj = json.dumps(ptypes)
          jbytes = bytes(gj, 'utf-8');
          self.serve_fake_json(jbytes)
        elif path[-9:] == '/getedges':
          edges = MODEL_BAG.get_edges()
          


        # generic pages
        else:
          if path[-3:] == '.js':
            self.serve_js(fpath);
          elif path[-5:] == '.json':
            self.serve_json(fpath);
          elif path[-4:] == '.css':
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

    global THIS_DIR
    THIS_DIR, THIS_FN = os.path.split(__file__)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print ('^C received, shutting down the web server')
        httpd.socket.close()

def run_using_model_bag(model_bag):
  global SYSTEM
  global SYSTEM_INFO
  global MODEL_BAG
  mb = json.loads(tsa.model_bag_to_json(model_bag))
  SYSTEM = mb['models']
  SYSTEM_INFO = mb['systemInfo']
  MODEL_BAG = model_bag
  run()

def run_using_fname(fname):
  global SYSTEM
  global SYSTEM_INFO
  global MODEL_BAG
  with open(fname, 'r') as f:
    model_bag = json.load(f)
    SYSTEM = model_bag['models']
    SYSTEM_INFO = model_bag['systemInfo']
    MODEL_BAG = tsa.json_to_model_bag(f)
  run()
    
if __name__ == "__main__":
    from sys import argv
    
    print('argv' + str(argv))
    if len(argv) == 2:
        # run(port=int(argv[1]))
        val = argv[1]
        run_using_fname(val)
    else:
        raise ValueError('Need to input a model file')

