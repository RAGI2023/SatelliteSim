import socket
#1. 创建Client类;2.发送message
class Client:
    def __init__(self, host="10.21.183.174", port=12345):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def send_message(self, message):
        self.socket.send(message.encode("utf-8"))
        response = self.socket.recv(1024)
        print(f"服务器回复: {response.decode('utf-8')}")


if __name__ == "__main__":

    # 启动客户端并发送消息
    # 默认为本机地址，可以指定，关键字host,port
    client = Client()
    client.send_message("111")
    client.send_message("222")
    client.send_message("333")
    #client.send_message('请求关闭')
    while 1:
        message = input('输入你要发送的信息')
        if(message == 'q'):
            client.send_message(message)
            break
    client.socket.close()

