import ssl
import socket

ip_address = '10.0.0.1'
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations('cert.pem')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#replace 'localhost' with the IP address or hostname
secure_socket = context.wrap_socket(client_socket, server_hostname=ip_address)
secure_socket.connect((ip_address, 8000))

print('Connected to SSL server')

while True:
    data = input('Enter message: ').encode()
    if not data:
        break
    secure_socket.sendall(data)

    response = secure_socket.recv(1024)
    print(f'Received response: {response.decode()}')

secure_socket.close()