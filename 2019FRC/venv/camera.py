# Class for connecting to and controlling the camera.

#Imports
import numpy
import cv2
import time
import threading
import datetime



class Camera:
    cameraID = None    # camera id
    curCam = None  # camera hardware object.
    imageWidth = 640    # default image width
    imageHieght = 480   # default image height
    imageQly = 20      # default image quality
    imageGrayMode = False   #Gray scale mode.
    imageEdgeMode = False   #Edge process mode.

    runCapture = False  # controls the capture of the frames
    showOutput = False  # controls if a debug output will be shown.
    showDebug = False   # Controls if diagnostic data is shown.

    tempData = None     #Temp data to pass to other operations.

    #Setting up the capture
    captureFileName = None
    captureCodec = None
    captureOutput = None
    runRecord = False

    #DateTime for start of record
    startRecordingDateTime = None

    #Length of time to record.
    recordLength = 10

    # Init of the camera object.
    def __init__(self, id):
        self.cameraID = id  # Hardward id of camera
        self.setupCamera()


    # Sets up the camera hardware connection.
    def setupCamera(self):
        self.curCam = cv2.VideoCapture(int(self.cameraID))   # Init the camera
        time.sleep(1.0)

        self.curCam.set(3, self.imageHieght)   # setting the capture height
        self.curCam.set(4, self.imageWidth)    # setting the capture width

    def setPreview(self, state):
        self.showOutput = state

    # Starts frame capture in a thread.
    def startCapture(self):
        print("Starting the collection of the camera images: ", self.cameraID)

        #Capturing the time that recording started.
        #self.startRecordingDateTime = datetime.datetime.now()
        #self.captureFileName = loc + 'capture' + str(self.cameraID) + '-' + self.startRecordingDateTime.datetime.now().strftime(
        #    "%Y-%m-%d-%H%M") + '.mp4'

        self.runCapture = True  # Setting the camera to a run state.
        # self.showOutput = True  # Setting the camera to output a debug image.

        t = threading.Thread(target=self.threadCapture, args=(self.runCapture, self.showOutput,))
        t.start()
        print('Capture started.')

    def stopCapture(self):
        self.runCapture = False
        print('Captured stopped.')

    def startRecord(self, loc):

        # Setting up the capture
        self.captureFileName = loc + 'capture' + str(self.cameraID) + '-' + datetime.datetime.now().strftime(
            "%Y-%m-%d-%H%M") + '.mp4'
        self.captureCodec = cv2.VideoWriter_fourcc(*'mp4v')
        self.captureOutput = cv2.VideoWriter(self.captureFileName, self.captureCodec, 40.0,
                                             (self.imageWidth, self.imageHieght))


        self.runRecord = True
        print('Recording started.')

    def stopRecord(self):
        self.runRecord = False

        self.captureOutput.release()  # Releasing the recording.
        print('Recording stopped.')

    def setQuality(self, quality):
        if quality > 0 and quality <= 100:
            self.imageQly = quality

    def setGrayMode(self, mode):
        self.imageGrayMode = mode
        print('Gray scale mode set.')

    def setEdgeMode(self, mode):
        self.imageEdgeMode = mode
        print('Edge mode set.')

    def setDebugMode(self, mode):
        self.showDebug = mode
        print('Debug mode started.')

    def threadCapture(self, state, showOutput):
        while(self.runCapture):
            ret, frame = self.curCam.read()     #Reading the frame from the camera

            #Saving the capture file to the harddrive.
            if self.runRecord == True:
                try:
                    self.captureOutput.write(frame)
                except:
                    print('Unable to write to video file.')
            else:
                if (self.captureOutput != None):
                    self.captureOutput.release()  # Releasing the recording.
                    self.captureOutput = None

            if self.showDebug == True:
                timestamp = datetime.datetime.now()
                #Adding the time stamp to the frame.
                cv2.putText(frame, str(timestamp), (10, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 0), 2)


            #Setting the frame to gray scale
            if self.imageGrayMode == True:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if self.imageEdgeMode == True:
                frame = cv2.Canny(frame, 50, 300)



            #Putting the current image into memory
            self.tempData = bytearray(cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.imageQly])[1].tostring())

            #Show preview option
            if(self.showOutput):
                frameName = "Frame: " + str(self.cameraID)
                cv2.imshow(frameName,frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            #time.sleep(1)

        self.curCam.release()

        cv2.destroyAllWindows()