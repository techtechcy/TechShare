import threading
import socket
import os

def prints(type: str, text: str, end_char: str = ""):
    if type == "error":
        print(f"{colors.RED}[@] {text}{colors.ENDC}{end_char}")
        
    if type == "warning":
        print(f"{colors.YELLOW}[!] {text}{colors.ENDC}{end_char}")
        
    if type == "success":
        print(f"{colors.GREEN}[*] {text}{colors.ENDC}{end_char}")
        
    if type == "important":
        print(f"{colors.BOLD}{colors.UNDERLINE}[*] {text}{colors.ENDC}{end_char}")
        

class types:
        ERROR = "error"
        WARNING = "warning"
        SUCCESS = "success"
        IMPORTANT = "important"

class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Client():
    def __init__(self, address):
        self.ip = address[0]
        self.port = address[1]
        
        
    
    
class Server():
    def __init__(self, address: list[str], max_connections: int = 5):
        self.ip = address[0]
        self.port = int(address[1])
        self.max_connections = max_connections
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_loop_pid: int = None
        
        
    def start(self):
        if self.server == None:
            prints(types)
        ip = self.ip
        port = self.port

        self.server.bind((ip, port,))
        self.server.listen(self.max_connections)
        prints(types.SUCCESS, f"Server binded on {ip}:{port}")
        
        threading.Thread(target=self.server_loop, args=(self.server,))
        
        
    
    def server_loop(self, server: socket.socket):
        self.server_loop_pid = os.getpid()
        prints(types.SUCCESS, f"Server loop started: {self.server_loop_pid}", end_char="\n")
        
        while True:
            client, address = server.accept()
            prints(types.IMPORTANT, f"Accepted connection from: {address[0]}:{address[1]}")
            
            
            
            
    
            
            
        