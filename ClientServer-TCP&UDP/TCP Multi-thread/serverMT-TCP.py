'''9.	На сервере хранится список товаров, имеющихся на складе.
Каждая запись списка содержит следующую информацию о товарах:
	страна-изготовитель;
	фирма-изготовитель;
	наименование товара;
	количество единиц товара.
Таких записей должно быть не менее пяти.
Клиент посылает на сервер страну-изготовитель. Назад он получает товары и их данные для указанной страны.
'''
import socket
from threading import Thread

client_amount = 0
SERVER_DATA = [['Belarus',	'Horizont',	'TV',	'14'],
['China',	'Geely',	'Usual car',	'3'],
['China',	'Digma',	'Tablet',	'412'],
['USA',	'Apple',	'Iphone',	'9821'],
['Russia',	'RostSelMash',	'Combine-harvester',	'7'],
['Russia',	'Baikal',	'CPU',	'2'],
['Russia',	'Moskvich',	'Chineese electric car',	'0'],
['Belarus',	'BelAZ',	'BelAZ',	'3']]

def client_service(c, addr, num):
    global client_amount, SERVER_DATA
    while True:
        data = c.recv(1024)
        if not data:
            break
        data = data.decode()
        print('Processing command', data, 'for client', num)
        if data == '1':
            c.send(bytes('0', 'utf-8'))
            print('Sent 1 byte to client', num)
            data = c.recv(1024).decode()
            print('Received', len(data), 'bytes from client', num)
            answer = str()
            for item in SERVER_DATA:
                answer += '\t'.join(item[1:]) + '\n' if item[0] == data else ''
            answer = answer[:-1] if answer != '' else '0'
            c.send(bytes(answer, 'utf-8'))
            print('Sent', len(answer), 'bytes back to client', num)
        elif data == '2':
            c.send(bytes('0', 'utf-8'))
            print('Sent 1 byte to client', num)
            data = c.recv(1024).decode()
            print('Received', len(data), 'bytes from client', num)
            SERVER_DATA.append(data.split('\t'))
            c.send(bytes('0', 'utf-8'))
            print('Sent 1 byte to client', num)
        elif data == '3':
            answer = '\n'.join(['\t'.join(item) for item in SERVER_DATA])
            c.send(bytes(answer, 'utf-8'))
            print('Sent', len(answer), 'bytes to client', num)
            field = c.recv(1024).decode()
            print('Received', len(field), 'byte(s) from client', num)
            field = int(field) - 1
            c.send(bytes('0', 'utf-8'))
            print('Sent 1 byte to client', num)
            if field != -1:
                data = c.recv(1024).decode()
                print('Received', len(data), 'bytes from client', num)
                SERVER_DATA[field] = data.split('\t')
                c.send(bytes('0', 'utf-8'))
                print('Sent 1 byte to client', num)
        elif data == '4':
            answer = '\n'.join(['\t'.join(item) for item in SERVER_DATA])
            c.send(bytes(answer, 'utf-8'))
            print('Sent', len(answer), 'bytes to client', num)
            field = c.recv(1024).decode()
            print('Received', len(field), 'byte(s) from client', num)
            field = int(field) - 1
            c.send(bytes('0', 'utf-8'))
            print('Sent 1 byte to client', num)
            if field != -1:
                SERVER_DATA.remove(SERVER_DATA[field])
                c.send(bytes('0', 'utf-8'))
                print('Sent 1 byte to client', num)
    c.close()
    print(f'Client {num} disconnected')
    client_amount -= 1
    print(f'{client_amount} active client(s) now')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('127.0.0.1', 65433))
    s.listen(5)
    count = 0
    clients = list()
    print('Server is running')
    while True:
        clients = [item if item.is_alive() else None for item in clients]
        while None in clients:
            clients.remove(None)

        print(f'{client_amount} active client(s) now')
        c, addr = s.accept()
        client_amount += 1
        count = count + 1
        t = Thread(target=client_service, args=(c, addr, count,))
        print(f'Connected client {count} by: {addr[0]}:{addr[1]}')
        t.start()
        clients.append(t)
    s.close()
