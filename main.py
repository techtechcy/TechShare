import os

print("""
1: Receive Files
2: Share Files
3: Exit\n
""")

user_input = input(">> ")

if int(user_input) == 1:
    import receive_files
    receive_files.main()

if int(user_input) == 2:
    import share_files
    share_files.main()
    
if int(user_input) == 3:
    pid = os.getpid()
    os.kill(pid, 0)