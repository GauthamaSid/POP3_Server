import ssl
import socket

CERT_DIR = r'cert.pem'
KEY_DIR = r'key.pem'
IP_ADDRESS = 'localhost'
USERS = {
    'user1': 'password1',
    'user2': 'password2',
}
authenticated = False

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(CERT_DIR, KEY_DIR)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP_ADDRESS, 8000))
server_socket.listen(5)
print('SSL server started on localhost:8000')


def handle_user_command(command, secure_socket, user):
    parts = command.split()
    if len(parts) == 2:
        user = parts[1]
        print(f'user is {user}')
        secure_socket.sendall(b'+OK\r\n')
    else:
        secure_socket.sendall(b'-ERR Missing username\r\n')
    return user


def handle_pass_command(command, secure_socket, user):
    if user in USERS:
        parts = command.split()
        if len(parts) == 2:
            password = parts[1]
            if USERS[user] == password:
                secure_socket.sendall(b'+OK User authenticated\r\n')
                authenticated = True
                return True
            else:
                secure_socket.sendall(b'-ERR Invalid password\r\n')
        else:
            secure_socket.sendall(b'-ERR Missing password\r\n')
    else:
        secure_socket.sendall(b'-ERR User not found\r\n')
    return False



while True:
    try:
        client_socket, client_address = server_socket.accept()
        print(f'New connection from {client_address}')
        secure_socket = context.wrap_socket(client_socket, server_side=True)
        secure_socket.sendall(b'+OK POP3 server ready\r\n')
        buffer = b''
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
                elif command.startswith("USER"):
                    user = handle_user_command(command, secure_socket, user)
                elif command.startswith("PASS"):
                    authenticated = handle_pass_command(command, secure_socket, user)
                elif command.startswith("STAT"):
                    if authenticated:
                        secure_socket.sendall(b'+OK will implement STAT\r\n')
                    else:
                        secure_socket.sendall(b'+ERR')
                
                else:
                    secure_socket.sendall(b'ERR Authentication required\r\n')

    except Exception as e:
        print(f'Error: {e}')
    finally:
        client_socket.close()
        secure_socket.close()