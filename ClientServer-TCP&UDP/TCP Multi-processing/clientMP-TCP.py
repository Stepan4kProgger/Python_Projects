'''9.	Сервер хранит предметный указатель, каждая компонента которого содержит слово и
номера страниц, где это слово встречается. Количество номеров страниц, относящихся к одному
слову, от одного до десяти. Клиент имеет возможность формирования указателя с клавиатуры и
из файла, вывода указателя, вывода номеров страниц для заданного слова, удаления элемента из
указателя. Программа клиента должна содержать меню, позволяющее осуществлять указанные действия на сервере. '''

import socket
PORT = 33334
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1', PORT))
    print('Connection established')
    while True:
        answer = input(
'''Choose what to do:
    1 - Form new subject index
    2 - Display subject index list
    3 - Display pages of typed word
    4 - Delete subject from list
    0 - Exit
Your input: ''')
        if answer == '1':
            answer = input(
'''How to form new index?
    1 - From keyboard
    2 - From file (Subjects.txt)
    0 - Cancel
Input: ''')
            line = str()
            if answer == '1':
                line = input('Type the word: ')
                if line == '':
                    print('Cancelled')
                    continue
                pages = set()
                page = int(input('Type pages of this word (0 - stop): '))
                while page != 0 and len(pages) <= 10:
                    pages.add(page)
                    page = int(input('Type another page of this word (0 - stop): '))
                if len(pages) == 0:
                    print('No pages, cancelling')
                    continue
                line = line + '\t' + '\t'.join([str(item) for item in pages])
            elif answer == '2':
                with open('Subjects.txt', 'r', encoding='utf-8') as file:
                    line = '\n'.join([item.replace('\n', '') for item in file])
            elif answer == '0':
                print('Cancelled')
                continue
            if len(line) == 0:
                print('Nothing to send. Cancelling')
                continue
            s.send(bytes('1', 'utf-8'))
            data = s.recv(1024)
            s.send(bytes(line, 'utf-8'))
            data = s.recv(1024).decode()
            if data == '0':
                print('Operation done successfully')
            else:
                print('Something went wrong. Error code:', data)
        elif answer == '2':
            s.send(bytes('2', 'utf-8'))
            data = s.recv(1024).decode().split('\n')
            if data[0] == '0':
                print('Something went wrong. No data received')
                continue
            data = [item.split('\t') for item in data]
            print('Word : Pages')
            for val in data:
                print(val[0], ':', val[1], end='')
                for i in range(2, len(val)):
                    print(',', val[i], end='')
                print()
        elif answer == '3':
            line = input('Type the word to get info about it\'s pages: ')
            s.send(bytes('3', 'utf-8'))
            data = s.recv(1024)
            s.send(bytes(line, 'utf-8'))
            data = s.recv(1024).decode()
            if data == '0':
                print('No info found about this word')
                continue
            data = data.split('\t')
            print(f'Pages where word "{line}" located:')
            for val in data:
                print(val, end=' ')
            print()
        elif answer == '4':
            line = input('Type the word to delete from list: ')
            s.send(bytes('4', 'utf-8'))
            data = s.recv(1024)
            s.send(bytes(line, 'utf-8'))
            data = s.recv(1024).decode()
            if data == '0':
                print('Operation done successfully')
            else:
                print('Operation not done. Code:', data)
        elif answer == '0':
            break
    s.close()