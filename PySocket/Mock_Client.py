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
        client.client_socket.close()


if __name__ == "__main__":

    # 启动客户端并发送消息
    client = Client()
    client.send_message("潘大海")

