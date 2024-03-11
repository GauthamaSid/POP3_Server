import socket
import ssl

class POP3Client:
    def __init__(self, server, port, username, password, ssl_enabled=True):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.ssl_enabled = ssl_enabled
        self.socket = None

    def connect(self):
        try:
            self.socket = socket.create_connection((self.server, self.port))
            if self.ssl_enabled:
                context = ssl.create_default_context()
                self.socket = context.wrap_socket(self.socket, server_hostname=self.server)
            self.receive_response()
        except (socket.error, ssl.SSLError) as e:
            print("Error connecting to server:", e)

    def receive_response(self):
        response = b""
        while True:
            try:
                part = self.socket.recv(1024)
                response += part
                if not part or b'\r\n' in part:
                    break
            except (socket.error, ssl.SSLError) as e:
                print("Error receiving response:", e)
                break
        return response.decode("utf-8")

    def send_command(self, command):
        try:
            command = command.upper()  # Convert command to uppercase
            self.socket.sendall(command.encode("utf-8") + b'\r\n')  # Ensure proper termination
            return self.receive_response()
        except (socket.error, ssl.SSLError, ConnectionResetError) as e:
            print("Error sending command:", e)


    def login(self):
        self.send_command(f"USER {self.username}")
        self.send_command(f"PASS {self.password}")

    def list_emails(self):
        response = self.send_command("LIST")
        print(response)

    def retrieve_email(self, email_number):
        response = self.send_command(f"RETR {email_number}")
        print(response)

    def delete_email(self, email_number):
        response = self.send_command(f"DELE {email_number}")
        print(response)

    def quit(self):
        self.send_command("QUIT")
        self.socket.close()

if __name__ == "__main__":
    server = input("Enter POP3 server address: ")
    port = int(input("Enter port number (usually 995 for SSL): "))
    username = input("Enter your email address: ")
    password = input("Enter your password: ")

    pop3_client = POP3Client(server, port, username, password)
    pop3_client.connect()
    pop3_client.login()

    pop3_client.list_emails()
    email_number = int(input("Enter the email number to retrieve: "))
    pop3_client.retrieve_email(email_number)

    delete_option = input("Do you want to delete this email? (yes/no): ").strip().lower()
    if delete_option == 'yes':
        pop3_client.delete_email(email_number)
        print("Email marked for deletion.")

    pop3_client.quit()
