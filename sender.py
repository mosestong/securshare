# Sender of the message / TCP client side
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
import socket
import os
import builtins

def send(message):
    bob_box = Box(skbob, pkalice_decoded)
    encrypted = bob_box.encrypt(message.encode())
    client_socket.send(encrypted)

# Generate keys for Bob
skbob = PrivateKey.generate()
pkbob = skbob.public_key
print("Skbob:", skbob)
print("Pkbob:", pkbob)

# Create client side IPV4 socket (AF_INET) and TCP (SOCK_STREAM)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# use dynamic port
port = 8080
host = socket.gethostname()

# Get IP address dynamically by using the host name
ip_addr = socket.gethostbyname(host)

# Connect the socket to a server located at a given IP and Port
client_socket.connect((ip_addr, port))

# Send message to client that just connected
client_socket.send(f"Connected to {host} with IP address of {ip_addr}".encode())
# Recieve "connected" message from the server
# while True:
message = client_socket.recv(1024).decode()

if message == "quit":
    client_socket.send("quit".encode())
    print("\nEnding the chat...goodbye!")
    # break
else:
    print(f"\n{message}")

# Exchange public keys
pkbob_encoded = pkbob.encode()
print("PKBOB_ENCODED:", pkbob_encoded)
client_socket.send(pkbob_encoded)
pkalice_decoded = client_socket.recv(1024)
print(f"\n{pkalice_decoded}")

# Decode
pkalice_decoded = PublicKey(pkalice_decoded)

send("hello")

client_socket.close()

