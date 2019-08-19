# Class for clint to connect to the server.

import socket
import imageProtocall
import threading
import time
import numpy as np
import cv2
import datetime

class SocketClient:
    host = '127.0.0.1'      # default ip address
    port = 123              # defailt port

    runClient = False

    dataBuffer = bytearray()    # container for the raw incoming data.

    showDebug = False   #Controls showing debug information

    curConnection = None    #Current connection.

    def __init__(self, ipaddress, port):
        print('Setting up the socket client')
        self.host = ipaddress
        self.port = port

    def clientConnect(self):
        print('Connecting to: ', self.host + ':' + str(self.port))

        #Starting decoding
        self.runClient = True
        t = threading.Thread(target=self.threadDecodePacket, args=())
        t.start()

        r = threading.Thread(target=self.threadReceiveData, args=())
        r.start()

    def clientDisconnect(self):
        self.runClient = False

    def setDebugMode(self, mode):
        self.showDebug = mode

    def threadReceiveData(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            self.curConnection = s      #Passing out the connection.
            while(self.runClient):

                # s.sendall(b'Hello, world')
                #data = s.recv(1024)
                data = s.recv(200000)

                self.dataBuffer += bytearray(data)

    def threadDecodePacket(self):
        while(self.runClient):
            if len(self.dataBuffer) >= 4:       #Checking to see if there is data in the buffer.

                #Looping through data.
                for i, item in enumerate(self.dataBuffer):
                    if self.dataBuffer[i : i + len(imageProtocall.ImageProtocall.syncData)] == bytes(imageProtocall.ImageProtocall.syncData):     #Searching for the sync bytes.
                        #print('Found synce bytes')
                        bType = self.dataBuffer[i + len(bytes(imageProtocall.ImageProtocall.syncData)) + 1]
                        bDataLen = self.dataBuffer[i + len(bytes(imageProtocall.ImageProtocall.syncData)) + 1 : i + len(bytes(imageProtocall.ImageProtocall.syncData)) + 1 + 4]
                        dataLen = int.from_bytes(bDataLen, byteorder='big', signed=False)

                        # Checking to see if there is enough data in the buffer.
                        if len(self.dataBuffer) > dataLen:
                            try:
                                #print("Current buffer: " + str(len(self.dataBuffer)))
                                #print('Now to decode')

                                imageData = bytes(self.dataBuffer[i + len(bytes(imageProtocall.ImageProtocall.syncData)) + 1 + 4 : (i + len(bytes(imageProtocall.ImageProtocall.syncData)) + 1 + 5) + dataLen])

                                #Removing the found image data from the buffer.
                                self.dataBuffer = self.dataBuffer[(i + len(
                                    bytes(imageProtocall.ImageProtocall.syncData)) + 1 + 5) + dataLen: len(self.dataBuffer)]

                                im = cv2.imdecode(np.asarray(bytearray(imageData), dtype=np.uint8), 1)

                                if self.showDebug == True:
                                    #Displaying frame size
                                    cv2.putText(im, str(len(imageData)), (10, im.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                                                0.50, (0, 0, 255), 1)

                                    cv2.putText(im, str(len(self.dataBuffer)), (200, im.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                                0.50, (0, 0, 255), 1)

                                    #Displaying the decode time stamp.
                                    timestamp = datetime.datetime.now()
                                    cv2.putText(im, str(timestamp), (10, im.shape[0] - 100), cv2.FONT_HERSHEY_SIMPLEX,
                                                1, (0, 0, 255), 2)


                                # Adding some overlays to help with alignment.
                                #Vertical Line
                                #cv2.line(im, (int(im.shape[1]/2), int(im.shape[0]/2) - 40), (int(im.shape[1]/2), int(im.shape[0])), (0, 0, 255), 2)

                                #Horizontal Line
                                #cv2.line(im, (int(im.shape[1]/2) - 40, int(im.shape[0]/2)), (int(im.shape[1]/2) + 40, int(im.shape[0]/2)), (0, 0, 255), 2)

                                #Floor pickup alignment line.
                                #cv2.line(im, (100, int(im.shape[0]) - 60), (int(im.shape[1]) - 100, int(im.shape[0]) - 60), (0, 0, 255), 2)

                                #Protecting the image display from the network issues.
                                try:

                                    MAZE_NAME = 'frameName' + self.host + ':' + str(self.port)
                                    curSize = cv2.getWindowImageRect(MAZE_NAME)

                                    window = cv2.namedWindow(MAZE_NAME, cv2.WINDOW_NORMAL)
                                    cv2.resizeWindow(MAZE_NAME, 640, 480)
                                    cv2.imshow(MAZE_NAME, im)
                                    #cv2.moveWindow(MAZE_NAME, 100, 0)

                                    #cv2.imshow('frameName' + self.host + ':' + str(self.port), im)
                                    #cv2.namedWindow('frameName' + self.host + ':' + str(self.port), WINDOW_NORMAL)
                                except:
                                    print(self.host + ':' + str(self.port) + ' Dropped Frame')

                            except:
                                print('Unable to proces')

                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                self.runClient = False
                        else:
                            print('Not enough data.', len(self.dataBuffer), self.host + ":" + str(self.port))
                            break

                            #print("Current buffer: " + str(len(self.dataBuffer)))

        time.sleep(0.034)        #Not enough data to decode so taking a break.

        print('Decoder has stopped.')

    def sendData(self, data):
        self.curConnection.sendall(str.encode(data))
