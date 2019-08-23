#Main program for starting cameras, servers, and logging.
import camera
import socketServer
import socketClient
import sys, os
import time
import unicodedata
import threading

robotCameras = []   #Array for the cameras
imageServer = []  #Server for sending out data.
imageClient = []    #Array of client connections.

runServerMonitor = True     #Controls the server monitoring the return messages.


#Main start.
def main():
    print("Starting main program.")

    autoMode = False
    commandBuffer = []  # Buffer for auto mode.

    #Setting up the thread to monitor servers.
    runServerMonitor = True;
    t = threading.Thread(target=threadMonitorServers, args=())
    t.start()

    if(len(sys.argv) > 1):
        if(sys.argv[1] == 'auto'):
            print('Starting auto startup')
            autoMode = True

            #Reading in all auto commands.
            with open(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[2]))) as f:
                commandBuffer = f.readlines()
            # you may also want to remove whitespace characters like `\n` at the end of each line
            commandBuffer = [x.strip() for x in commandBuffer]

            for x in commandBuffer:
                print(x)

    command = ""    # setting up the command holder.

    while(command != "exit"):

        if(autoMode and len(commandBuffer) > 0):
            command = commandBuffer[0]
        else:
            command = input("Enter command: ")  # Taking in the command.

        try:
            processCommand(command)

        except:
            print('Bad command')

        if(len(commandBuffer) > 0):
            commandBuffer.remove(commandBuffer[0])

def threadMonitorServers():
    while(runServerMonitor == True):
        for s in imageServer:
            if s.curReceivedData != None:
                print("Received a message: " + s.curReceivedData.decode("utf-8"))
                try:
                    commandReceived = s.curReceivedData.decode("utf-8")
                    commandReceived = str.replace(commandReceived, ';',',')
                    processCommand(commandReceived)
                except:
                    print("Bad incoming command.")
                s.curReceivedData = None    #Clearing the data.



        time.sleep(5)

def processCommand(command):
    commandBreak = command.split(",")

    if "camera" in command:
        if (commandBreak[1] == 'start'):
            robotCameras.append(camera.Camera(int(commandBreak[2])))

            if len(commandBreak) > 3:
                robotCameras[len(robotCameras) - 1].setupCamera(commandBreak[3], commandBreak[4])
            else:
                robotCameras[len(robotCameras) - 1].setupCamera(640, 480)

            robotCameras[len(robotCameras) - 1].setPreview(False)
            robotCameras[len(robotCameras) - 1].startCapture()

        if (commandBreak[1] == 'stop' and len(commandBreak) == 3):
            robotCameras[int(commandBreak[2])].stopCapture()
            robotCameras.remove(robotCameras[int(commandBreak[2])])

        if (commandBreak[1] == 'q'):
            robotCameras[int(commandBreak[2])].setQuality(int(commandBreak[3]))

        if (commandBreak[1] == 'record'):
            if commandBreak[2] == 'start':
                robotCameras[int(commandBreak[3])].startRecord(commandBreak[4])

            if commandBreak[2] == 'stop':
                robotCameras[int(commandBreak[3])].stopRecord()

        if (commandBreak[1] == 'preview'):
            if (commandBreak[2] == 'start'):
                robotCameras[int(commandBreak[3])].setPreview(True)

            if (commandBreak[2] == 'stop'):
                robotCameras[int(commandBreak[3])].setPreview(False)

        if (commandBreak[1] == 'mode'):
            if (commandBreak[2] == 'true'):
                robotCameras[int(commandBreak[3])].setGrayMode(True)
            else:
                robotCameras[int(commandBreak[3])].setGrayMode(False)

        if (commandBreak[1] == 'edge'):
            if (commandBreak[2] == 'true'):
                robotCameras[int(commandBreak[3])].setEdgeMode(True)
            else:
                robotCameras[int(commandBreak[3])].setEdgeMode(False)

        if (commandBreak[1] == 'debug'):
            if (commandBreak[2] == 'true'):
                robotCameras[int(commandBreak[3])].setDebugMode(True)
            else:
                robotCameras[int(commandBreak[3])].setDebugMode(False)

    if "exit" in command:

        # Stopping all cameras.
        for cam in robotCameras:
            cam.stopCapture()
            cam.stopRecord()

    if "server" in command:
        if commandBreak[1] == 'start':
            imageServer.append(
                socketServer.SocketServer('', int(commandBreak[2]), robotCameras[int(commandBreak[3])]))
            imageServer[len(imageServer) - 1].startServer()

        if commandBreak[1] == "stop":
            imageServer[int(commandBreak[2])].startServer()

        if (commandBreak[1] == 'frame'):
            imageServer[int(commandBreak[2])].setFrameRate(int(commandBreak[3]))

    if "client" in command:
        if commandBreak[1] == 'start':
            imageClient.append(socketClient.SocketClient(commandBreak[2], int(commandBreak[3])))
            imageClient[len(imageClient) - 1].clientConnect()

        if commandBreak[1] == 'stop':
            imageClient[int(commandBreak[2])].clientDisconnect()
            imageClient.remove(imageClient[int(commandBreak[2])])

        if (commandBreak[1] == 'debug'):
            if (commandBreak[2] == 'true'):
                imageClient[int(commandBreak[3])].setDebugMode(True)
            else:
                imageClient[int(commandBreak[3])].setDebugMode(False)

        if commandBreak[1] == 'send':
            imageClient[int(commandBreak[2])].sendData(commandBreak[3])

    if "sleep" in command:
        time.sleep(float(commandBreak[1]))

    if "shutdown" in command:
        print('Shutdown command received.')
        #for ser in imageServer:
        #    ser.stopServer()

        for cam in camera:
            cam.stopRecord()

        # Sending command to os to shutdown.
        #os.system('shutdown /s')    #Commanding the computer to shutdown.


if __name__ == '__main__':
    main()