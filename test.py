import socket
import threading
import pickle

SERVER_ADDRESS = ('localhost', 1100)
BUFFER_SIZE = 1024
MAILBOX_FILE = 'mailbox.pkl'  # File to store the mailbox

class Email:
    def __init__(self, sender, subject, body, to_del):
        self.sender = sender
        self.subject = subject
        self.body = body
        self.to_del = to_del

class Mailbox:
    def __init__(self):
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

class POP3Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(SERVER_ADDRESS)
        self.server_socket.listen()
        self.is_running = True
        self.connections = []

    def load_mailbox(self):
        try:
            with open(MAILBOX_FILE, 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            return Mailbox()

    def save_mailbox(self, mailbox):
        with open(MAILBOX_FILE, 'wb') as file:
            pickle.dump(mailbox, file)

    def handle_client(self, client_socket, client_address, mailbox):
        with client_socket:
            print(f"Accepted connection from {client_address}")
            client_socket.sendall(b'+OK POP3 server ready\r\n')
            buffer = b''
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                buffer += data
                lines = buffer.split(b'\r\n')
                buffer = lines.pop()
                for line in lines:
                    command = line.decode().strip()
                    if self.handle_command(command, client_socket, mailbox):
                        break

        print(f"Connection from {client_address} closed")

    def handle_list_command(self, client_socket, mailbox, message_number=None):
        if message_number is not None:
            email = mailbox.get_email(message_number)
            if email:
                response = f'+OK {message_number} {len(email.body.encode())}\r\n'
                client_socket.sendall(response.encode())
            else:
                client_socket.sendall(b'-ERR No such message\r\n')
        else:
            email_list = [(i + 1, len(email.body.encode())) for i, email in enumerate(mailbox.emails) if not email.to_del]
            maildrop_size = sum(size for _, size in email_list)
            response = f'+OK {len(email_list)} messages ({maildrop_size} octets)\r\n'
            for email_index, email_size in email_list:
                response += f'{email_index} {email_size}\r\n'
            client_socket.sendall(response.encode())
        return False

    def handle_retr_command(self, message_index, client_socket, mailbox):
        email = mailbox.get_email(message_index)
        if email:
            response = f'+OK {len(email.body.encode())} octets\r\n{email.body}\r\n.\r\n'
            client_socket.sendall(response.encode('utf-8'))
        else:
            client_socket.sendall(b'-ERR No such message\r\n')
        return False

    def handle_rset_command(self, client_socket, mailbox):
        for email in mailbox.emails:
            email.to_del = 0
        response = f'+OK maildrop has {mailbox.get_email_count()} messages ({mailbox.get_email_size()} octets)\r\n'
        client_socket.sendall(response.encode())
        return False

    def handle_dele_command(self, message_index, client_socket, mailbox):
        email = mailbox.get_email(message_index)
        if email and email.to_del == 1:
            client_socket.sendall(b'-ERR Message already deleted\r\n')
        elif email:
            mailbox.delete_email(message_index)
            client_socket.sendall(b'+OK Message deleted\r\n')
        else:
            client_socket.sendall(b'-ERR No such message\r\n')
        return False

    def throw_error(self, client_socket):
        client_socket.sendall(b'-ERR Unknown command\r\n')

    def handle_command(self, command, client_socket, mailbox):
        if command.startswith("QUIT"):
            client_socket.sendall(b'+OK Bye\r\n')
            mailbox.delete_marked_emails()
            self.save_mailbox(mailbox)
            return True
        elif command.startswith("STAT"):
            client_socket.sendall(f'+OK {mailbox.get_email_count()} {mailbox.get_email_size()}\r\n'.encode('utf-8'))
        elif command.startswith("LIST"):
            parts = command.split()
            if len(parts) == 2:
                message_number = int(parts[1])
                return self.handle_list_command(client_socket, mailbox, message_number)
            else:
                return self.handle_list_command(client_socket, mailbox)
        elif command.startswith("RETR"):
            parts = command.split()
            if len(parts) == 2:
                message_index = int(parts[1])
                return self.handle_retr_command(message_index, client_socket, mailbox)
            else:
                client_socket.sendall(b'-ERR Invalid RETR command\r\n')
        elif command.startswith("DELE"):
            parts = command.split()
            if len(parts) == 2:
                message_index = int(parts[1])
                return self.handle_dele_command(message_index, client_socket, mailbox)
            else:
                client_socket.sendall(b'-ERR Invalid DELE command\r\n')
        elif command.startswith("TEST"):
            client_socket.sendall(b'\r\n')
        elif command.startswith("NOOP"):
            client_socket.sendall(b'+OK')
        elif command.startswith("RSET"):
            return self.handle_rset_command(client_socket, mailbox)
        else:
            self.throw_error(client_socket)
        return False

    def run(self):
        print(f"POP3 server listening on {SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}")
        mailbox = self.load_mailbox()

        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                connection_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address, mailbox))
                connection_thread.start()
                self.connections.append(connection_thread)
            except KeyboardInterrupt:
                self.stop()

        self.save_mailbox(mailbox)

    def stop(self):
        print("Stopping POP3 server...")
        self.is_running = False
        self.server_socket.close()

        for connection_thread in self.connections:
            connection_thread.join()

if __name__ == "__main__":
    pop3_server = POP3Server()
    try:
        pop3_server.run()
    except KeyboardInterrupt:
        pop3_server.stop()
