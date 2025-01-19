from time import sleep
import threading
import requests
import socket
import tqdm
import json
import os


class _Types:
    ERROR = "error"
    WARNING = "warning"
    SUCCESS = "success"
    IMPORTANT = "important"
    DEBUG = "debug"
    ADEBUG = "adebug"
    
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


def force_divide(n1, n2):
    division_result = n1 // n2
    dr_times_10 = division_result*10
    excess = n1 - dr_times_10
    
    return [dr_times_10, division_result, excess]


def prints(type: str, text: str, end_char: str = "", config = None):
    if type == "error":
        print(f"{colors.RED}[@] {text}{colors.ENDC}{end_char}")
    elif type == "warning":
        print(f"{colors.YELLOW}[!] {text}{colors.ENDC}{end_char}")
    elif type == "success":
        print(f"{colors.GREEN}[*] {text}{colors.ENDC}{end_char}")
    elif type == "important":
        print(f"{colors.BOLD}{colors.UNDERLINE}[*] {text}{colors.ENDC}{end_char}")
    elif type == "debug":
        if config is None:
            prints(types.ERROR, "No config object passed to debug prints function")
        if isinstance(config, dict):
            if config["debug_mode"] == True:
                print(f"{colors.CYAN}[DEBUG] {text}{colors.ENDC}{end_char}")
    elif type == "adebug":
        print(f"{colors.CYAN}{text}{colors.ENDC}{end_char}")
        


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
        def __init__(self, config):
            self.myip = requests.get('https://api.ipify.org').text
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            self.config = config
        
        def connect_to_server(self, ip: str, port: int):
            self.server_address = (ip, port)
            
            self.socket.connect(self.server_address)
            prints(types.IMPORTANT, f"Connected to server at {ip}:{port}")
            
            
        def disconnect_from_server(self):
            try:
                prints(type=types.SUCCESS, text=f"Disconnecting from server...")
                self.socket.send("Command~#@#~disconnect".encode())
                self.socket.close()
                
            except Exception as e:
                prints(type=types.ERROR, text=f"Error while disconnecting: {e}", config=self.config)
                
            
        
        def stop(self):
            self.disconnect_from_server()
            self.socket.close()
            prints(types.SUCCESS, "Connection closed", config=self.config)
            
        
        def request_file(self, filename):
            try:
                prints(types.IMPORTANT, f"Requesting file '{filename}' from server...")
                self.socket.send(f"Requesting~%!%~{filename}".encode())
                file_size_response = self.socket.recv(1024).decode()
                
                if file_size_response == "File not found":
                    prints(types.ERROR, f"File '{filename}' not found on server")
                    return
                
                prints(types.DEBUG, f"File Size Response:   {file_size_response}", config=self.config)
         
                try:
                    file_size = int(file_size_response.split("~%!%~")[1])
                except ValueError:
                    prints(types.ERROR, f"Invalid file size response: {file_size_response}, {file_size_response.__class__}")
                    
                
                file_size = int(file_size_response.split("~%!%~")[1])
                
                
                mbfilesize = int((file_size/1048576) * (10**3)) / (10**3)
                
                prints(type=types.ADEBUG, text=f"""File size is: 
{file_size} Bytes
{mbfilesize}Mb""", config=self.config)
                
                if not isinstance(file_size, int):
                    prints(types.ERROR, f"Invalid file size response: {file_size}, with type {file_size.__class__}")
                    return
                
                prints(types.SUCCESS, f"File '{filename}' found on server with size {file_size} bytes")
                
                prints(types.IMPORTANT, f"Receiving file '{filename}'...")
                f = open(os.path.join("Downloads", filename), "wb")
                
                file_bytes = b""
                
                progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1024, total=file_size)
                
                
                
                ### Receive Order ###
                receive_order: list[int] = []
                
                divisible, result, excess = force_divide(file_size, 10)
                for i in range(10):
                    receive_order.append(result)
                    
                receive_order.append(excess)
                receive_order.sort()
                ### ############# ###
    
                
                ### Receive ###
                i = 0
                for bytes_to_receive in receive_order:
                    i = i + 1
                    data = self.socket.recv(bytes_to_receive)
                    file_bytes += data
                    
                    if len(file_bytes) == file_size:
                        done = True
                        
                    progress.update(bytes_to_receive)
                ### ####### ###
                
                file_bytes.replace(b"!<END>!", b"")
                f.write(file_bytes)
                

                progress.write(s=f"{colors.GREEN}[*] File '{filename}' received successfully.{colors.ENDC}")

            except Exception as e:
                prints(types.ERROR, f"Failed to receive file: {e}")
        
    
    
class Server():
    """
    A class to represent a server that handles client connections and file requests.
    Attributes
    ----------
    ip : str
        The IP address of the server.
    port : int
        The port number on which the server listens.
    max_connections : int
        The maximum number of simultaneous connections the server can handle.
    server : socket.socket
        The server socket.
    public_ip : str
        The public IP address of the server.
    server_loop_thread : threading.Thread
        The thread running the server loop.
    server_loop_pid : int
        The process ID of the server loop.
    server_loop_running : bool
        A flag indicating whether the server loop is running.
    config : dict
        Configuration settings for the server.
    Methods
    -------
    start():
        Starts the server and begins listening for connections.
    server_loop(server: socket.socket):
        The main loop that handles incoming client connections.
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
        self.server_loop_running = False
        
        self.config = {
                "debug_mode": False,
                "fake_sleep": 0.5
            }
        
        
        
    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        if self.server is None:
            prints(types.ERROR, "Server socket is not initialized")
            return
        ip = self.ip
        port = self.port

        prints(type=types.DEBUG, text=f"Socket: {self.server}", config=self.config)
    
        self.server.bind((ip, port))
        self.server.listen(self.max_connections)
        prints(types.SUCCESS, f"Server binded on {ip}:{port}")
        
        self.server_loop_running = True
        self.server_loop_thread = threading.Thread(target=self.server_loop, args=(self.server,), name="Server Loop")
        self.server_loop_thread.start()
        
    
    def server_loop(self, server: socket.socket):
        self.server_loop_pid = os.getpid()
        prints(types.SUCCESS, f"Server loop started with PID: {self.server_loop_pid}")
        
        while self.server_loop_running:
            try:
                client, address = server.accept()
                prints(types.SUCCESS, f"Accepted connection from: {address[0]}:{address[1]}")
                threading.Thread(target=self.handle_client, args=(client, address), name=f"Handling {address[0]}:{address[1]}").start()
                
                
            except OSError as e:
                if not self.server_loop_running:
                    break
                prints(types.ERROR, f"OSError: {e}")
                
            except Exception as e:
                prints(types.ERROR, f"Unexpected error: {e}")
            
    
    def handle_client(self, client: socket.socket, address: tuple):
        prints(types.SUCCESS, f"Handling client {address[0]}:{address[1]}")
        try:
            with client:
                while self.server_loop_running:
                    request = client.recv(1024).decode()
                    if request.startswith("Requesting~%!%~"):
                        filename = request.split("~%!%~")[1]
                        prints(types.DEBUG, f"Received request for file '{filename}' from {address[0]}:{address[1]}", config=self.config)
                        
                        if not os.path.exists(os.path.join("server_files", filename)):
                            prints(types.ERROR, f"Requested file '{filename}' does not exist.")
                            client.send("File not found".encode())
                            return
                        
                        f = open(os.path.join("server_files", filename), "rb")
                        prints(type=types.DEBUG, text=f"Sending file size to client...", config=self.config)
                        
                        file_size = int(os.path.getsize(os.path.join("server_files", filename)))
                        client.send(f"File size~%!%~{file_size}".encode())
                        
                        prints(type=types.DEBUG, text=f"Sent file size", config=self.config)
                        
                        
                        
                        prints(type=types.ADEBUG, text=f"Sending file to client...", config=self.config)
                        
                        file_data = f.read()
                        
                        client.sendall(file_data)
                            
                        prints(types.SUCCESS, f"File '{filename}' with size {file_size} bytes sent to {address[0]}:{address[1]}")
                        
                        f.close()
                        
                    elif request.startswith("Command~#@#~"):
                        command = request.split("~#@#~")[1]
                        
                        if command == "disconnect":
                            prints(type=types.DEBUG, text=f"Client {address[0]}:{address[1]} requested a disconnection.", config=self.config)
                            prints(type=types.DEBUG, text=f"Disconnecting client...", config=self.config)
                            break
                            
                        
                    else:
                        prints(types.ERROR, f"Invalid request from {address[0]}:{address[1]}")


                
                
        except Exception as e:
            prints(types.ERROR, f"Error handling client {address[0]}:{address[1]}: {e}")
            
        finally:
            client.close()
            prints(types.SUCCESS, f"Connection closed for {address[0]}:{address[1]}")
            
    
    def stop(self):
        self.server_loop_running = False
        
        if self.server_loop_thread:
            self.server_loop_thread.join(timeout=10)
        try:
            self.server.close()
            prints(types.DEBUG, "Server socket closed", config=self.config)
        except OSError as e:
            prints(types.ERROR, f"Error closing server socket: {e}")
            
        prints(types.SUCCESS, "Server has been stopped")