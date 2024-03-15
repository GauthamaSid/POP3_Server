import ssl
import socket
import signal
import sys

CERT_DIR = r'cert.pem'
# KEY_DIR = r'cert\key.pem'
ip_address = 'localhost'

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations(CERT_DIR)

client_socket = None
secure_socket = None

def graceful_exit(signal, frame):
    print('Shutting down client...')
    if secure_socket:
        secure_socket.close()
    if client_socket:
        client_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
secure_socket = context.wrap_socket(client_socket, server_hostname=ip_address)
secure_socket.connect((ip_address, 8000))
print('Connected to SSL server')

buffer = b''
authenticated = False
user = None

while True:
    try:
        response = secure_socket.recv(1024)
        if not response:
            break
        buffer += response
        lines = buffer.split(b'\r\n')
        buffer = lines.pop()
        print(f'Received response: {response.decode()}')
        print(f'lines: {lines}')

        for line in lines:
            command = line.decode().strip()
            data = (input('Enter response: ') + '\r\n').encode()
            secure_socket.sendall(data)

    except KeyboardInterrupt:
        graceful_exit(signal.SIGINT, None)
    except Exception as e:
        print(f'Error: {e}')
        break

if secure_socket:
    secure_socket.close()
if client_socket:
    client_socket.close()