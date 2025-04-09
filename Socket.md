[toc]

### 初级:python实现client与server通信

##### server端

方法:

- .socket  :创建socket对象
- .bind     :绑定端口
- .listen   :监听
- .accept:接受
- .recv    :读取上一步中.accpet接受的socket对象的数据

PS:.accept和.recv具体的作用(看到主机端直接接受即可有些疑惑)

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\***********

> - **`accept` 方法**：处于监听状态(.listen)的服务器套接字调用。返回一个的元组(含有两个元素)，第一个元素是新的套接字对象，专门用于和客户端进行通信(这时主机能进行别的通信)；第二个元素是元组,包含 客户端的IP 地址和端口号。
> - **`recv` 方法**：由已建立连接的套接字对象(.accept)调用。返回值是字节类型(bytes)
>   - 对于服务器端，是 `accept` 方法返回的新套接字对象；
>   - 对于客户端，是客户端套接字对象本身。
> - 小结:服务器的工作逻辑:   .listen -> .accept -> .recv

```python
import socket

# .socket方法			 :创建 socket 对象
# socket.AF_INET      :IPv4
# socket.SOCK_STREAM  :TCP协议
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# .bind方法             :绑定主机和端口号
# 127.0.0.1            :地址(本机地址)
# 12345                :端口号(需大于 1023，避免特权端口)
server_socket.bind(("127.0.0.1", 12345))

# .listen方法           :监听连接
server_socket.listen(5)#参数为最大同时监听的数量
print("正在监听来自端口12345的信息")

#**********************************************************************
#解包:.accept方法会返回一个包含两个元素的元组
#.accept方法   		   :接受相关信息
#client_socket          :接受到消息后创建一个socket对象用于通信
client_socket, addr = server_socket.accept()
print(f"监听到来自12345端口的信息,通信地址为{addr}")#这里显示之前接受的来自的地址

#.recv                  :接收客户端发送的数据
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
data = client_socket.recv(1024)
print(f"接受到了数据,按照utf-8解码结果为: {data.decode('utf-8')}")#按照utf-8进行解码
print(f"接受到了数据,按照 gbk 解码结果为: {data.decode('gbk')}")#按照gbk进行解码

"""
#.send                  :自己发送消息(不多余:确实多余:只是为了向客户端传递信息)
message = "Hello from server"
client_socket.send(message.encode('utf-8'))
"""

# 关闭连接(测试时可手动关闭)
client_socket.close()
server_socket.close()
```

##### client端口

方法:

- .socket   :创建socket对象
- .connect:链接服务器
- .send      :发送信息

```python
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#.connect              :连接服务器
# 127.0.0.1            :地址(本机地址)
# 12345                :端口号(需大于 1023，避免特权端口)
client_socket.connect(("127.0.0.1", 12345))
message = "尹哲"
client_socket.send(message.encode('utf-8'))
'''
data = client_socket.recv(1024)
print(f"Received data: {data.decode('utf-8')}")
'''
```

PS: 在汉字的编码上gbk是双字节编码;utf-8是三(or四)字节编码;所以utf-8编码的两个汉字gbk会解码成三个,gbk编码的无法用utf-8解码

![image-20250403162521021](C:\Users\jingdaihuakai\AppData\Roaming\Typora\typora-user-images\image-20250403162521021.png)

### 进阶:pyqt5实现client与server通信

##### server端口

```python
import socket
import threading
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QObject, pyqtSignal


# 定义服务器类
class Server(QObject):
    message_received = pyqtSignal(str)

    def __init__(self):
        # 和clint端相比:少了.connect,多了bind,listen
        super().__init__()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 127.0.0.0只允许本机访问,0.0.0.0允许所有设备访问
        self.server_socket.bind(("0.0.0.0", 5555))
        self.server_socket.listen(5)
        self.clients = []  # 先定义一个空的。里面是所有的套接字

    def start_server(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            self.clients.append(client_socket)#填装套接字
            #threading.Thread(target=self.receive_messages, args=(client_socket,)).start()

    def receive_messages(self, client_socket):
        # 循环接收客户端发送的消息
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = data.decode("utf-8")
                self.message_received.emit(message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_message(self, message):
        for client in self.clients:
            try:
                client.send(message.encode("utf-8"))
            except Exception as e:
                print(f"广播错误: {e}")


# 定义服务器应用程序窗口类
class ServerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.server = Server()

        self.server.message_received.connect(self.handle_message)

        # 设置窗口属性
        self.resize(1500, 1000)
        self.move(750, 500)
        self.setWindowTitle("Server")

        # 创建用户界面元素
        self.label = QLabel("系统正在运行", self)
        self.label.setAlignment(Qt.AlignCenter)
        '''
       # 设置布局
       layout = QVBoxLayout(self)
       layout.addWidget(self.label)
        '''

        # 启动服务器
        threading.Thread(target=self.server.start_server).start()


    def handle_message(self, message):
        # 处理从客户端接收到的消息，这里简单地打印到控制台并更新 UI
        print(f"Received message: {message}")
        self.label.setText(message)

# 主程序入口
if __name__ == "__main__":
    app = QApplication([])
    server_app = ServerApp()
    server_app.show()
    app.exec_()
```



##### client端口

类:

- Client:
  - 继承QObject类: pyqtSignal
  - 创建self.client_socket类,发送接受函数: .connect, .send ,.recv
- ClientApp

```python
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
#-----------------------------------------------------------------------------------------------------
		#备用，用于发送信息后等待回执
        #data = self.client_socket.recv(1024)
        #print(f'The server replies:{data.decode('utf-8')}')
#-----------------------------------------------------------------------------------------------------
    # 接受消息:不带参数；但是接受是一个等待过程，需要while True
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
        # 属性:单行文本输入框
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
        self.thread = threading.Thread(target=self.client.receive_messages,dameon=True)
        self.thread.start()


    def send_message(self):
        message = self.message_input.text()#从文本输入框取文字
        self.client.send_message(message)

    def handle_message(self, message):
        print(f"接收到的信息: {message}")#仅仅作为展示


#测试用例
if __name__ == "__main__":
    app = QApplication([])
    client_app = ClientApp()
    client_app.show()
    app.exec_()
```

PS:

1. `    message_received = pyqtSignal(str)` 问题:类属性和实例属性

|              | 作用               | 位置              |
| ------------ | ------------------ | ----------------- |
| 类属性(方法) | 所有类共享的       | 在__init\_\_里面  |
| 实例属性     | 当前创建的类独享的 | 在__init\_\_ 前面 |

2. `pyqtSignal(str)` 的使用:

来自于`from PyQt5.QtCore import Qt, QObject, pyqtSignal` 中的pyqtSignal类

3. 关于判断客户端和服务器连接的关闭：释放资源后（代码运行结束），会自动断开连接，服务器会判定客户端关闭

4. 纯tm沙比，自己命名一个socket