import socket
import threading

class socket_client:
    def __init__(self, host='127.0.0.1', port=12345, on_message=None):
        """
        :param host: 服务器IP地址
        :param port: 服务器端口号
        :param on_message: 接收到消息时的回调函数（参数为消息字符串）
        """
        self.host = host
        self.port = port
        self.on_message = on_message
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

    def connect(self):
        """连接到服务器并启动接收线程"""
        try:
            self.client_socket.connect((self.host, self.port))
            self.running = True
            threading.Thread(target=self.receive_messages, daemon=True).start()
            print(f"[Client] 连接成功 {self.host}:{self.port}")
        except Exception as e:
            print(f"[Client] 连接失败: {e}")

    def send_message(self, message):
        """发送消息到服务器"""
        try:
            self.client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"[Client] 发送失败: {e}")

    def receive_messages(self):
        """循环接收消息"""
        while self.running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    print("[Client] 服务器关闭连接")
                    break
                message = data.decode('utf-8')
                if self.on_message:
                    self.on_message(message)
                else:
                    print(f"[Client] 收到消息: {message}")
            except Exception as e:
                print(f"[Client] 接收失败: {e}")
                break
        self.running = False
        self.client_socket.close()

    def close(self):
        """关闭连接"""
        self.running = False
        try:
            self.client_socket.close()
            print("[Client] 连接已关闭")
        except Exception as e:
            print(f"[Client] 关闭异常: {e}")
