# Class for sending out data on a socket server

import socket
import threading
import time
import imageProtocall

class SocketServer:
    host = ''   # Setting it up to be accessible by any ip.
    port = 123  # TCP/IP port
    clients = []  # List of all clients.

    runSocketServer = False
    curPacket = None
    currentConnection = None    #Server connection.

    curReceivedData = None

    frameRate = 10

    def __init__(self, ipaddress, port, camera):
        self.host = ipaddress
        self.port = port

        #Setting up the protocall for one camera.
        self.curPacket = imageProtocall.ImageProtocall(0, camera)

    #Sets up the socket server thread and starts it.
    def startServer(self):
        self.runSocketServer = True     #setting the server control to run (true)
        t = threading.Thread(target=self.threadRunSever, args=())
        t.start()

        r = threading.Thread(target=self.threadIncomingData, args=())
        r.start()



    def stopServer(self):
        self.runSocketServer = False

    def setFrameRate(self, rate):
        self.frameRate = rate

    #Thread for sending out data.
    def threadRunSever(self):
        while(self.runSocketServer):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                s.listen()
                conn, addr = s.accept()
                #with conn:
                print('Connected by', addr)

                # Starting a server connection for this client.
                t = threading.Thread(target=self.on_new_client, args=(conn, addr,))
                t.start()

                # self.currentConnection = conn   #Passing out the connection to main.
                # while True:
                #     #data = conn.recv(1024)
                #     #print('Data in: ', data)
                #    # if not data:
                #     #    break
                #
                #
                #     # Loading file.
                #     self.curPacket.loadImage('cash0.jpg')
                #     data = self.curPacket.getFullImagePacket()
                #
                #     try:
                #         conn.sendall(data)
                #     except:
                #         break
                #     time.sleep(1/self.frameRate)


            time.sleep(0.1)

        print('Socket server stopped.')

    def on_new_client(self, clientsocket, addr):

        # Adding client to list
        self.clients.append(clientsocket)

        while True:
            # data = conn.recv(1024)
            # print('Data in: ', data)
            # if not data:
            #    break

            # Loading file.
            self.curPacket.loadImage('cash0.jpg')
            data = self.curPacket.getFullImagePacket()

            try:
                clientsocket.sendall(data)
                #self.sendToAll(data)
            except:
                break
            time.sleep(1 / self.frameRate)
        #clientsocket.close()

    def sendToAll(self, data):
        for c in self.clients:
            c.sendall(data)

    def threadIncomingData(self):
        while(self.runSocketServer == True):
            if(self.currentConnection != None):
                data = self.currentConnection.recv(1024)
                if not data:
                    time.sleep(1)
                else:
                    self.curReceivedData = data
