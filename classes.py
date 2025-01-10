import threading
import requests
import socket
import json
import os

class _Types:
    ERROR = "error"
    WARNING = "warning"
    SUCCESS = "success"
    IMPORTANT = "important"
    DEBUG = "debug"
    
    

class _Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    

colors = _Colors()
types = _Types()


def prints(type: str, text: str, end_char: str = ""):
    if type == "error":
        print(f"{colors.RED}[@] {text}{colors.ENDC}{end_char}")
    elif type == "warning":
        print(f"{colors.YELLOW}[!] {text}{colors.ENDC}{end_char}")
    elif type == "success":
        print(f"{colors.GREEN}[*] {text}{colors.ENDC}{end_char}")
    elif type == "important":
        print(f"{colors.BOLD}{colors.UNDERLINE}[*] {text}{colors.ENDC}{end_char}")
    elif type == "debug":
        with open("config.json", "r") as f:
            debug_mode: bool = json.loads(f.read())["debug_mode"]
            
        if debug_mode:
            print(f"{colors.CYAN}[DEBUG] {text}{colors.ENDC}{end_char}")


class Client:
        """
        A client class to handle connections and file requests from a server.
        Attributes:
            myip (str): The IP address of the client.
            sock (socket.socket): The socket object for the client.
        Methods:
            connect_to_server(ip: str, port: int):
                Connects to the server at the specified IP address and port.
                
            stop():
                Closes the connection to the server.
                
            request_file(filename: str):
                Requests a file from the server and saves it to the 'Downloads' directory.
        """
        def __init__(self, ):
            self.myip = requests.get('https://api.ipify.org').text
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        def connect_to_server(self, ip: str, port: int):
            self.server_address = (ip, port)
            
            self.sock.connect(self.server_address)
            prints(types.IMPORTANT, f"Connected to server at {ip}:{port}")
            
        
        def stop(self):
            self.sock.close()
            prints(types.SUCCESS, "Connection closed")
            
        
        def request_file(self, filename):
            try:
                self.sock.send(f"Requesting~%!%~{filename}".encode())
                response = self.sock.recv(1024).decode()
                
                if response == "File not found":
                    prints(types.ERROR, f"File '{filename}' not found on server")
                    return
                
                with open(os.path.join("Downloads", filename), "wb") as f:
                    while True:
                        data = self.sock.recv(1024)
                        if not data:
                            break
                        f.write(data)
                prints(types.SUCCESS, f"File '{filename}' received successfully.")
                
            except Exception as e:
                prints(types.ERROR, f"Failed to receive file: {e}")
        
    
    
class Server():
    """
    A class to represent a server.
    Attributes
    ----------
    ip : str
        The IP address of the server.
    port : int
        The port number of the server.
    max_connections : int
        The maximum number of connections the server can handle.
    server : socket.socket
        The server socket.
    server_loop_pid : int
        The process ID of the server loop.
    Methods
    -------
    start():
        Starts the server and begins listening for connections.
        
    server_loop(server: socket.socket):
        The main loop of the server that accepts and handles client connections.
        
    handle_client(client: socket.socket, address: tuple):
        Handles communication with a connected client.
        
    stop():
        Stops the server and closes the server socket.
    """
    def __init__(self, address: list[str], max_connections: int = 5):
        self.ip = str(address[0])
        self.port = int(address[1])
        self.max_connections = max_connections
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.public_ip = requests.get('https://api.ipify.org').text
        
        self.server_loop_thread: threading.Thread = None
        self.server_loop_pid = None
        
        
    def start(self):
        if self.server is None:
            prints(types.ERROR, "Server socket is not initialized")
            return
        ip = self.ip
        port = self.port

        prints(type=types.DEBUG, text=f"Socket: {self.server}" )
        
        self.server.bind((ip, port))
        self.server.listen(self.max_connections)
        prints(types.SUCCESS, f"Server binded on {ip}:{port}")
        
        self.server_loop_thread = threading.Thread(target=self.server_loop, args=(self.server,), name="Server Loop")
        self.server_loop_thread.start()
        
    
    def server_loop(self, server: socket.socket):
        self.server_loop_pid = os.getpid()
        prints(types.SUCCESS, f"Server loop started with PID: {self.server_loop_pid}")
        
        while self.server_loop_thread.is_alive():
            try:
                client, address = server.accept()
                prints(types.SUCCESS, f"Accepted connection from: {address[0]}:{address[1]}")
                threading.Thread(target=self.handle_client, args=(client, address), name=f"Handling {address[0]}:{address[1]}").start()
                
            except OSError as e:
                if not self.server_loop_thread.is_alive():
                    break
                
            except Exception as e:
                prints(types.ERROR, f"Unexpected error: {e}")
            
    
    def handle_client(self, client: socket.socket, address: tuple):
        prints(types.SUCCESS, f"Handling client {address[0]}:{address[1]}")
        try:
            with client:
                request = client.recv(1024).decode()
                if request.startswith("Requesting~%!%~"):
                    filename = request.split("~%!%~")[1]
                    
                    if not os.path.exists(os.path.join("server_files", filename)):
                        prints(types.ERROR, f"Requested file '{filename}' does not exist.")
                        client.send("File not found".encode())
                        return
                    
                    with open(os.path.join("server_files", filename), "rb") as f:
                        data = f.read(1024)
                        while data:
                            client.send(data)
                            data = f.read(1024)
                        prints(types.SUCCESS, f"File '{filename}' sent to {address[0]}:{address[1]}")
                        
                else:
                    prints(types.ERROR, f"Invalid request from {address[0]}:{address[1]}")
                
                
        except Exception as e:
            prints(types.ERROR, f"Error handling client {address[0]}:{address[1]}: {e}")
            
        finally:
            client.close()
            prints(types.SUCCESS, f"Connection closed for {address[0]}:{address[1]}")
            
    
    def stop(self):
        self._stop_loop(); prints(types.DEBUG, "Server loop killed")
        self.server.close(); prints(types.DEBUG, "Server socket closed")
        prints(types.SUCCESS, "Server has been stopped")
        
    
    def _stop_loop(self):
        pid = self.server_loop_pid
        os.kill(pid, 0)
        prints(types.SUCCESS, f"Server loop with pid {pid} has been killed")