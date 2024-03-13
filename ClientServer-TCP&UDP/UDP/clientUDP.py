'''9.	Клиент вводит с клавиатуры строку символов и посылает ее серверу.
Признак окончания ввода строки – нажатие  клавиши «Ввод». Сервер, получив
эту строку, должен определить длину введенной строки,  и, если эта длина
кратна 5,  то подсчитывается количество скобок всех видов. Их количество
посылается клиенту. '''

import socket

with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as s:
    while True:
        line = input('Enter string (0 - exit):\n')
        if line == '0':
            break
        s.sendto(bytes(line, 'utf-8'), ('127.0.0.1', 65432))
        reply = s.recvfrom(1024)[0].decode()
        print('Reply is:', reply)
        reply = reply.split()
        if reply[0][0].isdigit():
            print('No info about brackets')
        else:
            print('Brackets info (type : count):')
            for val in reply:
                print(val[0], ':', val[1:])
    s.close()
