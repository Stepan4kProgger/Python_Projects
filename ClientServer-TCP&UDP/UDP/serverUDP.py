'''9.	Клиент вводит с клавиатуры строку символов и посылает ее серверу.
Признак окончания ввода строки – нажатие  клавиши «Ввод». Сервер, получив
эту строку, должен определить длину введенной строки,  и, если эта длина
кратна 5,  то подсчитывается количество скобок всех видов. Их количество
посылается клиенту. '''

import socket

with socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) as s:
    s.bind(('127.0.0.1', 65432))
    print('Server is running')
    while True:
        data, address = s.recvfrom(1024)
        data = data.decode()
        print('Received', len(data), 'bytes from', address , end=' ... ')
        answer = list()
        if len(data) % 5 == 0:
            for bkt in {'(', ')', '{', '}', '[', ']', '<', '>'}:
                if bkt in data:
                    answer.append(bkt + str(data.count(bkt)))
            if answer:  # если нет инфы по скобкам, просто отправляем длину строки
                answer = ' '.join(answer)
        if not answer:
            answer = '0'
        s.sendto(bytes(answer, 'utf-8'), address)
        print('Sent', len(answer), 'back to', address)