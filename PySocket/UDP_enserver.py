import socket
import threading
server_on = 1
i = 1
class UDPServer:
    def __init__(self, host='0.0.0.0', port=12346):
        self.server_address = (host, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(self.server_address)
        print(f"服务器已启动，监听 {self.server_address}")

    def start(self):
        global i,server_on
        while server_on:
            try:
                data, client_addr = self.server_socket.recvfrom(1024)
                message = data.decode('utf-8')
                print(f"收到来自 {client_addr} 的消息: {message}")

                # 回发消息（可修改为其他逻辑）
                response = f"服务器收到第{i}条: {message}";i+=1
                self.server_socket.sendto(response.encode('utf-8'), client_addr)
                if(message == 'quit'):
                    self.server_socket.close()
                    server_on = 0
            except Exception as e:
                print(f"发生错误: {e}")
                break

    def shutdown(self):
        self.server_socket.close()
        print("服务器已关闭")


if __name__ == "__main__":
    server = UDPServer(host='0.0.0.0', port=12346)
    try:
        server.start()
    except KeyboardInterrupt:
        server.shutdown()
