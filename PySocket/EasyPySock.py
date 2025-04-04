import socket
import threading
from datetime import datetime
#1.创建服务器类;2.启动服务器
class Server:
    def __init__(self, host="127.0.0.1", port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        print(f"服务器正在监听 {host}:{port}...")

    def handle_client(self, client_socket, addr):
        print('********************************************************************')
        print(f'与客户端{addr}建立连接')
        print(datetime.now())
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                print(f"客户端发送:{message} (from {addr})")
                client_socket.send("服务器已收到".encode("utf-8"))

            except Exception as g:
                print(f"处理客户端{addr}请求时出错: {g}")
                break

        client_socket.close()
        print(f"客户端{addr}连接关闭")
        print(datetime.now())
        print('********************************************************************')

    def start(self):
        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                client_thread.start()
        except KeyboardInterrupt:
            self.server_socket.close()
            print("服务器已经关闭")

class Client:
    def __init__(self, host="127.0.0.1", port=12345):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

    def send_message(self, message):
        self.client_socket.send(message.encode("utf-8"))
        response = self.client_socket.recv(1024)
        print(f"服务器回复: {response.decode('utf-8')}")

        if message == "请求关闭":
            self.client_socket.close()


if __name__ == "__main__":
    # 启动服务器
    server = Server()
    server_thread = threading.Thread(target=server.start,daemon=True)
    server_thread.start()
    '''
    # 启动客户端并发送消息
    client = Client()
    client.send_message("潘大海")
    client.send_message("请求关闭")
    '''
#next step:如何优雅的关闭服务器进程；如何封装server_thread_start部分