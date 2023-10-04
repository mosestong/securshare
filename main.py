import receiver
import sender
import click
import os

@click.group()
def main():
    """
    CLI application for encyrpted file transfer
    """
    pass

@main.command()
@click.option("--port", default=8080, help="Port number for receiving files (default: 8080)")
@click.option("--path", default='.', help='Path where file should be transferred to, creates directory if not exists')
def receive(path, port):
    """Receive file from sender"""
    if not os.path.isdir(path):
        os.makedirs(path)
    receiver.receive(path, port)
        

@main.command()
# @click.argument("files", nargs=-1, type=click.Path(exists=True))
# @click.argument("files", nargs=-1)
@click.argument("files", type=click.Path(exists=True), nargs=-1)
@click.option("--dest", default='localhost', help='IP destination to send file to')
@click.option("--port", default=8080, help="Port number to send file to (default: 8080)")
# @click.option("--compress", default=False, help="Compress files to zip or tar")
def send(files, dest, port):
    """Send file to receiver"""
    sender.send(files, dest, port)

if __name__ == "__main__":
    main()