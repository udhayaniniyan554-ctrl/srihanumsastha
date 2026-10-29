import http.server
import socketserver
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

def run_server():
    os.chdir(DIRECTORY)
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"===============================================================")
    print(f" Sri Hanum Sastha Enterprises - Server Running!")
    print(f" Local URL: http://localhost:{PORT}/")
    print(f" Local IP:  http://127.0.0.1:{PORT}/")
    print(f" Serving Directory: {DIRECTORY}")
    print(f"===============================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == "__main__":
    run_server()
