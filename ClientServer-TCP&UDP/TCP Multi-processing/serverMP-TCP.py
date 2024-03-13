'''9.	Сервер хранит предметный указатель, каждая компонента которого содержит слово и
номера страниц, где это слово встречается. Количество номеров страниц, относящихся к одному
слову, от одного до десяти. Клиент имеет возможность формирования указателя с клавиатуры и
из файла, вывода указателя, вывода номеров страниц для заданного слова, удаления элемента из
указателя. Программа клиента должна содержать меню, позволяющее осуществлять указанные действия на сервере. '''

import socket, multiprocessing
from os import stat
from multiprocessing import Process
PORT = 33334

def client_service(c, addr, id):
    while True:
        data = c.recv(1024)
        if not data:
            break
        data = data.decode()
        if data == '1':
            c.send(bytes('0', 'utf-8'))
            print(f'Sent to client {id}: 0')
            sec_data = c.recv(1024).decode().split('\n')
            sec_data = [item.split('\t') for item in sec_data]
            to_write = list()
            if stat('ServerData.txt').st_size == 0:
                to_write = sec_data
            else:
                for val in sec_data:
                    found = False
                    with open('ServerData.txt', 'r', encoding='utf-8') as file:
                        for buf in file:
                            buf = buf.replace('\n', '').split('\t')
                            if val[0] == buf[0]:
                                found = True
                                break
                        if not found:
                            to_write.append(val)
            if len(to_write) != 0:
                with open('ServerData.txt', 'a', encoding='utf-8') as file:
                    to_write = '\n'.join(['\t'.join(item) for item in to_write])
                    file.write('\n' + to_write)
            answer = '0' if len(to_write) != 0 else '1'
            c.send(bytes(answer, 'utf-8'))
            print(f'Sent to client {id}: {answer}')
        elif data == '2':
            with open('ServerData.txt', 'r', encoding='utf-8') as file:
                line = ''.join([item for item in file])
                answer = line if len(line) != 0 else '0'
                c.send(bytes(answer, 'utf-8'))
                print(f'Sent to client {id} {len(answer)} bytes')
        elif data == '3':
            c.send(bytes('0', 'utf-8'))
            print(f'Sent to client {id}: 0')
            line = c.recv(1024).decode()
            found = False
            with open('ServerData.txt', 'r', encoding='utf-8') as file:
                for buf in file:
                    if buf.split('\t')[0] == line:
                        answer = buf[len(line) + 1:].replace('\n', '')
                        c.send(bytes(answer, 'utf-8'))
                        print(f'Sent to client {id}: {answer}')
                        found = True
                        break
            if not found:
                c.send(bytes('0', 'utf-8'))
                print(f'Sent to client {id}: 0')
        elif data == '4':
            c.send(bytes('0', 'utf-8'))
            print(f'Sent to client {id}: 0')
            line = c.recv(1024).decode()
            to_write = list()
            found = False
            with open('ServerData.txt', 'r', encoding='utf-8') as file:
                for buf in file:
                    if not found and line == buf.split('\t')[0]:
                        found = True
                        continue
                    to_write.append(buf.replace('\n', ''))
            with open('ServerData.txt', 'w', encoding='utf-8') as file:
                file.write('\n'.join(to_write))
            answer = '0' if found else '1'
            c.send(bytes(answer, 'utf-8'))
            print(f'Sent to client {id}: {answer}')
        print(f'Done command {data} for client {id} ({addr[0]}:{addr[1]})')
    c.close()
    print(f'Client {id} disconnected ({addr[0]}:{addr[1]})')

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', PORT))
        s.listen(1)
        id = 1
        print('Server is running')
        while True:
            print(len(multiprocessing.active_children()), 'active client(s)')
            c, addr = s.accept()
            p = Process(target=client_service, args=(c, addr, id))
            p.daemon = True
            p.start()
            print(f'Client {id} connected ({addr[0]}:{addr[1]})')
            id += 1
        s.close()