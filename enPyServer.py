import socket
import threading
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QObject, pyqtSignal


# 定义服务器类，继承自 QObject 以支持信号和槽机制
class Server(QObject):
    # 定义信号，当接收到消息时触发，传递一个字符串参数
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()  # 调用父类的构造函数

        # 创建服务器套接字（socket.AF_INET 表示 IPv4，socket.SOCK_STREAM 表示 TCP 连接）
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 绑定服务器到 0.0.0.0（允许所有设备访问），端口 5555
        self.server_socket.bind(("0.0.0.0", 5555))
        # 开始监听，最多允许 5 个客户端等待连接
        self.server_socket.listen(5)
        # 存储已连接的客户端套接字
        self.clients = []

    # 服务器主循环，接受新的客户端连接
    def start_server(self):
        while True:
            client_socket, addr = self.server_socket.accept()  # 接受客户端连接
            self.clients.append(client_socket)  # 将新客户端添加到列表

            # 启动新线程来接收该客户端的消息
            threading.Thread(target=self.receive_messages, args=(client_socket,)).start()

    # 处理客户端消息的线程方法
    def receive_messages(self, client_socket):
        while True:
            try:
                # 接收最多 1024 字节的数据
                data = client_socket.recv(1024)
                if not data:
                    break  # 如果数据为空，退出循环

                # 解码消息并通过信号传递给 UI 线程
                message = data.decode("utf-8")
                self.message_received.emit(message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    # 服务器向所有已连接的客户端发送消息
    def send_message(self, message):
        for client in self.clients:
            try:
                client.send(message.encode("utf-8"))
            except Exception as e:
                print(f"广播错误: {e}")


# 定义服务器 GUI 界面类，继承自 QWidget
class ServerApp(QWidget):
    def __init__(self):
        super().__init__()  # 调用父类构造函数
        self.server = Server()  # 创建 Server 实例

        # 绑定信号 message_received 到处理消息的方法
        self.server.message_received.connect(self.handle_message)

        # 设置窗口属性
        self.resize(1000, 600)
        self.move(750, 500)
        self.setWindowTitle("服务器")

        # 创建一个标签，用于显示接收到的消息
        self.label = QLabel("系统正在运行", self)
        self.label.setAlignment(Qt.AlignCenter)  # 居中对齐

        # 启动服务器线程，使其能够接受客户端连接
        threading.Thread(target=self.server.start_server).start()

    # 处理接收到的消息（更新 UI 并打印到控制台）
    def handle_message(self, message):
        print(f"Received message: {message}")
        self.label.setText(message)  # 更新标签文本


# 主程序入口
if __name__ == "__main__":
    app = QApplication([])  # 创建 PyQt5 应用
    server_app = ServerApp()  # 创建服务器窗口
    server_app.show()  # 显示窗口
    app.exec_()  # 运行事件循环
