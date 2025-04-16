import socket
import bpsk
import numpy as np

#接受的信息，用于测试
data = np.array([0,1,0,1],dtype=np.float64)
data = bpsk.bpsk_modulate(data)
data = data[:,1]
sign = np.array([999,999],dtype=np.float64)
message = np.concatenate((sign,data))
message = message.tobytes()
print('发送的信息:')
print(data)
print(message)

#.connect连接→.send发送
#尚未封装
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 12345))
#************************此处更改发送的信息**************************************
client_socket.send(message)

#用于接受的服务器信息
data_received = client_socket.recv(40960)#接收到的消息：字节流
message_received = np.frombuffer(data_received, dtype=np.float64)#将字节流转换成float64
print('收到的信息:')
print(data_received)
print(message_received)
print(len(message_received))
client_socket.close()
#****************************************************************
#next step:class封装 + 多线程工作