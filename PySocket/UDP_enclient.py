import socket
import threading
from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QWidget, QPlainTextEdit
from PyQt5.QtCore import Qt, QObject, pyqtSignal

class UDPClient(QObject):
    message_received = pyqtSignal(str)

    def __init__(self, server_host='127.0.0.1', server_port=12346, local_port=12347):
        super().__init__()
        self.server_address = (server_host, server_port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind(('0.0.0.0', local_port))  # 为了能接收消息，需要绑定本地端口

    def send_message(self, message):
        self.client_socket.sendto(message.encode("utf-8"), self.server_address)

    def receive_messages(self):
        while True:
            try:
                data, addr = self.client_socket.recvfrom(1024)
                message = data.decode("utf-8")
                self.message_received.emit(message)
            except Exception as e:
                print(f"发生错误: {e}")
                break

    def close(self):
        self.client_socket.close()

class UDPClientApp(QWidget):
    def __init__(self):
        super().__init__()
        self.client = UDPClient(server_host="10.21.183.174", server_port=12346)

        self.resize(1500, 750)
        self.move(300, 300)
        self.setWindowTitle("UDP 客户端")

        self.client.message_received.connect(self.handle_message)

        self.message_input = QLineEdit(self)
        self.message_input.resize(300, 50)
        self.message_input.move(500, 200)

        self.message_output = QPlainTextEdit(self)
        self.message_output.setReadOnly(True)
        self.message_output.resize(600, 50)
        self.message_output.move(1000, 200)

        self.send_button = QPushButton("Send", self)
        self.send_button.resize(150, 100)
        self.send_button.move(500, 400)
        self.send_button.clicked.connect(self.send_message)

        self.shutdown_button = QPushButton("Shutdown", self)
        self.shutdown_button.resize(150, 100)
        self.shutdown_button.move(1000, 400)
        self.shutdown_button.clicked.connect(self.shutdown)

        self.thread = threading.Thread(target=self.client.receive_messages, daemon=True)
        self.thread.start()

    def send_message(self):
        message = self.message_input.text()
        self.client.send_message(message)

    def handle_message(self, message):
        self.message_output.setText(f"{message}")
        print(f"接收到的信息: {message}")

    def shutdown(self):
        print('正在退出')
        self.client.close()
        print('客户端套接字已释放')
        self.close()
        print('窗口已关闭')

if __name__ == "__main__":
    app = QApplication([])
    client_app = UDPClientApp()
    client_app.show()
    app.exec_()
