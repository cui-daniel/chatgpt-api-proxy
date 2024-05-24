# chatgpt-api-proxy
ChatGPT API 接口代理

python proxy.py 监听端口 代理地址（当前只支持http代理）

比如 python proxy.py 8001 127.0.0.1:8080
现在访问http://127.0.0.1:8001/v1 就会通过 127.0.0.1:8080 代理把请求转发到 https://api.openai.com/v1
