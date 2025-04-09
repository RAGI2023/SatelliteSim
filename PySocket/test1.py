import socket
import select

HOST = '0.0.0.0'
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"服务器已启动，监听端口 {PORT}...")

clients = {}       # {client_socket: client_id}
client_ids = {}    # {client_id: client_socket}

while True:
    # 监听 server_socket 和所有客户端 socket
    read_sockets, _, _ = select.select([server_socket] + list(clients.keys()), [], [])

    for sock in read_sockets:
        if sock == server_socket:
            # 有新客户端连接
            client_socket, addr = server_socket.accept()
            print(f"新客户端连接来自 {addr}")

            try:
                client_socket.send("请输入你的ID：".encode())
                client_id = client_socket.recv(1024).decode().strip()

                if client_id in client_ids:
                    client_socket.send(f"ID '{client_id}' 已被使用，请重连".encode())
                    client_socket.close()
                else:
                    clients[client_socket] = client_id
                    client_ids[client_id] = client_socket
                    print(f"客户端ID: {client_id} 注册成功")
                    client_socket.send(f"注册成功，你的ID是：{client_id}".encode())
            except Exception as e:
                print("注册出错：", e)
                client_socket.close()
        else:
            try:
                msg = sock.recv(1024)
                if not msg:
                    raise Exception("客户端断开连接")
                msg = msg.decode().strip()

                if msg.startswith("TO:"):
                    try:
                        target_info, content = msg[3:].split("|", 1)
                        target_id = target_info.strip()
                        sender_id = clients[sock]

                        if target_id in client_ids:
                            target_socket = client_ids[target_id]
                            forward_msg = f"[{sender_id} ➜ 你]：{content}"
                            target_socket.send(forward_msg.encode())
                            sock.send(f"[你 ➜ {target_id}]：{content}".encode())
                        else:
                            sock.send(f"❌ 目标客户端 '{target_id}' 不在线或不存在".encode())
                    except ValueError:
                        sock.send("❗ 格式错误，应为 TO:<目标ID>|<内容>".encode())
                else:
                    sock.send("❗ 发送格式应为 TO:<目标ID>|<内容>".encode())
            except:
                # 断开连接清理
                client_id = clients.get(sock, "未知")
                print(f"客户端 {client_id} 断开连接")
                if sock in clients:
                    del client_ids[clients[sock]]
                    del clients[sock]
                sock.close()
