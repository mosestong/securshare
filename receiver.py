# Receiver of the message / TCP server side
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
import socket
import os
import builtins

# Generate keys for Alice
skalice = PrivateKey.generate()
pkalice = skalice.public_key
print("Skalice:", skalice)
print("Pkalice:", pkalice)


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
client_socket, client_address = server_socket.accept()

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
pkalice_encoded = pkalice.encode()
# print("PKALICE_ENCODED:", pkalice_encoded)
client_socket.send(pkalice_encoded)
pkbob_encoded = client_socket.recv(1024)
# print(f"\n{pkbob_encoded}")

# Decode
pkbob = PublicKey(pkbob_encoded)

# RECIEVE ENCRYPTED FILE SIZE FIRST TO KNOW WHAT APPROPRIATE BUFSIZE SHOULD BE

# Recieve encrypted file/message
encrypted = client_socket.recv(1024)

# print("ENCRYPTED MESSAGE", encrypted)

# Decrypt message using private key
alice_box = Box(skalice, pkbob)
plaintext = alice_box.decrypt(encrypted)
print(plaintext.decode())

server_socket.close()
