import socket
import ssl

SERVER_ADDRESS = ('localhost', 995)

class POP3Client:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.socket = None
        self.ssl_context = ssl.create_default_context()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(SERVER_ADDRESS)
        self.ssl_context.load_verify_locations('/path/to/server/certificate.pem')
        self.ssl_socket = self.ssl_context.wrap_socket(self.socket, server_hostname='localhost')

        response = self.receive_response()
        print(response)

    def authenticate(self):
        self.send_command(f"USER {self.username}")
        response = self.receive_response()
        print(response)

        self.send_command(f"PASS {self.password}")
        response = self.receive_response()
        print(response)

        if not response.startswith("+OK"):
            raise Exception("Authentication failed")

    def send_command(self, command):
        self.ssl_socket.sendall(f"{command}\r\n".encode())

    def receive_response(self):
        response = self.ssl_socket.recv(1024).decode()
        return response.strip()

    def list_emails(self):
        self.send_command("LIST")
        response = self.receive_response()
        print(response)

    def retrieve_email(self, index):
        self.send_command(f"RETR {index}")
        response = self.receive_response()
        print(response)

        if response.startswith("+OK"):
            email_body = ""
            line = self.ssl_socket.recv(1024).decode()
            while line != ".\r\n":
                email_body += line
                line = self.ssl_socket.recv(1024).decode()
            print(email_body)

    def delete_email(self, index):
        self.send_command(f"DELE {index}")
        response = self.receive_response()
        print(response)

    def quit(self):
        self.send_command("QUIT")
        response = self.receive_response()
        print(response)
        self.ssl_socket.close()

if __name__ == "__main__":
    username = "user1"
    password = "password1"

    client = POP3Client(username, password)
    client.connect()
    client.authenticate()
    client.list_emails()
    client.retrieve_email(1)
    client.delete_email(1)
    client.quit()