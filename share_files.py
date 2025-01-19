import socket
import threading
import keyboard
import json
from time import sleep

from classes import *
from classes import types as tp
import os

### This is the server file for the file sharing application. It is responsible for handling incoming connections and requests from clients. ###


def config_loader():
    if not os.path.exists("config.json"):
        prints(tp.WARNING, """"The config file was not found. Creating a new one with default values...""")
        with open("config.json", "w") as f:
            default_config = {
                "debug_mode": False,
                "fake_sleep": 0.5
            }
            
            f.write(json.dumps(default_config))
        return default_config
    
    
    with open("config.json", "r+") as f:
        config = json.loads(f.read())
        f.seek(0)
        
        try:
            if not isinstance(config["debug_mode"], bool):
                prints(tp.WARNING, """The value for the "Debug mode" config is not boolean. Setting to False.""")
                prints(type=tp.ADEBUG, text=f"debug_mode value & type: {config['debug_mode']}, {config['debug_mode'].__class__}")
                config["debug_mode"] = False
        except KeyError:
            prints(tp.WARNING, """The value for the "Debug Mode" config was not found. Setting to False.""")
            config["debug_mode"] = False
            
        
        try:
            if not isinstance(config["fake_sleep"], float) and not isinstance(config["fake_sleep"], int):
                prints(tp.WARNING, """The value for the "Fake sleep" config is not a float or integer. Setting to 0.5.""")
                prints(type=tp.DEBUG, text=f"fake_sleep value & type: {config['fake_sleep']}, {config['fake_sleep'].__class__}", config=config)
            config["fake_sleep"] = 0.5
        except KeyError:
            prints(tp.WARNING, """The value for the "Fake sleep" config was not found. Setting to 0.5.""")
            config["fake_sleep"] = 0.5
            
        f.write(json.dumps(config))
        f.truncate()
    

    prints(type=tp.DEBUG, text=f"Config loaded successfully with values:\n{config}", config=config)
    
    return config

def command_handler(command: str, server: Server, config: dict):
    if command.lower() == "start":
        if server.server_loop_thread.is_alive():
            prints(tp.WARNING, "Server is already running.")
            return
        
        prints(tp.IMPORTANT, "Starting server...")
        sleep(1)
        start_server_thread = threading.Thread(target=server.start, name="Main Server Loop")
        start_server_thread.start()
        start_server_thread.join()
           
    elif command.lower() == "test_delay":
        if config["debug_mode"] == True:
            print("Testing delay of 3 seconds...")
            sleep(3)
            print("Delay test complete.")
        
    elif command.lower() == "whatsmyip":
        prints(text=f"Your public IP address is {server.public_ip}.", type=tp.SUCCESS)
        
    elif command.lower() == "status":
        if server.server_loop_thread.is_alive():
            prints(type=tp.SUCCESS, text="Server is running.")
        else:
            prints(type=tp.SUCCESS, text="Server is not running.")
            
    elif command.lower() == "start":
        if server.server_loop_running:
            prints(type=tp.IMPORTANT, text="Server is already running.")
            return
        
        prints(tp.IMPORTANT, "Starting server...")
        sleep(1)
        start_server_thread = threading.Thread(target=server.start, name="Main Server Loop")
        start_server_thread.start()
                
    
        
    elif command.lower() == "stop" or command.lower() == "exit" or command.lower()== "quit" or command.lower() == "bye" or command.lower() == "shutdown" or command.lower() == "stop":
        prints(tp.IMPORTANT, "Stopping server...")
        prints(tp.IMPORTANT, "This can take up to 10 seconds.")
        server.stop()
        
        
    elif command.lower().startswith("list") or command.lower().startswith("ls") or command.lower().startswith("dir"):  
        try:
            arg1 = command.split(" ")[1:][0].lower()
            
        except:
            files = os.listdir("server_files")
            for file in files:
                print(file)
                return
           
        if arg1 == "-l":
            files = os.listdir("server_files")
            for file in files:
                print(file, os.path.getsize(f"server_files/{file}"), "bytes")
                
        else:
            prints(type=tp.WARNING, text="Invalid list command. Type 'help list' for a list of list commands.")
            
            
    elif command.lower().startswith("cls") or command.lower().startswith("clear"):
        os.system("cls" if os.name == "nt" else "clear")
            
    elif command.lower().startswith("restart"):
        prints(tp.IMPORTANT, "Restarting server...")
        prints(tp.IMPORTANT, "This can take up to 20 seconds.")
        if server.server_loop_running:
            server.stop()
        
        start_server_thread = threading.Thread(target=server.start, name="Main Server Loop")
        start_server_thread.start()
        start_server_thread.join(timeout=30)
        sleep(config["fake_sleep"])
    
            
    elif command.startswith("help"):
        if command == "help":
            print("""Available commands:
    start - Start the server
    stop - Stop the server
    restart - Restart the server
    status - Display the status of the server
    help - Display this help message
    list - List files in server_files directory:
        -l - List files in server_files directory with details
    whatsmyip - Display your public IP address
    exit,quit - Stop the server
    clear,cls - Clear the console""")
            
            prints(type=tp.DEBUG, text="""Available commands:
    test_delay: Test by delaying command handler by 3 seconds""", config=config)
        
        else: 
            arg1 = command.split(" ")[1:][0]
            
            if arg1 == "list":
                print("""List commands:
    list - List files in server_files directory
    list -l - List files in server_files directory with details""")
            
    else:
        prints(tp.WARNING, "Invalid command. Type 'help' for a list of commands.")


def main():
    config = config_loader(); print(f"Config: {config}")
    
    if not os.path.exists("server_files"):
        os.makedirs("server_files")
        
    server = Server(["0.0.0.0", 8081])
    server.config = config
    
    def exit_program():
        prints(tp.IMPORTANT, "Stopping server...")
        server.stop()
        exit(0)
    
    
    prints(tp.IMPORTANT, "Starting server...")
    start_server_thread = threading.Thread(target=server.start, name="Main Server Loop")
    start_server_thread.start()
    
    start_server_thread.join()
    sleep(config["fake_sleep"])
    print("Type 'help' for a list of commands.")
    
    while True:
        try:
            command = input(">> ")
            command_handler(command, server, config)
            
        except KeyboardInterrupt:
            exit_program()    
            
        except Exception as e:
            prints(tp.ERROR, f"Encountered error in Command Loop: {e}")

if __name__ == "__main__":
    main()