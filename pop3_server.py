import socket
import threading

SERVER_ADDRESS = ('localhost', 1100) #use port 110
BUFFER_SIZE = 1024

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


    def handle_command(self, command, client_socket):
        if command.startswith("QUIT"):
            client_socket.sendall(b'+OK Bye\r\n')
            return True
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
