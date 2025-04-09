import socket
import threading
from datetime import datetime
from PyQt5.QtCore import Qt, QObject, pyqtSignal

#1.创建服务器类;2.启动服务器
class Server:
    message_received = pyqtSignal(str)
    def __init__(self, host="0.0.0.0", port=12345):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
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
                if(message == 'q' ):
                    self.socket.close()
                    return 0

            except Exception as g:
                print(f"处理客户端{addr}请求时出错: {g}")
                break

        client_socket.close()
        print(f"客户端{addr}连接关闭")
        print(datetime.now())
        print('********************************************************************')
        return 1

    def start(self):
        server_on = 1
        try:
            while server_on:
                client_socket, addr = self.socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                client_thread.start()
                server_on = self.handle_client(client_socket,addr)
        except KeyboardInterrupt:
            self.socket.close()
            print("服务器已经关闭")

class Client:
    message_received = pyqtSignal(str)
    def __init__(self, host="10.21.183.174", port=12345):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def send_message(self, message):
        self.socket.send(message.encode("utf-8"))
        #response = self.socket.recv(1024)
        #print(f"服务器回复: {response.decode('utf-8')}")

if __name__ == "__main__":
    # 启动服务器
    server = Server(host='0.0.0.0',port=12345)
    #server_thread = threading.Thread(target=server.start,daemon=True)
    #server_thread.start()
    server.start()
    '''
    # 启动客户端并发送消息
    client = Client()
    client.send_message("潘大海")
    client.send_message("请求关闭")
    '''
#next step:如何优雅的关闭服务器进程；如何封装server_thread_start部分；多线程;