# Simple POP3 Server in Python

A basic implementation of a POP3 (Post Office Protocol version 3) server in Python. This server allows clients to connect and retrieve, list, and delete emails from a simple mailbox.

## Features

- POP3 server implementation with basic commands (QUIT, STAT, LIST, RETR, DELE, TEST, NOOP, RSET).
- Uses Python's built-in `socket` module for networking.
- Persistence of emails using pickle for loading and saving the mailbox.

## How to Use

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/pop3-server-python.git
    cd pop3-server-python
    ```

2. Run the server:

    ```bash
    python pop3_server.py
    ```

3. Connect to the server using a POP3 client (e.g., Outlook, Thunderbird) and configure the client with the server address (`localhost`) and port (`1100`).Or alternatively use telnet:  \n

    ```bash 
    telnet localhost 1100
    ```
4. Use standard POP3 commands to interact with the server.

## Configuration

- **Server Address:** localhost
- **Server Port:** 1100

## Dependencies

- Python 3.x

## Notes

- This is a basic implementation and lacks advanced features and security measures.
- Be cautious about using this in a production environment.

## License

This project is licensed under the [MIT License](LICENSE).

