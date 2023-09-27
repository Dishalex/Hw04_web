from http.server import HTTPServer, BaseHTTPRequestHandler
import pathlib
import urllib.parse
import mimetypes
from datetime import datetime
import json

BASE_DIR = pathlib.Path()
RESPONSE_OK = 200
RESPONSE_BAD = 404
RESPONSE_REDIR = 302
PORT = 3000

class HTTPHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        body = urllib.parse.unquote_plus(body.decode())

        payload = {str(datetime.now()): {k: v for k, v in [el.split('=') for el in body.split('&')]}}
        print(payload)
        with open(BASE_DIR.joinpath('storage/data.json'), 'w', encoding='utf-8') as fd:
            json.dump(payload, fd, ensure_ascii='utf-8')



        self.send_response(RESPONSE_REDIR)
        self.send_header('Location', 'message.html')
        self.end_headers()


    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
     
        match route.path:
            case '/':
                self.send_html('index.html')
            case '/message.html':
                self.send_html('message.html')           
            case _:
                file = BASE_DIR / route.path[1:]
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html('error.html', RESPONSE_BAD)




    def send_html(self, filename, status_code=RESPONSE_OK):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())


    def send_static(self, filename, status_code=RESPONSE_OK):
        self.send_response(status_code)

        mt = mimetypes.guess_type(filename)[0]
        if not mt:
            mt = 'text/plain'

        self.send_header('Content-Type', mt)
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())



def run(server=HTTPServer, handler=HTTPHandler):
    address = ('', PORT)
    http_server = server(address, handler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


if __name__ == '__main__':
    run()
