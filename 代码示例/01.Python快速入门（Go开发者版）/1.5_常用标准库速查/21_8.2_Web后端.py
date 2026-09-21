"""简单的HTTP服务器 - 对比Go的net/http"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        
        response = {"message": "Hello from Python"}
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)
        
        # 处理数据...
        
        self.send_response(201)
        self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(("", 8000), Handler)
    print("Server running on port 8000...")
    server.serve_forever()
