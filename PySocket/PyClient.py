import socket

#.connect连接→.send发送
#尚未封装
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 12345))
#************************此处更改发送的信息**************************************
message = "请求关闭"
client_socket.send(message.encode('utf-8'))

#用于接受的服务器信息
data = client_socket.recv(1024)
print(f"{data.decode('utf-8')}")

client_socket.close()
#****************************************************************
#next step:class封装 + 多线程工作