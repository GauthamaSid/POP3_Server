import ssl
import socket
import pickle
import ssl

CERT_DIR = r'cert.pem'
KEY_DIR = r'key.pem'
IP_ADDRESS = 'localhost'

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(CERT_DIR, KEY_DIR)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

 # replace 'localhost' with the actual IP address/hostname of server
server_socket.bind((IP_ADDRESS, 8000))
server_socket.listen(5)

print('SSL server started on localhost:8000')

while True:
    try:
        client_socket, client_address = server_socket.accept()
        print(f'New connection from {client_address}')

        secure_socket = context.wrap_socket(client_socket, server_side=True)

        while True:
            data = secure_socket.recv(1024)
            if not data:
                break
            print(f'Received data: {data.decode()}')

            response = input('Enter response: ').encode()
            secure_socket.sendall(response)

    except Exception as e:
        print(f'Error: {e}')

    finally:
        secure_socket.close()
        client_socket.close()