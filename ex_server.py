import ssl
import socket
import signal
import sys
import threading
import pickle

CERT_DIR = r'cert.pem'
KEY_DIR = r'key.pem'
IP_ADDRESS = '192.168.94.59'
MAILBOX_FILE = 'mailbox.pkl'

port = input("Enter the port number to listen on (default is 995): ")
try:
    port = int(port)
except ValueError:
    print("Invalid port number. Using default port 8000.")
    port = 8000



USERS = {
    'user1': 'password1',
    'user2': 'password2',
}

# region ssl config
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(CERT_DIR, KEY_DIR)
server_socket = None
client_sockets = []
# endregion


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

 
def handle_stat_command(secure_socket, user):
    mailbox = load_mailbox(user)
    email_count = mailbox.get_email_count()
    email_size = mailbox.get_email_size()
    response = f'+OK {email_count} {email_size}\r\n'
    secure_socket.sendall(response.encode())


def handle_noop_command(secure_socket, user):
    secure_socket.sendall(b'+OK\r\n')


def handle_retr_command(secure_socket, user, index):
    mailbox = load_mailbox(user)
    email = mailbox.get_email(index)
    if email:
        header = f"From: {email.sender}\r\nSubject: {email.subject}\r\n\r\n"
        response = f"+OK {len(email.body.encode())} octets\r\n{header}{email.body}\r\n.\r\n"
        secure_socket.sendall(response.encode())
    else:
        secure_socket.sendall(b"-ERR no such message\r\n")

def handle_dele_command(secure_socket, user, index):
    mailbox = load_mailbox(user)
    if mailbox.delete_email(index):
        save_mailbox(mailbox, user)
        secure_socket.sendall(f"+OK message {index} deleted\r\n".encode())
    else:
        secure_socket.sendall(b"-ERR no such message\r\n")

def save_mailbox(mailbox, user):
    with open(f'{MAILBOX_FILE}_{user}', 'wb') as file:
        pickle.dump(mailbox, file)

def handle_list_command(secure_socket, user, arg=None):
    mailbox = load_mailbox(user)
    email_list = mailbox.get_email_list()
    if not arg:
        if not email_list:
            secure_socket.sendall(b'+OK 0 messages\r\n')
        else:
            response = b'+OK %d messages (%d octets)\r\n' % (len(email_list), sum(size for _, size in email_list))
            for index, size in email_list:
                response += b'%d %d\r\n' % (index, size)
            response += b'.\r\n'
            secure_socket.sendall(response)
    else:
        try:
            index = int(arg)
            email = mailbox.get_email(index)
            if email and not email.to_del:
                body_size = len(email.body.encode())
                secure_socket.sendall(b'+OK %d %d\r\n' % (index, body_size))
            else:
                secure_socket.sendall(b'-ERR no such message\r\n')
        except ValueError:
            secure_socket.sendall(b'-ERR invalid message number\r\n')

def handle_rset_command(secure_socket, user):
    mailbox = load_mailbox(user)
    mailbox.reset_deletion_markers()
    save_mailbox(mailbox, user)
    email_count = mailbox.get_email_count()
    email_size = mailbox.get_email_size()
    response = f"+OK maildrop has {email_count} messages ({email_size} octets)\r\n"
    secure_socket.sendall(response.encode())

#region graceful exit
def graceful_exit(signal, frame):
    print('Shutting down server...')
    for client_socket in client_sockets:
        client_socket.close()
    server_socket.close()
    sys.exit(0)
    
signal.signal(signal.SIGINT, graceful_exit)
signal.signal(signal.SIGTERM, graceful_exit)

#endregion

# region mailbox and email

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
        email_list = [(i + 1, len(email.body.encode())) for i, email in enumerate(self.emails) if not email.to_del]
        return email_list

    def get_email(self, index):
        if 1 <= index <= len(self.emails):
            return self.emails[index - 1]
        else:
            return None

    def delete_email(self, index):
        if 1 <= index <= len(self.emails):
            self.emails[index - 1].to_del = 1
        else:
            return False
        return True
    
    def reset_deletion_markers(self):
        for email in self.emails:
            email.to_del = 0

   
    def delete_marked_emails(self):
        self.emails = [email for email in self.emails if not email.to_del]

# endregion
 
def remove_deleted_emails(mailbox):
        mailbox.emails = [email for email in mailbox.emails if not email.to_del]
    


def load_mailbox(user):
    try:
        with open(f'{MAILBOX_FILE}_{user}', 'rb') as file:
            mailbox = pickle.load(file)
    except FileNotFoundError:
        mailbox = Mailbox(user)  # Initialize a new Mailbox instance
        with open(f'{MAILBOX_FILE}_{user}', 'wb') as file:
            pickle.dump(mailbox, file)  # Save the new mailbox instance to a file
    return mailbox

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
            if command.startswith("QUIT") and not authenticated:
                secure_socket.sendall(b'+OK dewey POP3 server signing off\r\n')     
                break
            elif command.startswith("QUIT") and authenticated:
                mailbox = load_mailbox(user)
                remove_deleted_emails(mailbox)
                save_mailbox(mailbox, user)
                secure_socket.sendall(b'+OK dewey POP3 server signing off(maildrop empty)\r\n')
                break
            elif command.startswith("USER"):
                user = handle_user_command(command, secure_socket, user)
            elif command.startswith("PASS"):
                authenticated = handle_pass_command(command, secure_socket, user)
            elif command.startswith("STAT"):
                handle_stat_command(secure_socket, user)
            elif command.startswith("NOOP"):
                handle_noop_command(secure_socket, user)
            elif command.startswith("LIST"):
                parts = command.split()
                if len(parts) == 1:
                    handle_list_command(secure_socket, user)
                elif len(parts) == 2:
                    handle_list_command(secure_socket, user, parts[1])
            
            elif command.startswith("RETR"):
                parts = command.split()
                if len(parts) == 2:
                    try:
                        index = int(parts[1])
                        handle_retr_command(secure_socket, user, index)
                    except ValueError:
                        secure_socket.sendall(b"-ERR invalid message number\r\n")
                else:
                    secure_socket.sendall(b"-ERR\r\n")
            
            elif command.startswith("DELE"):
                parts = command.split()
                if len(parts) == 2:
                    try:
                        index = int(parts[1])
                        handle_dele_command(secure_socket, user, index)
                    except ValueError:
                        secure_socket.sendall(b"-ERR invalid message number\r\n")
                else:
                    secure_socket.sendall(b"-ERR\r\n")
            
            elif command.startswith("RSET"):
                handle_rset_command(secure_socket, user)
            else:
                secure_socket.sendall(b'-ERR\r\n')
        break   
    secure_socket.close()
    client_socket.close()
    print(f'Connection from {client_address} closed.')
# region sll connection
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP_ADDRESS, port))
server_socket.listen(5)
print(f'SSL server started on localhost:{port}')
# endregion
while True:
    client_socket, client_address = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()