import socket
import signal
from classes import *
import os
from time import sleep


def command_handler(command: str, client: Client):
    if command == "help":
        print("Commands:")
        print("help - Display this help message")
        print("exit - Stop the client and exit")
        print("request <filename> - Request a file from the server")
        
    elif command == "exit":
        client.stop()
        exit(0)
        
    elif command.startswith("request"):
        filename = command.split(" ")[1]
        client.request_file(filename)
        
    else:
        print("Invalid command. Type 'help' for a list of commands.")

def main():
    if not os.path.exists("Downloads"):
        os.makedirs("Downloads")
    
    client = Client()
    
    def signal_handler(sig, frame):
        print("Interrupt received, stopping client...")
        client.stop()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

    server_ip = input("Enter the sender's IP address: ")
    client.connect_to_server(server_ip, 8081)

    while True:
        command = input(">> ")
        command_handler(command, client)

if __name__ == "__main__":
    main()