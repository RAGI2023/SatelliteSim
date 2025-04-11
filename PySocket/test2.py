import socket
import threading

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024)
            if msg:
                print(f"\n📩 {msg.decode()}\n> ", end="")
            else:
                print("服务器断开连接。")
                break
        except:
            break

HOST = '127.0.0.1'
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# 获取欢迎信息和注册
server_prompt = client_socket.recv(1024).decode()
print(server_prompt)
client_id = input("> ")
client_socket.send(client_id.encode())

# 注册结果
print(client_socket.recv(1024).decode())

# 启动接收线程
threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

# 主线程负责发送消息
print("\n请输入消息（格式：TO:<目标ID>|<内容>）：")

while True:
    msg = input("> ")
    if msg.lower() in ['exit', 'quit']:
        break
    client_socket.send(msg.encode())

client_socket.close()
print("已断开连接。")
