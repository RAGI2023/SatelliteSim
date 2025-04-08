import socket
import threading
from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QWidget
from PyQt5.QtCore import QObject, pyqtSignal


# 定义客户端类，继承自QObject，以支持信号和槽机制
class Client(QObject):
    # 定义信号，当接收到消息时触发，传递一个字符串参数
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()  # 调用父类的构造函数

        # 创建客户端套接字（socket.AF_INET 表示 IPv4，socket.SOCK_STREAM 表示 TCP 连接）
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 连接到服务器，地址为 localhost，端口号 5555
        # 在本地运行服务器时，可以使用 "localhost" 作为地址
        self.client_socket.connect(("localhost", 5555))

    # 发送消息的方法，参数 message 是要发送的字符串
    def send_message(self, message):
        self.client_socket.send(message.encode("utf-8"))  # 发送 UTF-8 编码的消息

    # 接收消息的方法，持续监听服务器发送的数据
    def receive_messages(self):
        while True:
            try:
                # 接收最多 1024 字节的数据
                data = self.client_socket.recv(1024)
                if not data:
                    break  # 如果数据为空，则跳出循环

                # 解码收到的字节数据，并通过信号传递给 UI 线程
                message = data.decode("utf-8")
                self.message_received.emit(message)
            except Exception as e:
                print(f"发生错误: {e}")
                break


# 定义客户端 GUI 界面类，继承自 QWidget
class ClientApp(QWidget):
    def __init__(self):
        super().__init__()  # 调用父类构造函数
        self.client = Client()  # 创建 Client 实例

        # 设置窗口属性
        self.resize(600, 300)
        self.move(300, 300)
        self.setWindowTitle("客户端")

        # 绑定信号 message_received 到处理消息的方法
        self.client.message_received.connect(self.handle_message)

        # 创建单行文本输入框，用于输入消息
        self.message_input = QLineEdit(self)
        self.message_input.resize(300, 100)
        self.message_input.move(300, 100)

        # 创建发送按钮，并绑定点击事件
        self.send_button = QPushButton("发送", self)
        self.send_button.resize(100, 100)
        self.send_button.move(300, 200)
        self.send_button.clicked.connect(self.send_message)  # 点击按钮时调用 send_message 方法

        # 启动接收消息的线程，使客户端能够同时发送和接收消息
        self.thread = threading.Thread(target=self.client.receive_messages)
        self.thread.start()

    # 发送消息的槽函数，从输入框获取消息并调用 Client 的 send_message 方法
    def send_message(self):
        message = self.message_input.text()
        self.client.send_message(message)

    # 处理接收到的消息（此处仅打印到控制台）
    def handle_message(self, message):
        print(f"接收到的信息: {message}")


# 主程序入口
if __name__ == "__main__":
    app = QApplication([])  # 创建 PyQt5 应用
    client_app = ClientApp()  # 创建客户端窗口
    client_app.show()  # 显示窗口
    app.exec_()  # 运行事件循环
