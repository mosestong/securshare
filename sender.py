# Sender of the message / TCP client side
from nacl.public import Box, PrivateKey, PublicKey
import socket
import os
import tqdm

# Class responsible for encryption and decryption using NaCl library
class EncryptionHandler:
    def __init__(self, skbob, pkalice):
        self.box = Box(skbob, pkalice)

    def encrypt(self, data):
        encrypted = self.box.encrypt(data)
        return encrypted

    def decrypt(self, data):
        return self.box.decrypt(data).decode()
    
# Class responsible for sending files securely over a network connection
class FileSender:
    def __init__(self, destination_ip, destination_port, buffer_size=1024):
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.buffer_size = int(buffer_size)
        self.encryption_handler = None
        self.skbob = PrivateKey.generate()
        self.pkbob = self.skbob.public_key
        self.client_socket = None
        self.pkalice = None
        
    def key_exchange(self):
        pkbob_encoded = self.pkbob.encode()
        self.client_socket.sendall(pkbob_encoded)
        pkalice_bytes = self.client_socket.recv(self.buffer_size)
        self.pkalice = PublicKey(pkalice_bytes)
        
    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[+] Connecting to {self.destination_ip}:{self.destination_port}")
        self.client_socket.connect((self.destination_ip, self.destination_port))
        print(f"[+] Connected")
        
    def close(self):
        self.client_socket.close()

    def send_message(self, message):
        encrypted = self.encryption_handler.encrypt(message.encode())
        self.client_socket.sendall(encrypted)
        
    def _send_bytes(self, bytes):
        encrypted = self.encryption_handler.encrypt(bytes)
        self.client_socket.sendall(encrypted)

    def send_file(self, file_name):
        if self.client_socket == None:
            print("Must connect to server before sending!")
        if self.pkalice == None:
            self.key_exchange()

        # Send file name and size
        file_size = os.path.getsize(file_name)
        separator = "<SEPARATOR>"
        file_info = f"{file_name}{separator}{file_size}"
        self.encryption_handler =  EncryptionHandler(self.skbob, self.pkalice)
        self.send_message(file_info)

        # Receive "OK" message before sending the file
        ok_enc = self.client_socket.recv(self.buffer_size)
        ok = self.encryption_handler.decrypt(ok_enc)

        # Start sending file once recieved confirmation of ready to accept
        if ok == "OK":
            # Sending the file in chunks
            progress = tqdm.tqdm(range(file_size), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024, total=int(file_size))
            i = 0

            with open(file_name, "rb") as f:
                while True:
                    data = f.read(self.buffer_size)
                    if not data:
                        break
                    self._send_bytes(data)
                    i += 1
                    progress.update(len(data))
        else:
            print(f"Did not receive OK. File transfer failed.")


def sender():
    destination_ip = socket.gethostbyname(socket.gethostname())
    destination_port = 8080
    file_name = "file.txt"

    sender = FileSender(destination_ip, destination_port)
    sender.connect()
    sender.send_file(file_name)
    sender.close()

if __name__ == "__main__":
    sender()