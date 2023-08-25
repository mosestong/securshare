# Receiver of the message / TCP server side
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
import socket
import os
import builtins
import logging
import tqdm

logging.basicConfig(filename='receiver.log', level=logging.INFO)

# For decrypting ordinary messages
def decrypt(message):
    alice_box = Box(skalice, pkbob)
    return alice_box.decrypt(message).decode()

# For decrypting bytes, does not decode bytes to string
def decryptbytes(bytes):
    alice_box = Box(skalice, pkbob)
    return alice_box.decrypt(bytes)

port = 8080
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
# Device's own ip address
# Using 0.0.0.0 to be reachable if device has multiple ip addresses
device_ip = "0.0.0.0"
# device_ip = socket.gethostbyname(socket.gethostname())

# Generate keys for Alice
skalice = PrivateKey.generate()
pkalice = skalice.public_key
print("Skalice:", skalice)
print("Pkalice:", pkalice)


# TODO: Could create this as a function??

# Create a server side socket using IPV4 (AF_INET) and TCP (SOCK_STREAM)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind socket to our local address (IP address, Port)
server_socket.bind((device_ip, port))

# Put socket into listening mode to listen for any possible connections
server_socket.listen()
print(f"[*] Listening as {device_ip}:{port}")
# Accept any incoming connection if any
client_socket, client_address = server_socket.accept()
# Message printed if sender is connected
print(f"[+] {client_address} is connected")

# Send message to client that just connected
client_socket.send(f"Connected to IP address of {socket.gethostbyname(socket.gethostname())}".encode())
# Recieve "connected" message from the server
message = client_socket.recv(BUFFER_SIZE).decode()

if message == "quit":
    client_socket.send("quit".encode())
    print("\nEnding the chat...goodbye!")
    # break
else:
    print(f"\n{message}")

# Exchange public keys
pkalice_encoded = pkalice.encode()
# print("PKALICE_ENCODED:", pkalice_encoded)
client_socket.sendall(pkalice_encoded)
print("PKALICE_ENCODED SENT", pkalice_encoded)
pkbob_encoded = client_socket.recv(BUFFER_SIZE)
print(f"\nPKBOB RECEIVED {pkbob_encoded}")

# Decode
pkbob = PublicKey(pkbob_encoded)

# Receive encrypted file info
file_info_enc = client_socket.recv(BUFFER_SIZE)
print("FILE INFO ENC", file_info_enc)

# Decrypt message using private key
file_info = decrypt(file_info_enc)
print(file_info)

file_name, file_size = file_info.split(SEPARATOR)

# Remove absolute file path if present
file_name = os.path.basename(file_name)

# FOR TESTING PURPOSES: appending 'sent' to file name so that original file won't be overwritten
file_name = "".join(["sent-", file_name])

# Convert to integer
file_size = int(file_size)
print("FILE NAME", file_name)
print("FILE SIZE", file_size)

### PROBLEMS START!

# Start receiving file from socket and writing to the file stream
progress = tqdm.tqdm(range(file_size), f"Receiving {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
with open(file_name, "wb") as f:
    while True:
        # Receive and read 4096 bytes from the socket
        data_enc = client_socket.recv(BUFFER_SIZE)
        print("DATA_ENC:", data_enc)
        if not data_enc:
            # Nothing received and file transmitting is finished
            break
        # Decrypt bytes using keys
        data = decryptbytes(data_enc)
        print("DATA", data)
        # Write to the file the bytes we received
        f.write(data)
        # Update progress bar
        progress.update(len(data))

server_socket.close()
