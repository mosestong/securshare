# Receiver of the message / TCP server side
import nacl.utils
from nacl.public import PrivateKey, Box
import socket

# Generate keys for Alice
skalice = PrivateKey.generate()
pkalice = skalice.public_key

""" Could create this as a function??"""

# Create a server side socket using IPV4 (AF_INET) and TCP (SOCK_STREAM)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# use dynamic port
port = 8080
# get host name
host = socket.gethostname()

# Get IP address dynamically by using the host name
ip_addr = socket.gethostbyname(host)

print("Host name:", host)
print("IP address:", ip_addr)

# Bind socket to tuple (IP address, Port address)
server_socket.bind((ip_addr, port))

# Put socket into listening mode to listen for any possible connections
server_socket.listen()

# Listen forever to accept ANY connection
while True:
    # Accept every single connection and obtain socket object and address of incoming connection
    client_socket, client_address = server_socket.accept()
    # print(type(client_socket))
    # print(client_socket)
    # print(type(client_address))
    # print(client_address)

    print(f"Connected to {client_address}")

    # Send message to client that just connected
    client_socket.send(f"Connected to {host} with IP address of {ip_addr}".encode('utf-8'))

    # Close connection and break out of infinite loop
    server_socket.close()
    break
