# Sender of the message / TCP client side
import nacl.utils
from nacl.public import PrivateKey, Box
import socket

# Generate keys for Bob
skbob = PrivateKey.generate()
pkbob = skbob.public_key

# Create client side IPV4 socket (AF_INET) and TCP (SOCK_STREAM)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get IP address dynamically by using the host name
ip_addr = socket.gethostbyname(socket.gethostname())

# use dynamic port
port = 8080

# Connect the socket to a server located at a given IP and Port
client_socket.connect((ip_addr, port))

# Recieve message from the server. You must specify the max number of bytes to receive
message = client_socket.recv(1024)
print(message.decode("utf-8"))
