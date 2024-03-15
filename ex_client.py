import ssl
import socket

CERT_DIR = r'cert.pem'
# KEY_DIR = r'cert\key.pem'
ip_address = 'localhost'


context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations(CERT_DIR)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#replace 'localhost' with the IP address or hostname
secure_socket = context.wrap_socket(client_socket, server_hostname=ip_address)
secure_socket.connect((ip_address, 8000))

print('Connected to SSL server')
buffer = b''
authenticated = False
user = None

while True:
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

        data = (input('Enter response: ')+'\r\n').encode() 
        secure_socket.sendall(data)
 
secure_socket.close()