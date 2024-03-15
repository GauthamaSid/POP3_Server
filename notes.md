## Server

- error handling
- command validation
- unit tests?

 The AUTHORIZATION State .....................................
    QUIT Command ................................................    y
    The TRANSACTION State .......................................
    STAT Command ................................................    y
      LIST Command ................................................    y
      RETR Command ................................................    y
      DELE Command ................................................    y
      NOOP Command ................................................    y
      RSET Command ................................................    y
   6. The UPDATE State ............................................
    QUIT Command ................................................   y

--
# notes

## openssl

```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=localhost"
```

```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=10.0.0.1"
```

## to do

- graceful error handling client
- client not connet handling
- quit
- maybe color

## testing

To test the SSL client and server running on different computers with just one computer, you can use network namespaces in Linux. Network namespaces provide a way to create isolated network environments within the same host, allowing you to simulate different network interfaces and IP addresses.

Here's how you can set up and test the SSL client and server on a single computer:

1. **Create network namespaces**:

   - Create two network namespaces, one for the server and one for the client:

     ```bash
     sudo ip netns add server
     sudo ip netns add client
     ```

2. **Set up virtual network interfaces**:

   - Create a virtual Ethernet pair (veth) and assign one end to each namespace:

     ```bash
     sudo ip link add veth0 type veth peer name veth1
     sudo ip link set veth0 netns server
     sudo ip link set veth1 netns client
     ```

3. **Assign IP addresses to the virtual interfaces**:

   - Inside the server namespace:

     ```bash
     sudo ip netns exec server ip addr add 10.0.0.1/24 dev veth0
     sudo ip netns exec server ip link set veth0 up
     ```

   - Inside the client namespace:

     ```bash
     sudo ip netns exec client ip addr add 10.0.0.2/24 dev veth1
     sudo ip netns exec client ip link set veth1 up
     ```

4. **Update the server code**:

   - In the server code, replace `'localhost'` with the server's IP address `'10.0.0.1'`:

     ```python
     server_socket.bind(('10.0.0.1', 8000))
     ```

5. **Update the client code**:

   - In the client code, replace `'localhost'` with the server's IP address `'10.0.0.1'`:

     ```python
     secure_socket.connect(('10.0.0.1', 8000))
     secure_socket = context.wrap_socket(client_socket, server_hostname='10.0.0.1')
     ```

6. **Start the server and client**:

   - Start the server in the server namespace:

     ```bash
     sudo ip netns exec server python3 server.py
     ```

   - Start the client in the client namespace:

     ```bash
     sudo ip netns exec client python3 client.py
     ```

Now, the SSL server and client are running in different network namespaces, simulating different computers. The server is listening on the IP address `10.0.0.1`, and the client is connecting to that IP address.

You can test the two-way communication between the server and client as described earlier. When you're done testing, you can clean up the network namespaces with the following commands:

```bash
sudo ip netns delete server
sudo ip netns delete client
```

Using network namespaces allows you to test your SSL server and client in a simulated environment without the need for multiple physical machines. However, keep in mind that network namespaces do not provide the same level of isolation and performance characteristics as running on separate physical machines or virtual machines.

## generating the key

Ah, I see the issue now. The `ssl.SSLCertVerificationError` is occurring because the client is trying to verify the server's certificate against the IP address `10.0.0.1`, but the self-signed certificate we generated earlier does not have that IP address as the `Subject Alternative Name` (SAN).

The `Common Name` (`CN`) field in the certificate is only used for identifying the server during the initial handshake. For subsequent verification, the client checks the `Subject Alternative Name` (SAN) field, which should contain the IP address or hostname that the client is connecting to.

To resolve this issue, we need to generate a new self-signed certificate with the IP address `10.0.0.1` added as a SAN. Here's how you can do it:

1. **Generate a new self-signed certificate with the IP address as a SAN**:

   - Run the following command to generate a new self-signed certificate with the IP address `10.0.0.1` as a SAN:

     ```bash
     openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=server" -addext "subjectAltName=IP:10.0.0.1"
     ```

   - This command sets the `Common Name` (`CN`) to `server` and adds the IP address `10.0.0.1` as a SAN using the `-addext` option.
   - Replace the old `cert.pem` and `key.pem` files with the newly generated ones.

2. **Update the server code**:

   - In the server code, update the `load_cert_chain` line to point to the new `cert.pem` and `key.pem` files:

     ```python
     context.load_cert_chain('cert.pem', 'key.pem')
     ```

3. **Update the client code**:

   - In the client code, update the `load_verify_locations` line to point to the new `cert.pem` file:

     ```python
     context.load_verify_locations('cert.pem')
     ```

After making these changes, try running the server and client again. The client should now be able to verify the server's certificate against the IP address `10.0.0.1` and establish a secure SSL/TLS connection.

Note that when you generate a new self-signed certificate, you need to update both the server and the client code to use the new certificate files.


