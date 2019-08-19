#!/usr/bin/env python3

import socket
import threading
import time

HOST = ''  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

runServer = False   # Controls the server running state.



def threadSocketServer(state):
    runServer = state

    while runServer:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    print('Data in: ', data)
                    if not data:
                        break
                    conn.sendall(data)
                    time.sleep(0.01)

        time.sleep(0.1)

    print('Server Ended')


#Starting the main server program.
def main():
    print('Starting socket server')
    runServer = True
    t = threading.Thread(target=threadSocketServer, args=(runServer,))
    t.start()

    command = ''
    while command != "exit":
        command = input("Command:")


if __name__ == '__main__':
    main()