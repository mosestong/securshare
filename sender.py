# Sender of the message / TCP client side
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
import socket
import os
import builtins
import tqdm

# For sending ordinary messages
def send(message):
    bob_box = Box(skbob, pkalice)
    encrypted = bob_box.encrypt(message.encode())
    print("FILE INFO ENC", encrypted)
    client_socket.sendall(encrypted)

# For sending bytes
def sendbytes(bytes):
    bob_box = Box(skbob, pkalice)
    encrypted = bob_box.encrypt(bytes)
    client_socket.sendall(encrypted)

# For decrypting ordinary messages
def decrypt(message):
    bob_box = Box(skbob, pkalice)
    return bob_box.decrypt(message).decode()

# use dynamic port
port = 8080
# Host name of the receiver you want to send file to

# TODO: Will use input() to get file name after

file_name = "file.txt"
file_size = os.path.getsize(file_name)
SEPARATOR = "<SEPARATOR>"
# TODO: Possibly allow to change buffer size? 
# prob not though since client and sender would 
# need to have same buf size
BUFFER_SIZE = 4096

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

# Send message to client that just connected
client_socket.send(f"Connected to IP address of {socket.gethostbyname(socket.gethostname())}".encode())
# Recieve "connected" message from the server
message = client_socket.recv(BUFFER_SIZE).decode()
print(message)

if message == "quit":
    client_socket.send("quit".encode())
    print("\nEnding the chat...goodbye!")
    # break
else:
    print(f"\n{message}")

# Exchange public keys
pkbob_encoded = pkbob.encode()
client_socket.sendall(pkbob_encoded)
print("PKBOB_ENCODED SENT:", pkbob_encoded)
pkalice = client_socket.recv(BUFFER_SIZE)
print(f"\nPKALICE RECEIVED {pkalice}")

# TODO: Exception if PKALICE is empty, ie not sent correctly

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

if ok == "OK":
    ### PROBLEMS START! 

    # start sending file
    progress = tqdm.tqdm(range(file_size), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)

    # Read file in chunks and send to socket
    with open(file_name, "rb") as f:
        while True:
            data = f.read(BUFFER_SIZE)
            print("DATA", data)
            if not data:
                # file transmitting is done
                break
            sendbytes(data)
            progress.update(len(data))
else:
    print(f"Did not receive OK. Received {ok}.")

client_socket.close()

