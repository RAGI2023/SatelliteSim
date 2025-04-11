import socket
import threading
from datetime import datetime
#from PyQt5.QtCore import Qt, QObject, pyqtSignal
server_on = 1
i = 1#测试用
#1.创建服务器类;2.启动服务器
class Server:
    #message_received = pyqtSignal(str)
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
                global i#测试用
                data = client_socket.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                # #实验协议   1为转发请求
                message1 = message[0:7]
                message2 = message[7:len(message)]
                print(f"客户端发送:{message} (from {addr})")
                client_socket.send(f"服务器已收到{i}".encode("utf-8"));i+=1
                if(message == 'quit' ):
                    self.socket.close()
                    return 0
                if(message1 == 'encode@'):
                    client_socket.send(str(('utf-8 encode result:'+ message2)).encode("utf-8"))

            except Exception as g:
                print(f"处理客户端{addr}请求时出错: {g}")
                break

        client_socket.close()
        print(f"客户端{addr}连接关闭")
        print(datetime.now())
        print('********************************************************************')
        return 1

    '''
    def send_message_to_target(self,message,host='127.0.0.1',port=54321):
        try:
            # 创建一个新的 TCP 套接字
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 连接到目标地址和端口
            target_socket.connect((host,port))
            # 发送消息
            target_socket.send(message)
            print(f"已向 {54321} 发送消息: {message}")
        except Exception as e:
            print(f"向 {54321} 发送消息时发生错误: {e}")
        finally:
            target_socket.close()
    '''

    def start(self):
        global server_on
        try:
            while server_on:
                client_socket, addr = self.socket.accept()
                #client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                #client_thread.start()
                server_on = self.handle_client(client_socket,addr)
        except KeyboardInterrupt:
            self.socket.close()
            print("服务器已经关")
        finally:
            self.socket.close()
            print("服务器已经关闭")

if __name__ == "__main__":
    # 启动服务器
    server = Server(host='0.0.0.0',port=12345)
    #server_thread = threading.Thread(target=server.start,daemon=True)
    #server_thread.start()
    #server_thread.join()
    server.start()
    '''
    # 启动客户端并发送消息
    client = Client()
    client.send_message("潘大海")
    client.send_message("请求关闭")
    '''
#next step:如何优雅的关闭服务器进程；如何封装server_thread_start部分；多线程;