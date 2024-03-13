import socket

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        line = input('Enter string to refactor (0 - exit):\n')
        if line == '0':
            break
        s.sendall(bytes(line, 'utf-8'))
        data = s.recv(1024)
        print(f'Server answered:\n{data.decode()}')
    s.close()
input('Client shutting down')