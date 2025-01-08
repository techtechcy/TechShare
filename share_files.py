import socket
import threading
import signal
from time import sleep

from classes import *
import os

def main():
    if not os.path.exists("server_files"):
        os.makedirs("server_files")
        
    
    server = Server(["0.0.0.0", 8081])
    
    def signal_handler(sig, frame):
        prints(types.IMPORTANT, "Interrupt received, stopping server...")
        server.stop()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    server.start()
    
    # Keep the main thread alive to handle signals
    while True:
        sleep(1)

if __name__ == "__main__":
    main()