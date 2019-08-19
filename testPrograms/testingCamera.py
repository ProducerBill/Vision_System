import numpy as np
import cv2
from PIL import Image


cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)
#cap.set(5,1)
#cap.set(15,1)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',gray)

    edge = cv2.Canny(gray, 5, 300)
    cv2.imshow('edge', edge)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if cv2.waitKey(1) & 0xFF == ord('s'):

        cv2.imwrite('C:/capture/test.jpg', gray)
        cv2.imwrite('C:/capture/edgetest.jpg', edge)

        cv2.imwrite('C:/capture/1bit.png', edge, [cv2.IMWRITE_PNG_BILEVEL, 1])

        image_file = Image.open("C:/capture/edgetest.jpg")
        image_file = image_file.convert('1')
        image_file.save('C:/capture/edgetest-bw.jpg')

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()