import socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.sendto('heloworld'.encode('utf-8'), ('10.21.183.174', 12346));print('send successfully')
client_socket.close();print('client_socket has been released')
