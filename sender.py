# Sender of the message / TCP client side
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
import socket
import os
import builtins
import tqdm
import logging

logging.basicConfig(filename='sender.log', level=logging.INFO)
logging.info("\nNew run:\n")

# For sending ordinary messages
def send(message):
    bob_box = Box(skbob, pkalice)
    encrypted = bob_box.encrypt(message.encode())
    print("FILE INFO ENC", encrypted)
    client_socket.sendall(encrypted)

# For sending bytes
def sendbytes(bytes, i):
    bob_box = Box(skbob, pkalice)
    # print("BEFORE ENCRYPT", len(bytes))
    encrypted = bob_box.encrypt(bytes)
    # print("AFTER ENCRYPT", len(encrypted))
    client_socket.sendall(encrypted)
    logging.info(f"{i}: {encrypted}")

# For decrypting ordinary messages
def decrypt(message):
    bob_box = Box(skbob, pkalice)
    return bob_box.decrypt(message).decode()

# use dynamic port
port = 8080
# Host name of the receiver you want to send file to

# TODO: Will use input() to get file name after

file_name = "tower.jpg"
# file_name = "moses-tong-resume.pdf"
# file_name = "proxy-image.jpg"
# file_name = "file.txt"
file_size = os.path.getsize(file_name)
SEPARATOR = "<SEPARATOR>"
# TODO: Possibly allow to change buffer size? 
# prob not though since client and sender would 
# need to have same buf size
BUFFER_SIZE = 1024

# Generate keys for Bob
skbob = PrivateKey.generate()
pkbob = skbob.public_key
print("Skbob:", skbob)
print("Pkbob:", pkbob)

# Create client side IPV4 socket (AF_INET) and TCP (SOCK_STREAM)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# TODO: To be removed in favour of input(), only for testing right now so ip address is set to the same machine
ip_addr = socket.gethostbyname(socket.gethostname())
# ip_addr = input("Enter IP address to send file to: ")

# if ip_addr == "loopback":
#     ip_addr = "localhost"

# Connect the socket to a server located at a given IP and Port
print(f"[+] Connecting to {ip_addr}:{port}")
client_socket.connect((ip_addr, port))
print(f"[+] Connected")

# NOTE: Removed because connect message and public key data have possibility of merging
    # Would need to send "OK" confirmation before sending key data

# # Send message to client that just connected
# client_socket.sendall(f"Connected to IP address of {socket.gethostbyname(socket.gethostname())}".encode())
# # Recieve "connected" message from the server
# try:
#     message = client_socket.recv(BUFFER_SIZE)
#     print(message.decode())
# except UnicodeDecodeError:
#     print("Received message couldn't be decoded as UTF-8")
#     print(f"Raw bytes: {message}")

# if message == "quit":
#     client_socket.send("quit".encode())
#     print("\nEnding the chat...goodbye!")
#     # break
# else:
#     print(f"\n{message}")

# Exchange public keys
pkbob_encoded = pkbob.encode()
client_socket.sendall(pkbob_encoded)
print("PKBOB_ENCODED SENT:", pkbob_encoded)
pkalice = client_socket.recv(BUFFER_SIZE)
print(f"\nPKALICE RECEIVED {pkalice}")

# Convert bytes back into PulicKey object
pkalice = PublicKey(pkalice)

# Send the name and size of the file
send(f"{file_name}{SEPARATOR}{file_size}")
print("FILE NAME", file_name)
print("FILE SIZE", file_size)

# Receive "OK" message before sending file
ok_enc = client_socket.recv(BUFFER_SIZE)
print("OK ENC", ok_enc)

# Decrypt ok message using private key
ok = decrypt(ok_enc)
print("OK", ok)

# Start sending file once recieved confirmation of ready to accept
if ok == "OK":
    # start sending file
    progress = tqdm.tqdm(range(file_size), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024, total=int(file_size))
    i = 0
    # Read file in chunks and send to socket
    with open(file_name, "rb") as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            sendbytes(data, i)
            i += 1
            progress.update(len(data))
else:
    print(f"Did not receive OK. File transfer failed.")

client_socket.close()

