import socket               # Import socket module
import threading
import time

s = socket.socket()         # Create a socket object
host = '' ##socket.gethostname() # Get local machine name
port = 1234                # Reserve a port for your service.
clients = []                # List of all clients.
runServers = True          # Controls all server levels.


def on_new_client(clientsocket,addr):

    #Adding client to list
    clients.append(clientsocket)

    while runServers:
        msg = clientsocket.recv(1024)
        #do some checks and if msg == someWeirdSignal: break:
        print(addr, ' >> ', msg)
        #msg = raw_input('SERVER >> ')
        #Maybe some code to compute the last digit of PI, play game or anything else can go here and when you are done.
        clientsocket.send(msg)
    clientsocket.close()


def threadStartServer(state):



    print('Server started!')
    print('Waiting for clients...')

    s.bind((host, port))  # Bind to the port
    s.listen(5)  # Now wait for client connection.


    while runServers:

        if len(clients) < 5:
            c, addr = s.accept()  # Establish connection with client.
            print('Got connection from', addr)
            t = threading.Thread(target=on_new_client, args=(c, addr,))
            t.start()
            # thread.start_new_thread(on_new_client, (c, addr))
            # Note it's (addr,) not (addr) because second parameter is a tuple
            # Edit: (c,addr)
            # that's how you pass arguments to functions when creating new threads using thread module.
    s.close()

def sendToAll(data):
    for c in clients:
        c.send(data)

#Starting the main server program.
def main():

    runServers = True

    t = threading.Thread(target=threadStartServer, args=(runServers,))
    t.start()

    command = ''
    while command != "exit":

        if command == "send":
            for lp in range(10000):
                sendToAll("This is a long command data just to push data out to all clients... This is just a random stuff from my brain.".encode())
                time.sleep(.01)

        if command == "stop":
            runServers = False


        command = input("Command:")


if __name__ == '__main__':
    main()