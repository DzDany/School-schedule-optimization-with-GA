import http.server
import socketserver
import webbrowser
import os
import threading

PORT = 8000

# Go to the parent directory to serve both data and viewer
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

Handler = http.server.SimpleHTTPRequestHandler

def start_server():
    global PORT
    while True:
        try:
            httpd = socketserver.TCPServer(("", PORT), Handler)
            return httpd
        except OSError as e:
            if e.winerror == 10048 or e.errno == 98: # Address already in use
                PORT += 1
            else:
                raise

httpd = start_server()
print(f"Sirviendo en http://localhost:{PORT}")
print("El navegador se abrirá automáticamente...")

# Abrir el navegador en un hilo separado
def open_browser():
    webbrowser.open(f"http://localhost:{PORT}/viewer/index.html")
    
threading.Timer(1.0, open_browser).start()

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServidor detenido.")
    httpd.server_close()
