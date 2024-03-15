import ssl
import socket
import signal
import sys
import threading

CERT_DIR = r'cert.pem'
# KEY_DIR = r'cert\\key.pem'
IP_ADDRESS = 'localhost'

port = input("Enter the port number to listen on (default is 995): ")
try:
    port = int(port)
except ValueError:
    print("Invalid port number. Using default port 8000.")
    port = 8000

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
    print("sys.exit")
    
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

def receive_data():
    buffer = b''
    while True:
        try:
            response = secure_socket.recv(1024)
            if not response:
                break
            buffer += response
            lines = buffer.split(b'\r\n')
            buffer = lines.pop()
            for line in lines:
                print(f'S: {line.decode()}')
        except Exception as e:
            print(f'Error: {e}')
            break

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
secure_socket = context.wrap_socket(client_socket, server_hostname=IP_ADDRESS)
secure_socket.connect((IP_ADDRESS, port))
print(f'Connected to SSL server using port{port}')

receive_thread = threading.Thread(target=receive_data)
receive_thread.start()

while True:
    try:
        data = (input('') + '\r\n').encode()
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