from http.server import HTTPServer, BaseHTTPRequestHandler
import pathlib
import urllib.parse
import mimetypes
from datetime import datetime
import json
import logging
from threading import Thread
import socket

BASE_DIR = pathlib.Path()
RESPONSE_OK = 200
RESPONSE_BAD = 404
RESPONSE_REDIR = 302
PORT = 3000
PORT_SOCKET = 5000
IP = '127.0.0.1'
BUFFER = 1024


def send_data_to_socket(body):
    print('send_data_to_socket body', body)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("client_socket", client_socket)
    client_socket.sendto(body, (IP, PORT_SOCKET))
    
    client_socket.close()



class HTTPHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        print('do_POST body', body)
        send_data_to_socket(body)
        
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


    def send_static(self, filename):
        self.send_response(RESPONSE_OK)

        mt, *rest = mimetypes.guess_type(filename)[0]
        if not mt:
            mt = 'text/plain'

        self.send_header('Content-Type', mt)
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())


def run(server=HTTPServer, handler=HTTPHandler):
    address = (IP, PORT)
    print('84 run, address - ', address)
    http_server = server(address, handler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


def save_data(data):
    body = urllib.parse.unquote_plus(data.decode())
    print(f'body from save_data {body}')
    try:
        payload = {str(datetime.now()): {k: v for k, v in [el.split('=') for el in body.split('&')]}}
        print(payload)
        with open(BASE_DIR.joinpath('storage/data.json'), 'w', encoding='utf-8') as fd:
            json.dump(payload, fd, ensure_ascii=False)
    except ValueError as err:
        logging.error(f'Field parse data {body} with error: {err}')
    except OSError as err:
        logging.error(f'Field write data {body} with error: {err}')


def run_socket_server(ip, port):
    print('107 run_socket_server')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    print("server", server)
    server_socket.bind(server)
    
    try:
        while True:
            data, address = server_socket.recvfrom(BUFFER)
            print(f"run_socket_server with data: {data}, address: {address}")
            save_data(data)
            print(f'Data {data} from address {address} saved')
    except KeyboardInterrupt:
        logging.info('Socket server stopped')
    finally:
        server_socket.close()



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(threadName)s %(message)s')

    thread_server = Thread(target=run)
    thread_server.start()

    thread_socket = Thread(target=run_socket_server(IP, PORT_SOCKET))
    thread_socket.start()


