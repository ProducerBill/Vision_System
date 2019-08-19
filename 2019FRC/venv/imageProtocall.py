# Class for processing image protocall.

import camera

class ImageProtocall:

    # Internal objects
    imageData = None     # Raw container for image data.
    imageID = None  # Image id.
    syncData = bytearray([0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x01, 0xFF, 0x00
                             , 0xFF, 0xFF, 0xFF])

    #Creating a local version of the camera
    curCamera = None


    def __init__(self, id, camera):
        print('Protocall up.')
        self.imageID = id   # Setting up the id.

        #Creating connection to camera.
        self.curCamera = camera

    # Loads the data file into memory
    def loadImage(self, fileName):
        #self.imageData = bytearray(open(fileName, "rb").read()) # Loading the file into memory.

        #Getting the data from the camera temp stream.
        self.imageData = self.curCamera.tempData

    # Compiles all data into one byte array.
    def getFullImagePacket(self):
        curPacket  = bytearray()
        messageID = bytearray([0x00])

        dataAmount = 0

        if(self.imageData != None):
            # Converting the image length to bytes
            dataAmount = len(self.imageData)

            bDataAmoaunt = bytearray((dataAmount).to_bytes(4, byteorder='big', signed=False))

            test = int.from_bytes(bDataAmoaunt, byteorder='big', signed=False)

            #decodeTest = int.from_bytes(bytearray([0x00, 0x00, 0x02, 0x7A]), byteorder='big', signed=False)

            #Compiling the whole message (Sync(5), MessageId(1), DataCount(4), Message Data (See DataCount)
            curPacket = self.syncData + messageID + bDataAmoaunt + self.imageData
            return curPacket
        else:
            return None
