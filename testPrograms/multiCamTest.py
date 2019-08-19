import numpy
import cv2
import threading
import time
import platform
from zipfile import ZipFile

cap = []    #Capture devices.
curOS = platform.system()
saveLOC = ""

imageQly = 100
edgeMin = 100
edgeMax = 200

def findCamera():
    arr = []
    index = 0

    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
            print('Camera found at: ', index)
        cap.release()
        index += 1
    return arr

#Thread for running the camera.
def threadRunCamera(camera):
    camCap = cv2.VideoCapture(camera)

    camCap.set(3,640)
    camCap.set(4,480)

    while(True):
        ret, frame = camCap.read()

        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_image, edgeMin, edgeMax)

        frameName = 'frame' + str(camera)

        cv2.imshow(frameName, frame)
        cv2.imshow(frameName + 'gray', edges)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if cv2.waitKey(1) & 0xff == ord('s'):
            cv2.imwrite('test' + str(camera) + '.jpg', gray_image, [cv2.IMWRITE_JPEG_QUALITY, imageQly])
            cv2.imwrite('test-edge' + str(camera) + '.jpg', edges, [cv2.IMWRITE_JPEG_QUALITY, imageQly])
            cv2.imwrite('test-edge-bi' + str(camera) + '.png', edges ,[cv2.IMWRITE_PNG_BILEVEL, 1])

            with ZipFile('testPNG.zip','w') as zip:
                zip.write('test-edge-bi' + str(camera) + '.png')

    camCap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    print(curOS)

    if curOS == 'Windows':
        saveLOC = "C:/Temp/"
    else:
        saveLOC = "./"

    print("Running the camera search")
    # Getting the camera.
    cap = findCamera()
    print(len(cap))

    #Starting all cameras.



    while(True):
        userInput = input("Enter command:")

        if userInput == 'exit':
            break

        if "cam" in userInput:
            command = userInput.split(",")
            t = threading.Thread(target=threadRunCamera, args=(int(command[1]),))
            t.start()

        if "all" in userInput:
            for cam in cap:
                t = threading.Thread(target=threadRunCamera, args=(cam,))
                t.start()
                time.sleep(1)

        if "qul" in userInput:
            command = userInput.split(",")
            imageQly = int(command[1])

        if "minE" in userInput:
            command = userInput.split(",")
            edgeMin = int(command[1])

        if "maxE" in userInput:
            command = userInput.split(",")
            edgeMax = int(command[1])


    print("end of program.")

# cap = cv2.VideoCapture(0)
# cap2 = cv2.VideoCapture(1)
#
# while(True):
#     # Capture frame-by-frame
#     ret, frame = cap.read()
#
#     # Our operations on the frame come here
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#     # Display the resulting frame
#     cv2.imshow('frame',gray)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()