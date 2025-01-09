import socket
import threading
import signal
import keyboard
import json
from time import sleep

from classes import *
from classes import types as tp
import os

# This is the server file for the file sharing application. It is responsible for handling incoming connections and requests from clients.
def config_loader():
    if not os.path.exists("config.txt"):
        with open("config.json", "w") as f:
            default_config = {
                "debug_mode": False,
            }
            
            f.write(json.dumps(default_config))
        return
    
    with open("config.json", "rw") as f:
        config: dict = json.loads(f.read())
        
        if "debug_mode" not in config:
            prints(tp.WARNING, """"Debug mode" was not found in the config file. Setting to False.""")
            config["debug_mode"] = False
        
        if not isinstance(config["debug_mode"], bool):
            prints(tp.WARNING, """The value for the "Debug mode" config is not boolean. Setting to False.""")
            config["debug_mode"] = False
            
        f.write(json.dumps(config))
            
        globals()["debug_mode"] = config["debug_mode"]
    
    
    prints(type=tp.DEBUG, text=f"Config loaded successfully with values:\n{config}")
    
    if globals()["debug_mode"] == False:
        prints(tp.SUCCESS, "Config loaded successfully.")
        
    return config
    
        

def keybinds_handler(server: Server):
    pass


def command_handler(command: str, server: Server, config: dict):
    if command == "start":
        if server.server_loop_thread.is_alive():
            prints(tp.WARNING, "Server is already running.")
            return
        
        prints(tp.IMPORTANT, "Starting server...")
        sleep(1)
        start_server_thread = threading.Thread(target=server.start, name="Main Server Loop")
        start_server_thread.start()
        start_server_thread.join()
           
    elif command == "test_delay":
        if config["debug_mode"] == True:
            print("Testing delay of 3 seconds...")
            sleep(3)
            print("Delay test complete.")
        
    elif command == "whatsmyip":
        prints(text=f"Your public IP address is {server.public_ip}.", type=tp.SUCCESS)
        
    elif command == "status":
        if server.server_loop_thread.is_alive():
            prints(type=tp.SUCCESS, text="Server is running.")
        else:
            print("Server is not running.")
            
    elif command == "start":
        if server.server_loop_running:
            prints(type=tp.IMPORTANT, text="Server is already running.")
            return
        
        prints(tp.IMPORTANT, "Starting server...")
        sleep(1)
        start_server_thread = threading.Thread(target=server.start, name="Main Server Loop")
        start_server_thread.start()
                
    
        
    elif command == "stop" or command == "exit" or command == "quit" or command == "bye" or command == "shutdown" or command == "stop":
        # stopping_server_thread = threading.Thread(target=server.stop, name="Stopping Server")
        # stopping_server_thread.start()
        # stopping_server_thread.join()
        server.stop()
        
    elif command.startswith("list"):
        if command == "list":
            print("Listing files in server_files directory...")
            files = os.listdir("server_files")
            for file in files:
                print(file)
                
        elif command == "list -l":
            print("Listing files in server_files directory with details...")
            files = os.listdir("server_files")
            for file in files:
                print(file, os.path.getsize(f"server_files/{file}"), "bytes")
                
        else:
            prints(type=tp.WARNING, text="Invalid list argument. Type 'help list' for a list of commands.")
            
        
    elif command.startswith("help"):
        if command == "help":
            print("""Available commands:
    start - Start the server
    stop - Stop the server
    status - Display the status of the server
    help - Display this help message
    list - List files in server_files directory:
        -l - List files in server_files directory with details
    whatsmyip - Display your public IP address
    exit - Stop the server and exit the program""")
            
            prints(type=tp.DEBUG, text="""Available commands:
    test_delay: Test by delaying command handler by 3 seconds""")
        
        else: 
            arg1 = command.split(" ")[1:][0]
            
            if arg1 == "list":
                print("""List commands:
    list - List files in server_files directory
    list -l - List files in server_files directory with details""")
            
    else:
        prints(tp.WARNING, "Invalid command. Type 'help' for a list of commands.")
    

def main():
    config: dict = config_loader()
    
    if not os.path.exists("server_files"):
        os.makedirs("server_files")
        
    
    server = Server(["0.0.0.0", 8081])
    
    def signal_handler(sig, frame):
        prints(tp.IMPORTANT, "Interrupt received, stopping server...")
        server.stop()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    prints(tp.IMPORTANT, "Starting server...")
    sleep(1)
    start_server_thread = threading.Thread(target=server.start, name="Main Server Loop")
    start_server_thread.start()
    
    
    start_server_thread.join()
    sleep(0.5)
    print("Type 'help' for a list of commands.")
    command = input(">> ")
    
    
    while True:
        command_handler_thread = threading.Thread(target=command_handler, args=(command, server, config), name="Server Command Handler")
        command_handler_thread.start()
        
        command_handler_thread.join()
        try:
            command = input(">> ")
            
        except Exception as e:
            prints(tp.ERROR, f"Encountered error in Command Loop: {e}")
            break
        
        
        

if __name__ == "__main__":
    main()