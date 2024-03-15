import ssl
import socket
import time

CERT_DIR = r'cert.pem'
KEY_DIR = r'key.pem'
IP_ADDRESS = 'localhost'
USERS = {
    'user1': 'password1',
    'user2': 'password2',
}

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(CERT_DIR, KEY_DIR)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP_ADDRESS, 8000))
server_socket.listen(5)

print('SSL server started on localhost:8000')

while True:
    try:
        client_socket, client_address = server_socket.accept()
        print(f'New connection from {client_address}')

        secure_socket = context.wrap_socket(client_socket, server_side=True)
        secure_socket.sendall(b'+OK POP3 server ready\r\n')

        buffer = b''
        authenticated = False
        user = None

        while True:
            data = secure_socket.recv(1024)
            if not data:
                break

            print(f'Received data: {data.decode()}')
            buffer += data
            lines = buffer.split(b'\r\n')
            buffer = lines.pop()
            print(f'lines: {lines} , data {data}')
            
            for line in lines:
                command = line.decode().strip()
                if command.startswith("QUIT"):
                    secure_socket.sendall(b'+OK dewey POP3 server signing off\r\n') 
                    break

    except Exception as e:
        print(f'Error: {e}')
    finally:
        client_socket.close()
        secure_socket.close()