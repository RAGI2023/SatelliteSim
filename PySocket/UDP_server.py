import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_socket.bind(('0.0.0.0', 12346));print(f"正在监听{server_address}")

data, client_address = server_socket.recvfrom(1024)
message = data.decode('utf-8');print(f"收到来自 {client_address} 的消息: {message}")

server_socket.close()