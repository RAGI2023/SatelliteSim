import socket
import threading
from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QWidget, QPlainTextEdit
from PyQt5.QtCore import Qt, QObject, pyqtSignal

class Client(QObject):
    message_received = pyqtSignal(str)

    def __init__(self,host='127.0.0.1',port=12345):
        super().__init__()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host,port))

    def send_message(self, message):
        self.client_socket.send(message.encode("utf-8"))

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                message = data.decode("utf-8")
                self.message_received.emit(message)
            except Exception as e:
                print(f"发生错误: {e}")
                break

class ClientApp(QWidget):
    def __init__(self):
        #继承和增加属性
        super().__init__()
        self.client = Client(host="10.21.183.174", port=12345)
        #画窗口
        self.resize(1500, 750)
        self.move(300, 300)
        self.setWindowTitle("客户端")
        self.client.message_received.connect(self.handle_message)
        self.message_input = QLineEdit(self)
        self.message_input.resize(300, 50)
        self.message_input.move(500, 200)
        self.message_output = QLineEdit(self)
        self.message_output.resize(600, 50)
        self.message_output.move(1000, 200)
        self.send_button = QPushButton("send", self)
        self.send_button.resize(150, 150)
        self.send_button.move(500, 400)
        self.send_button.clicked.connect(self.send_message)
        self.send_button = QPushButton("shutdown", self)
        self.send_button.resize(150, 150)
        self.send_button.move(1000, 400)
        self.send_button.clicked.connect(self.shutdown)

        # 多线程工作
        self.thread = threading.Thread(target=self.client.receive_messages,daemon=True)
        self.thread.start()

    def send_message(self):
        message = self.message_input.text()
        self.client.send_message(message)

    def handle_message(self, message):
        self.message_output.setText('@'+message)
        print(type(message))
        print(f"接收到的信息: {message}")

    def shutdown(self):
        print('正在退出')
        self.client.client_socket.close()
        print('客户端套接字已释放')
        self.close()
        print('窗口已关闭')

if __name__ == "__main__":
    app = QApplication([])
    client_app = ClientApp()
    client_app.show()
    app.exec_()
