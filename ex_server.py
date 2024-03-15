import ssl
import socket
import signal
import sys
import threading
import pickle

CERT_DIR = r'cert.pem'
KEY_DIR = r'key.pem'
IP_ADDRESS = 'localhost'
MAILBOX_FILE = 'mailbox.pkl'  

USERS = {
    'user1': 'password1',
    'user2': 'password2',
}
#region ssl config
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(CERT_DIR, KEY_DIR)
server_socket = None
client_sockets = []
#endregion

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
                return True
            else:
                secure_socket.sendall(b'-ERR Invalid password\r\n')
        else:
            secure_socket.sendall(b'-ERR Missing password\r\n')
    else:
        secure_socket.sendall(b'-ERR User not found\r\n')
    return False



def graceful_exit(signal, frame):
    print('Shutting down server...')
    for client_socket in client_sockets:
        client_socket.close()
    server_socket.close()
    sys.exit(0)

#region mailbox and email

class Email:
    def __init__(self, sender, subject, body, to_del):
        self.sender = sender
        self.subject = subject
        self.body = body
        self.to_del = to_del

class Mailbox:
    def __init__(self, user):
        self.user = user
        self.emails = []

    def add_email(self, sender, subject, body):
        email = Email(sender, subject, body, 0)
        self.emails.append(email)

    def get_email_count(self):
        def count_to_del(self):
            count = 0
            for email in self.emails:
                if email.to_del:
                    count += 1
            return count

        return len(self.emails) - count_to_del(self)

    def get_email_size(self):
        total_size = 0

        for email in self.emails:
            email_header_size = len(f"From: {email.sender}\r\nSubject: {email.subject}\r\n\r\n".encode())
            email_body_size = len(email.body.encode())
            total_size += email_header_size + email_body_size
        return total_size

    def get_email_list(self):
        email_list = [(i + 1, len(email.body.encode())) for i, email in enumerate(self.emails)]
        return email_list

    def get_email(self, index):
        if 1 <= index <= len(self.emails):
            return self.emails[index - 1]
        else:
            return None

    def delete_email(self, index):
        if 1 <= index <= len(self.emails):
            self.emails[index - 1].to_del = 1

    def delete_marked_emails(self):
        self.emails = [email for email in self.emails if not email.to_del]

#endregion
signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

def handle_client(client_socket, client_address):
    print(f'New connection from {client_address}')
    secure_socket = context.wrap_socket(client_socket, server_side=True)
    secure_socket.sendall(b'+OK POP3 server ready\r\n')
    buffer = b''
    user = None
    authenticated = False
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
                    secure_socket.sendall(b'-ERR Authentication required\r\n')
            elif command.startswith("NOOP"):
                if authenticated:
                    secure_socket.sendall(b'+OK')
                else:
                    secure_socket.sendall(b'-ERR Authentication required\r\n')
            else:
                secure_socket.sendall(b'-ERR\r\n')
    secure_socket.close()
    client_socket.close()
    print(f'Connection from {client_address} closed.')

#region sll connection
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP_ADDRESS, 8000))
server_socket.listen(5)
print('SSL server started on localhost:8000')
#endregion
while True:
    client_socket, client_address = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()