# threading:创建线程,使得客户端同时接受和发送消息
import socket
import threading
from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QObject, pyqtSignal

# 定义客户端类型类
class Client(QObject):  # Client继承自QObject,主要是为了signal/slot系统
    # *****************************这是什么信号,有什么用,和第36行的联系.和self.message_received差不多但是不一样
#-------------------------------------------------------------------------------------------------------
    message_received = pyqtSignal(str)
#-------------------------------------------------------------------------------------------------------
    # __init__是创建class时候自动执行的,第一个参数始终是self(可额外增加参数)
    def __init__(self):
        super().__init__()  # 直接继承父类QObject的属性,下面self.client_socket为一个socket对象
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("localhost", 5555))
        # *****************这里localhost能直接实现?不需要写具体的地址?电脑可以自动解析

    # 发送消息;带一个参数→发送的消息
    def send_message(self, message):
        self.client_socket.send(message.encode("utf-8"))
        data = self.client_socket.recv(1024)
        print(f'The server replies:{data.decode('utf-8')}')

    # 接受消息:不带参数
    def receive_messages(self):
        while True:
            try:
                # .recv方法接收
                # ********************和之前的理解有偏差不需要用.accept: 因为是客户端,客户端与服务器的使用不同
                data = self.client_socket.recv(1024)
                if not data:
                    break
                # data.decode破译
                message = data.decode("utf-8")
#------------------------------------------------------------------------------------------------------
                self.message_received.emit(message)  # 联系上面的第10行
#------------------------------------------------------------------------------------------------------
            except Exception as e:
                # 发生异常时打印错误信息，并退出循环
                print(f"发生错误: {e}")
                break


# 定义客户端应用程序窗口类
class ClientApp(QWidget):
    def __init__(self):
        super().__init__()
#------------------------------------------------------------------------------------------------------
        self.client = Client()
#------------------------------------------------------------------------------------------------------
        # 属性:window的
        '''
         本次使用.resize和move分别设置
        self.setGeometry(600, 300, 300, 200)
        '''

        self.resize(1500, 750)
        self.move(300, 300)
        self.setWindowTitle("客户端")
#------------------------------------------------------------------------------------------------------
        self.client.message_received.connect(self.handle_message)
#------------------------------------------------------------------------------------------------------
        # 属性:message_input
        self.message_input = QLineEdit(self)  # QLineEdit:单行文本输入框
        self.message_input.resize(300,50)
        self.message_input.move(750,200)

        # 属性:按键
        self.send_button = QPushButton("发送", self)
        self.send_button.resize(300, 300)
        self.send_button.move(750, 400)
        self.send_button.clicked.connect(self.send_message)

        # 布局
        '''
        本代码使用手动布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)
        '''

        # 多线程工作
        #self.thread = threading.Thread(target=self.client.receive_messages)
        #self.thread.start()


    def send_message(self):
        message = self.message_input.text()
        self.client.send_message(message)

    def handle_message(self, message):
        print(f"接收到的信息: {message}")


#测试用例
if __name__ == "__main__":
    app = QApplication([])
    client_app = ClientApp()
    client_app.show()
    app.exec_()