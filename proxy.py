from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import sys

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.on_request("get")

    def do_HEAD(self):
        self.on_request("head")

    def do_DELETE(self):
        self.on_request("delete")

    def do_PUT(self):
        _data = self.rfile.read(int(self.headers['Content-Length']))
        self.on_request("put", _data)

    def do_POST(self):
        _data = self.rfile.read(int(self.headers['Content-Length']))
        self.on_request("post", _data)
       
    def on_request(self, method, data=None):
        method = method.upper()
        _headers = {key: value for key, value in self.headers.items()}
        _headers['Host'] = 'api.openai.com'
        _headers['Connection'] = 'close'
        try:
            _url = "https://api.openai.com%s" % self.path
            print("Redirecting %s request to: %s" % (method, _url))
            if method == "GET":
                _response = requests.get(_url, headers=_headers, proxies={"https": sys.argv[2]})
            elif method == "HEAD":
                _response = requests.head(_url, headers=_headers, proxies={"https": sys.argv[2]})
            elif method == "DELETE":
                _response = requests.delete(_url, headers=_headers, proxies={"https": sys.argv[2]})
            elif method == "PUT":
                _response = requests.put(_url, data=data, headers=_headers, proxies={"https": sys.argv[2]})
            elif method == "POST":
                _response = requests.post(_url, data=data, headers=_headers, proxies={"https": sys.argv[2]})
            else:
                self.send_response(405)
                self.connection.close()
                return

            self.send_response(_response.status_code)
            for header, value in _response.headers.items():
                if header.lower() == "transfer-encoding" and value.lower() == "chunked":
                    continue
                self.send_header(header, value)
            self.end_headers()
            #print(_response.content)
            self.wfile.write(_response.content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Internal Server Error: {e}".encode())
        finally:
            self.connection.close()
    
def is_port(port):
    try:
        _port = int(port)
        return _port > 0 and _port < 65536
    except:
        return False

def is_proxy(proxy):
    _nodes = proxy.split("://")
    if len(_nodes) != 2:
        return False
    _nodes[0] = _nodes[0].lower()
    if not _nodes[0] == 'http' and not _nodes[0] == 'socks4' and not _nodes[0] == 'socks5':
        return False
    _nodes = _nodes[1].split(":")
    if len(_nodes) != 2:
        return False
    if not is_port(_nodes[1]):
        return False
    _nodes = _nodes[0].split(".")
    if len(_nodes) != 4:
        return False
    try:
        for _node in _nodes:
            _node = int(_node)
            if _node < 0 or _node > 255:
                return False
        return True
    except:
        return False

def main():
    if len(sys.argv) < 3 or not is_port(sys.argv[1]) or not is_proxy(sys.argv[2]):
        print("Usage: python %s <port> <proxy>")
        print("Simples:")
        print("\tpython %s 1234 http://127.0.0.1:2345")
        print("\tpython %s 1234 socks4://127.0.0.1:2345")
        print("\tpython %s 1234 socks5://127.0.0.1:2345")
        return
    _server = HTTPServer(('', int(sys.argv[1])), ProxyHTTPRequestHandler)
    print('Starting chatgpt api proxy server on 0.0.0.0:%s...' % sys.argv[1])
    print('proxy server:%s...' % sys.argv[2])
    _server.serve_forever()

if __name__ == "__main__":
    main()
