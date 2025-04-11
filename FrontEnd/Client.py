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

# def main():
