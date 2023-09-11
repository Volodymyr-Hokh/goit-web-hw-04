from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import mimetypes
from pathlib import Path
import socket
from threading import Thread   
import urllib.parse


SOCKET_IP = "127.0.0.1"
SOCKET_PORT = 5000
STORAGE_PATH = Path("storage")

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        front_path = Path('./front-init')
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file(front_path.joinpath('index.html'))
        elif pr_url.path == '/message':
            self.send_html_file(front_path.joinpath('message.html'))
        else:
            if front_path.joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file(front_path.joinpath('error.html'), 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        file_path = f'./front-init/{self.path}'
        self.send_response(200)
        mt = mimetypes.guess_type(file_path)
        if mt:
            self.send_header('Content-type', mt[0])
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(file_path, 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        send_data_to_socket(data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()



def save_data(data):
    data_parse = urllib.parse.unquote_plus(data.decode())

    data_path = STORAGE_PATH.joinpath("data.json")
    try:
        with open(data_path, encoding="utf-8") as file:
            data_json = json.load(file)
    except FileNotFoundError:
        data_json = {}
    data_json[str(datetime.now())] = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}

    with open(data_path, "w", encoding="utf-8") as fh:
        json.dump(data_json, fh, indent=4, ensure_ascii=False)


def send_data_to_socket(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (SOCKET_IP, SOCKET_PORT))
    sock.close()


def run_socket_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            save_data(data)

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    print("Server started!")
    if not STORAGE_PATH.exists():
        STORAGE_PATH.mkdir()

    http_server_thread = Thread(target=run_http_server)
    http_server_thread.start()

    socket_server_thread = Thread(target=run_socket_server, args=(SOCKET_IP, SOCKET_PORT))
    socket_server_thread.start()

    http_server_thread.join()
    socket_server_thread.join()
