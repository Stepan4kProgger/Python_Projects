import socket

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print('Server is running')
    while True:
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    print('Connection closed')
                    conn.close()
                    break
                data = data.decode().split()
                line = str()
                for val in data:
                    if len(val) != 0:
                        line += val + ' '
                conn.sendall(bytes(line[:len(line) - 1], 'utf-8'))