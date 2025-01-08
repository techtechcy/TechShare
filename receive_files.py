import socket
import signal
from classes import *
import os
from time import sleep

def main():
    if not os.path.exists("Downloads"):
        os.makedirs("Downloads")
    
    client = Client()
    
    def signal_handler(sig, frame):
        prints(types.IMPORTANT, "Interrupt received, stopping client...")
        client.stop()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    client.connect_to_server("127.0.0.1", 8081)
    client.request_file("test.txt")

if __name__ == "__main__":
    main()