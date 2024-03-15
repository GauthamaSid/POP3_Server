import socket
import ssl

SERVER_ADDRESS = ('localhost', 995)
BUFFER_SIZE = 1024

def main():
    # Create a socket and connect to the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE  # Disable certificate verification
    ssl_socket = ssl_context.wrap_socket(sock, server_hostname='localhost')
    ssl_socket.connect(SERVER_ADDRESS)

    try:
        print("Connected to POP3 server")

        # Send the USER command
        username = input("Enter username: ")
        send_command(ssl_socket, f"USER {username}")

        # Send the PASS command
        password = input("Enter password: ")
        send_command(ssl_socket, f"PASS {password}")

        # Get the mailbox status
        send_command(ssl_socket, "STAT")

        # List available messages
        send_command(ssl_socket, "LIST")

        # Retrieve a message
        message_index = int(input("Enter message index to retrieve: "))
        send_command(ssl_socket, f"RETR {message_index}")

        # Delete a message
        message_index = int(input("Enter message index to delete: "))
        send_command(ssl_socket, f"DELE {message_index}")

        # Reset the mailbox (undelete messages)
        send_command(ssl_socket, "RSET")

        # Quit the session
        send_command(ssl_socket, "QUIT")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        ssl_socket.close()

def send_command(ssl_socket, command):
    ssl_socket.sendall(f"{command}\r\n".encode())
    response = ssl_socket.recv(BUFFER_SIZE)
    print(response.decode())

if __name__ == "__main__":
    main()