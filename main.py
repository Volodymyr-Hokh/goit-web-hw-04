from http.server import HTTPServer, BaseHTTPRequestHandler
import mimetypes
from pathlib import Path
import urllib.parse


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
        


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
