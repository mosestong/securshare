from nacl.public import Box, PrivateKey, PublicKey
import socket
import os
import logging
import tqdm

logging.basicConfig(filename='receiver.log', level=logging.INFO)
logging.info("\nNew run:\n")

# Class responsible for encryption and decryption using NaCl library
class EncryptionHandler:
    def __init__(self, skalice, pkbob):
        self.box = Box(skalice, pkbob)

    def encrypt(self, message):
        encrypted = self.box.encrypt(message.encode())
        return encrypted

    def decrypt(self, message):
        return self.box.decrypt(message).decode()
    
    def decryptbytes(self, bytes):
        return self.box.decrypt(bytes)

# Class to manage the server-side socket
class Server:
    def __init__(self, host, port, buffer_size=1064):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.server_socket = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"[*] Listening as {self.host}:{self.port}")

    def accept_client(self):
        client_socket, client_address = self.server_socket.accept()
        print(f"[+] {client_address} is connected")
        return client_socket
    
    def close(self):
        self.server_socket.close()

# Class to handle receiving and processing of files
class FileReceiver:
    def __init__(self, client_socket, encryption_handler, buffer_size=1064):
        self.client_socket = client_socket
        self.encryption_handler = encryption_handler
        self.buffer_size = buffer_size

    def send_response(self, message):
        encrypted = self.encryption_handler.encrypt(message)
        self.client_socket.sendall(encrypted)

    def receive_file(self, file_path, file_name, file_size):
        with open(os.path.join(file_path, file_name), "wb") as f:
            progress = tqdm.tqdm(range(file_size), f"Receiving {file_name}", unit="B", unit_scale=True, unit_divisor=1064, total=int(file_size * 1.04))
            file_bytes = b""

            while True:
                data_enc = self.client_socket.recv(self.buffer_size)
                # No more data to transmit
                if not data_enc:
                    break

                data = self.encryption_handler.decryptbytes(data_enc)
                file_bytes += data
                progress.update(len(data_enc))

            f.write(file_bytes)

        # TODO: Decide whether this needs to be closed
        self.client_socket.close()

def receive(file_path="", port=8080):
    device_ip = "0.0.0.0"

    skalice = PrivateKey.generate()
    pkalice = skalice.public_key

    # Initialize the server and start listening for connections on specified port
    server = Server(device_ip, port)
    server.start()

    # Accept the client connection
    client_socket = server.accept_client()

    # Send public key and receive peer's public key
    pkalice_encoded = pkalice.encode()
    client_socket.sendall(pkalice_encoded)
    pkbob = client_socket.recv(server.buffer_size)
    pkbob = PublicKey(pkbob)

    # Create an EncryptionHandler instance for secure communication
    encryption_handler = EncryptionHandler(skalice, pkbob)

    # Receive encrypted file info and decrypt it
    file_info_enc = client_socket.recv(server.buffer_size)
    file_info = encryption_handler.decrypt(file_info_enc)
    file_name, file_size = file_info.split("<SEPARATOR>")
    # Remove absolute file path if present
    file_name = os.path.basename(file_name)
    # Appending sent to file name so that original file won't be overwritten
    file_name = "".join(["sent-", file_name])
    file_size = int(file_size)

    # Initialize the Receiver to handle file reception
    receiver = FileReceiver(client_socket, encryption_handler, server.buffer_size)
    receiver.send_response("OK")
    receiver.receive_file(file_path, file_name, file_size)
    server.close()

# if __name__ == "__main__":
#     receive()
