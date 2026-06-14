import http.server
import socketserver
import webbrowser
import os
import threading
import subprocess
import json
import sys
from urllib.parse import urlparse

PORT = 8000

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/generar':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length)) if length else {}
                max_horas = str(body.get('maxHorasLibres', 3))
                resultado = subprocess.run(
                    [sys.executable, 'main.py', max_horas],
                        capture_output=True,
                        text=True
                )
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'ok': True,
                    'output': resultado.stdout
                }).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'ok': False,
                    'error': str(e)
                }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Silencia los logs del servidor

def start_server():
    global PORT
    while True:
        try:
            httpd = socketserver.TCPServer(("", PORT), Handler)
            return httpd
        except OSError as e:
            if e.errno in (98, 48):
                PORT += 1
            else:
                raise

httpd = start_server()
print(f"Sirviendo en http://localhost:{PORT}")

def open_browser():
    webbrowser.open(f"http://localhost:{PORT}/viewer/index.html")

threading.Timer(1.0, open_browser).start()

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServidor detenido.")
    httpd.server_close()