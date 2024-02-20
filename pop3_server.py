import socket
import threading

SERVER_ADDRESS = ('localhost', 1100) #NOTE:POP3 uses port 110
BUFFER_SIZE = 1024

class Email:
    def __init__(self, sender, subject, body):
        self.sender = sender
        self.subject = subject
        self.body = body

class Mailbox:
    def __init__(self):
        self.emails = []

    def add_email(self, sender, subject, body):
        email = Email(sender, subject, body)
        self.emails.append(email)

    def get_email_count(self):
        return len(self.emails)

    def get_email_size(self):
        # Calculate the total size of all emails (for simplicity, assume each email has a fixed size)
        total_size = 0

        for email in self.emails:
            # Consider the size of headers and the separator (CRLF)
            email_header_size = len(f"From: {email.sender}\r\nSubject: {email.subject}\r\n\r\n".encode())
            email_body_size = len(email.body.encode())
            total_size += email_header_size + email_body_size
        return total_size

    def get_email_list(self):
        # Return a list of email indices and their sizes
        email_list = [(i + 1, len(email.body.encode())) for i, email in enumerate(self.emails)]
        return email_list

    def get_email(self, index):
        # Return the email at the specified index
        if 1 <= index <= len(self.emails):
            return self.emails[index - 1]
        else:
            return None

    def delete_email(self, index):
        # Delete the email at the specified index
        if 1 <= index <= len(self.emails):
            del self.emails[index - 1]

# creating email data:
mailbox = Mailbox()
mailbox.add_email("raj@example.com", "Hello", "This is the body of the email.")
mailbox.add_email("ram@example.com", "Meeting", "Meeting at 2 PM in the conference room.")

# Retrieve mailbox information
email_count = mailbox.get_email_count()
email_size = mailbox.get_email_size()
email_list = mailbox.get_email_list()


class POP3Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(SERVER_ADDRESS)
        self.server_socket.listen()
        self.is_running = True
        self.connections = []

    def handle_client(self, client_socket, client_address):
        with client_socket:
            print(f"Accepted connection from {client_address}")
            client_socket.sendall(b'+OK POP3 server ready\r\n')
            buffer = b''
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                buffer += data
                lines=buffer.split(b'\r\n')
                buffer=lines.pop()
                for line in lines:
                    command=line.decode().strip()
                    if self.handle_command(command, client_socket):
                        break

        print(f"Connection from {client_address} closed")

    def handle_list_command(self, client_socket):
        # Send a positive response with a list of message sizes
        maildrop_size = mailbox.get_email_size()
        email_list = mailbox.get_email_list()

        response = f'+OK {len(email_list)} messages ({maildrop_size} octets)\r\n'
        for email_index, email_size in email_list:
            response += f'{email_index} {email_size}\r\n'

        client_socket.sendall(response.encode())

        return False

    def handle_command(self, command, client_socket):
        
        if command.startswith("QUIT"):
            client_socket.sendall(b'+OK Bye\r\n')
            return True
        
        elif command.startswith("STAT"):
 
            client_socket.sendall(f'+OK {email_count} {email_size}\r\n'.encode('utf-8'))
        
        elif command.startswith("LIST"):
            return self.handle_list_command(client_socket)
        
        else:
            client_socket.sendall(b'-ERR Unknown command\r\n')

        return False

    def run(self):
        print(f"POP3 server listening on {SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}")

        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                connection_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                connection_thread.start()
                self.connections.append(connection_thread)
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        print("Stopping POP3 server...")
        self.is_running = False
        self.server_socket.close()

        # Wait for all connection threads to finish
        for connection_thread in self.connections:
            connection_thread.join()

if __name__ == "__main__":
    pop3_server = POP3Server()
    try:
        pop3_server.run()
    except KeyboardInterrupt:
        pop3_server.stop()
