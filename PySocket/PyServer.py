import socket

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

        data = client_socket.recv(1024)
        if not data:
            break
        print(f"UTF-8 解码: {data.decode('utf-8')}")
        #print(f"GBK 解码: {data.decode('gbk')}")
        #************对输入信息的处理**********************************
        if(data.decode('utf-8') == '请求关闭'):
            client_socket.close()
            server_socket.close()
            break
        #************发送处理结果*************************************
        message = "服务器已收到"
        client_socket.send(message.encode('utf-8'))

    except Exception as g:
        print(f"Error receiving message: {g}")
        break
#****************************************************************
#next step:class封装 + 多线程工作
