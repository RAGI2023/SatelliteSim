import socket
#1. 创建Client类;2.发送message
class Client:
    def __init__(self, host="127.0.0.1", port=12345):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

    def send_message(self, message):
        self.client_socket.send(message.encode("utf-8"))
        response = self.client_socket.recv(1024)
        print(f"服务器回复: {response.decode('utf-8')}")


if __name__ == "__main__":

    # 启动客户端并发送消息
    # 默认为本机地址，可以指定，关键字host,port
    client = Client("127.0.0.1", 12345)
    client.send_message("222")
    client.send_message("333")
    client.send_message('请求关闭')
    while 1:
         message = input('输入你要发送的信息:')
         client.send_message(message)
         if(message == 'quit'):
            client.client_socket.close()
            break