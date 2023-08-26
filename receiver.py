# Receiver of the message / TCP server side
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
import socket
import os
import builtins
import logging
import tqdm

logging.basicConfig(filename='receiver.log', level=logging.INFO)
logging.info("\nNew run:\n")

# For sending ordinary messages
def send(message):
    alice_box = Box(skalice, pkbob)
    encrypted = alice_box.encrypt(message.encode())
    print("ENC MESSAGE", encrypted)
    client_socket.sendall(encrypted)

# For decrypting ordinary messages
def decrypt(message):
    alice_box = Box(skalice, pkbob)
    return alice_box.decrypt(message).decode()

# For decrypting bytes, does not decode bytes to string
def decryptbytes(bytes):
    alice_box = Box(skalice, pkbob)
    return alice_box.decrypt(bytes)

port = 8080

# NOTE: Buffer size must always be 40 bytes more than the sender because encryption will pad with 40 more bytes automatically

BUFFER_SIZE = 1064
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

# NOTE: Removed because connect message and public key data have possibility of merging
    # Would need to send "OK" confirmation before sending key data

# # Send message to client that just connected
# client_socket.sendall(f"Connected to IP address of {socket.gethostbyname(socket.gethostname())}".encode())
# # Recieve "connected" message from the server
# message = client_socket.recv(BUFFER_SIZE).decode()

# if message == "quit":
#     client_socket.send("quit".encode())
#     print("\nEnding the chat...goodbye!")
#     # break
# else:
#     print(f"\n{message}")

# Exchange public keys
pkalice_encoded = pkalice.encode()
client_socket.sendall(pkalice_encoded)
print("PKALICE_ENCODED SENT", pkalice_encoded)
pkbob = client_socket.recv(BUFFER_SIZE)
print(f"\nPKBOB RECEIVED {pkbob}")

# Convert bytes back into PublicKey object
pkbob = PublicKey(pkbob)

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

##### TEST
# Send ok before transmitting file to ensure clients are in sync and to avoid mixing packets together/out-of-order delivery
# OR: Append <END> label to every packet to know when packet ends and remove once accepted?
send("OK")

# Start receiving file from socket and writing to the file stream
progress = tqdm.tqdm(range(file_size), f"Receiving {file_name}", unit="B", unit_scale=True, unit_divisor=1064, total=int(file_size * 1.04))
file_bytes = b""

i = 0
with open(file_name, "wb") as f:
    while True:
        # Receive and read x bytes from the socket
        data_enc = client_socket.recv(BUFFER_SIZE)
        # No more data to transmit
        if not data_enc:
            logging.info(f"Received empty")
            break
        # logging.info(f"DATA_ENC: {data_enc}")
        # # Decrypt bytes using keys
        try:
            data = decryptbytes(data_enc)
        except nacl.exceptions.CryptoError:
            logging.info(f"{i}: Failed: {data_enc}")
        else:
            logging.info(f"{i}: Success")
        finally:
            i += 1
        # print("DECRYPTED", data)
        file_bytes += data
        # Update progress bar
        progress.update(len(data_enc))

    # Write to file decrypted bytes
    f.write(file_bytes)

server_socket.close()
