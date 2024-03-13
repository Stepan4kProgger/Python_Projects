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

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1', 65433))
    print('Connection established')
    while True:
        answer = input('''Choose what to do
    1 - Search
    2 - Add
    3 - Edit / View
    4 - Delete / View
    0 - Exit
Your input: ''')
        if answer == '1':
            s.send(bytes('1', 'utf-8'))
            data = s.recv(1024)
            line = input('Enter manufacturer counry (0 - exit):\n')
            if line == '0':
                break
            s.send(bytes(line, 'utf-8'))
            data = s.recv(1024).decode()
            if data == '0':
                print('No information found about this country')
            else:
                print('Firm-manufacturer\tName\tAmount')
                print(data)

        elif answer == '2':
            s.send(bytes('2', 'utf-8'))
            data = s.recv(1024)
            data = list()
            print('Input country, firm, name, amount. Separated by Enter')
            for i in range(4):
                data.append(input())
            s.send(bytes('\t'.join(data), 'utf-8'))
            data = s.recv(1024).decode()
            print('Success' if data == '0' else 'Fault')

        elif answer == '3':
            s.send(bytes('3', 'utf-8'))
            data = s.recv(1024).decode().split('\n')
            for i in range(len(data)):
                print(i + 1, data[i])
            answer = input('Which field to edit? (0 - skip): ')
            if 0 < int(answer) <= len(data):
                s.send(bytes(answer, 'utf-8'))
                data = s.recv(1024)
                data = list()
                print('Input country, firm, name, amount. Separated by Enter')
                for i in range(4):
                    data.append(input())
                s.send(bytes('\t'.join(data), 'utf-8'))
                data = s.recv(1024).decode()
                print('Success' if data == '0' else 'Fault')
            else:
                s.send(bytes('0', 'utf-8'))
                data = s.recv(1024)

        elif answer == '4':
            s.send(bytes('4', 'utf-8'))
            data = s.recv(1024).decode().split('\n')
            for i in range(len(data)):
                print(i + 1, data[i])
            answer = input('Which field to delete? (0 - skip): ')
            if 0 < int(answer) <= len(data):
                s.send(bytes(answer, 'utf-8'))
                data = s.recv(1024)
                data = list()
                print('Input country, firm, name, amount. Separated by Enter')
                for i in range(4):
                    data.append(input())
                s.send(bytes('\t'.join(data), 'utf-8'))
                data = s.recv(1024).decode()
                print('Success' if data == '0' else 'Fault')
            else:
                s.send(bytes('0', 'utf-8'))
                data = s.recv(1024)
        elif answer == '0':
            break
    s.close()