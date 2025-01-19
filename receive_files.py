import socket
import signal
from classes import *
from classes import types as tp
import os
import json
from time import sleep

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


def command_handler(command: str, client: Client):
    if command == "help":
        print("""
Commands:
    help - Display this help message
    exit - Stop the client and exit
    connect <server ip> - Connect to a server
    request <filename> - Request a file from the server
    disconnect - Disconnect from the connected server
        """)
        
    elif command.lower().startswith("exit"):
        client.stop()
        exit(0)
        
    elif command.lower().startswith("connect"):
        server_ip = command.split(" ")[1]
        client.connect_to_server(server_ip, 8081)
        
    elif command.lower().startswith("request"):
        filename = command.split(" ")[1]
        client.request_file(filename)
        
    elif command.lower().startswith("disconnect") or command.lower().startswith("ds"):
        client.disconnect_from_server()
        
    else:
        print("Invalid command. Type 'help' for a list of commands.")

def main():
    os.system("cls" if os.name == "nt" else "clear")
    prints(tp.IMPORTANT, "Starting client...")
    
    config = config_loader()
    
    if not os.path.exists("Downloads"):
        os.makedirs("Downloads")
    
    client = Client(config)
    
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