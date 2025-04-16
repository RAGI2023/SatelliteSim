import socket
import bpsk
import numpy as np

#初始化(.socket创建socket对象→.bind绑定端口号)+工作(.listen监听→.accept接收到→.recv读取数据)
#PS:主机.accept接受信号并返回一个元组,含有两个元素.一个是专门与客户端通信的socket,一个是客户端的地址.利用.recv读取收取到的信息

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 12345))

while True:
    try:
        server_socket.listen(5)
        print("监听端口 12345...")

        client_socket, addr = server_socket.accept()
        print(f"客户端地址: {addr}")

        data = client_socket.recv(10240)
        if not data:
            break
        #print(f"UTF-8 解码: {data.decode('utf-8')}")
        #print(f"GBK 解码: {data.decode('gbk')}")
        #************对输入信息的处理**********************************
        '''
        if data.decode('utf-8') == 'quit':
            client_socket.close()
            server_socket.close()
            break
        '''
        data = np.frombuffer(data, dtype=np.float64);print(data)#将接受的字节流转换成float64变量
        if data[0] == 1 and data[1] == 2:
            data = data[2:]
            data = bpsk.bpsk_modulate(data);print(data)#处理
            data = data.T.reshape(-1)#变为一维数组
            message = data.tobytes()#将float64转换为字节流（准备发送
            client_socket.send(message)#发送
        if data[0] == 3 and data[1] ==4:
            data = data[2:]
            data = bpsk.bpsk_demodulate(data);print(data)
            data = np.array(data,dtype=np.float64)
            message = data.tobytes()
            client_socket.send(message)
        if data[0] == 999 and data[1] == 999:
            server_socket.close()
            client_socket.close()
            break


        #************发送处理结果*************************************


    except Exception as g:
        if g == KeyboardInterrupt:
            client_socket.close()
        print(f"Error receiving message: {g}")
        break
#****************************************************************
#next step:class封装 + 多线程工作
