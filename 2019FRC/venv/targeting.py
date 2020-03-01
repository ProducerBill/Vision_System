#Class for targeting for 2020 FRC

import numpy as np
import cv2
import mss
import mss.tools
import PIL as Image
import threading
import time

class Targeting:

    imgSouce = None
    runTargetProcess = False;
    mode = 'test'   # Mode of processing.

    # Setting to the point we want to target.
    camCenterToShooterCenterOffset = 0.0
    camTopToShooterBottom = 0.0
    imgXPos = 0.0
    ballDiaAtTarget = 0.0
    distanceToWall = 0.0

    # Targeting outputs
    curTarXPos = 0.0
    curTarXOffset = 0.0
    curTarYPos = 0.0
    curTarYOffset = 0.0



    def __init__(self, source, mode):
        print('Starting Target')

        if(mode == 'run'):
            self.mode = 'run'
            self.imgSouce = source

        if(mode == 'test'):
            print('Target test mode.')
            self.mode = 'test'

        #Starting target processing.
        self.runTargetProcess = True;
        tTargeting = threading.Thread(target=self.threadProcess, args=())
        tTargeting.start()
        
    def stopTartgeting(self):
        self.runTargetProcess = False

    def stackImages(self, scale, imgArray):
        rows = len(imgArray)
        cols = len(imgArray[0])
        rowsAvailable = isinstance(imgArray[0], list)
        width = imgArray[0][0].shape[1]
        height = imgArray[0][0].shape[0]
        if rowsAvailable:
            for x in range(0, rows):
                for y in range(0, cols):
                    if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                        imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                    else:
                        imgArray[x][y] = cv2.resize(imgArray[x][y],
                                                    (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale,
                                                    scale)
                    if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y],
                                                                                     cv2.COLOR_GRAY2BGR)
            imageBlank = np.zeros((height, width, 3), np.uint8)
            hor = [imageBlank] * rows
            hor_con = [imageBlank] * rows
            for x in range(0, rows):
                hor[x] = np.hstack(imgArray[x])
            ver = np.vstack(hor)
        else:
            for x in range(0, rows):
                if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                    imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
                else:
                    imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale,
                                             scale)
                if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
            hor = np.hstack(imgArray)
            ver = hor
        return ver

    def screemGrab(self):
        with mss.mss() as sct:
            # The screen part to capture
            monitor = {"top": 160, "left": 160, "width": 640, "height": 480}

            # Grab the data
            sct_img = sct.grab(monitor)
            img = np.array(sct_img)
            return img

    def filterColor(self, img, MaskColors):  # lowerColor, highColor):
        # Converting the image to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        masks = []

        # Building the mask to find just the colors input.
        for msk in MaskColors:
            masks.append(cv2.inRange(hsv, msk[0], msk[1]))

        mask = None

        mask = sum(masks)

        # mask = cv2.inRange(hsv, lowerColor, highColor)

        # Bitwising the base image to the mask.
        result = cv2.bitwise_and(img, img, mask=mask)

        # Returning the results.
        return result

    def blurImage(self, img):
        imgBlur = cv2.GaussianBlur(img, (7, 7), 2)
        return imgBlur

    def sharpenImage(self, img):
        kernel = np.array([[0, 0, 0, 0, 0],
                           [0, -1, -1, -1, 0],
                           [0, -1, 8, -1, 0],
                           [0, -1, -1, -1, 0],
                           [0, 0, 0, 0, 0]])

        # Sharpen image
        image_sharp = cv2.filter2D(img, -1, kernel)
        return image_sharp

    def findEdges(self, img, threshold1, threshold2):

        imgGray = None

        if len(img.shape) < 3:
            imgGray = img
        else:
            imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgCanny = cv2.Canny(imgGray, threshold1, threshold2)

        return imgCanny

    def getContours(self, img, imgContour, areaMin, areaMax):
        contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        cntResults = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > areaMin and area < areaMax:
                cv2.drawContours(imgContour, cnt, -1, (255, 0, 255), 7)
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

                cntResults.append(cnt)

        return cntResults

    def drawContours(self, imgTemp, contours):
        for cnt in contours:
            area = cv2.contourArea(cnt)
            cv2.drawContours(imgTemp, cnt, -1, (255, 0, 255), 7)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            x, y, w, h = cv2.boundingRect(approx)
            cv2.rectangle(imgTemp, (x, y), (x + w, y + h), (0, 255, 0), 5)

            cv2.putText(imgTemp, "Points: " + str(len(approx)), (x + w + 20, y + 20), cv2.FONT_HERSHEY_COMPLEX, .7,
                        (0, 255, 0), 2)
            cv2.putText(imgTemp, "Area: " + str(int(area)), (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                        (0, 255, 0), 2)

        return imgTemp

    def paintVerTarget(self, imgTemp, contour):
        height, width, channels = imgTemp.shape
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        x, y, w, h = cv2.boundingRect(approx)

        #Finding X offset to target.
        self.curTarXPos = x + (int)(w/2)

        imgTemp = cv2.line(imgTemp, (self.curTarXPos, 0),
                           (self.curTarXPos, height),
                           (0,255,0), 2)
        return imgTemp

    def drawOffsets(self, imgTemp):
        cv2.putText(imgTemp, "X: " + str(), (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                    (0, 255, 0), 2)

        return imgTemp

    def matchContourToMaster(self, contour, offset):
        for cnt in contour:
            for data in cnt:
                data[0][0] = data[0][0] + offset[1]
                data[0][1] = data[0][1] + offset[0]

        return contour

    def findTargets(self, img):

        # Final target information
        lowerTargetData = None
        upperTargetData = None

        # Grabing the lower part of the image as the lower target is most likely in that area.
        height, width, channels = img.shape
        lowerImg = img[(int)(height / 2): height, 0: width]
        lowerImgLoc = [(int)(height / 2), 0]

        # cv2.imshow("Lower Half", lowerImg)

        # Real ranges Blue
        lTLowerHSV = np.array(([63, 43, 59]))
        lTUpperHSV = np.array(([111, 102, 187]))
        # maskColor = ([[lTLowerHSV, lTUpperHSV]])

        # Real ranges for Red
        maskColor = ([
            [np.array((([0, 50, 50]))), np.array(([8, 255, 255]))]
            , [np.array((([170, 150, 130]))), np.array(([180, 255, 255]))]
            , [np.array((([63, 43, 59]))), np.array((([111, 102, 187])))]
        ])

        # fliter image for color.
        filterImg = self.filterColor(lowerImg, maskColor)

        # For filter debug
        # cv2.imshow("First Filter", filterImg)

        # Getting the blured image needed.
        imgBlur = self.blurImage(filterImg)

        # Finding the edges.
        # imgEdges = findEdges(filterImg, 157, 158)  # For Blue
        imgEdges = self.findEdges(imgBlur, 165, 106)  # For Red

        # cv2.imshow("Found Edges", imgEdges)

        kernel = np.ones((5, 5))
        imgDil = cv2.dilate(imgEdges, kernel, iterations=1)

        # Debug for dilation
        # cv2.imshow("Dia", imgDil)

        # Making a copy of the image.
        imgP2 = img.copy()

        # Finding the contours
        LTContours = self.getContours(imgDil, img.copy(), 2000, 60000)

        # Updating the contours to match master image.
        LTContours = self.matchContourToMaster(LTContours, lowerImgLoc)

        #Shows all found contours
        imgFP = self.drawContours(img, LTContours)


        # If the lower target is found then look for upper.

        # Flitering all contours looking for the largest best one.
        if len(LTContours) > 0:  # If there are any contours start looking for the upper.

            lTar = LTContours[0]

            for cnt in LTContours:
                areaCnt = cv2.contourArea(cnt)
                arealTar = cv2.contourArea(lTar)
                if areaCnt > arealTar:
                    lTar = cnt

            area = cv2.contourArea(lTar)
            if area > 2000 and area < 55000:
                peri = cv2.arcLength(lTar, True)
                approx = cv2.approxPolyDP(lTar, 0.02 * peri, True)
                x, y, w, h = cv2.boundingRect(approx)
                # if len(approx) >= 8:
                if x > 0 and y > 0:
                    upperImg = imgP2[0: int(w * 1.3), x: x + w]
                    # cv2.imshow("UpperArea", upperImg)

                    #Painting the center of detected target bottom.
                    imgFP = self.paintVerTarget(imgFP, cnt)

                    # Start of second tier processing.
                    # manualTune(upperImg)

                    HTContours = self.findUpperTarget(upperImg)
                    HTContours = self.matchContourToMaster(HTContours, ([0, x]))
                    imgFP = self.drawContours(imgFP, HTContours)



        # Painting the X target.
        imgFP = cv2.line(imgFP, ((int)(self.imgXPos), 0), ((int)(self.imgXPos), height), (0, 0, 255), 2)

        #shoing onscreen the current offsets.


        cv2.imshow("Final", imgFP)

        cv2.imshow("Lower", self.stackImages(0.5, ([lowerImg, filterImg],
                                            [imgBlur, imgEdges],
                                            [imgDil, imgDil])))

    def findUpperTarget(self, upperImg):

        # Upper Mask Values Red Values
        hTLowerHSV = np.array(([0, 0, 0]))
        hTUpperHSV = np.array(([179, 255, 255]))
        maskColor2 = ([[hTLowerHSV, hTUpperHSV]])

        # fliter image for color.
        filterImg = self.filterColor(upperImg, maskColor2)

        blurCount = cv2.getTrackbarPos("Blur", "Smash")
        sharpCount = cv2.getTrackbarPos("Sharp", "Smash")

        imgGray = cv2.cvtColor(filterImg, cv2.COLOR_BGR2GRAY)

        imgSharp = imgGray.copy()

        for y in range(sharpCount):
            imgSharp = self.sharpenImage(imgSharp)

        if blurCount > 0:
            for x in range(blurCount):
                imgBlur = self.blurImage(imgSharp)
        else:
            imgBlur = imgSharp

        # Finding the edges. Red Values
        imgEdges = self.findEdges(
            imgBlur
            , cv2.getTrackbarPos("Threshold1", "Parameters")
            , cv2.getTrackbarPos("Threshold2", "Parameters")
        )

        # cv2.imshow("UpperEdge", imgEdges)

        kernel = np.ones((5, 5))
        # imgErosion = cv2.erode(imgEdges, kernel, iterations=1)
        imgDil = cv2.dilate(imgEdges, kernel, iterations=1)

        # cv2.imshow("UpperDil", imgDil)

        # Finding the contours
        HTContours = self.getContours(imgDil, upperImg.copy(), 1500, 60000)

        imgFP = self.drawContours(upperImg, HTContours)

        cv2.imshow("Upper", self.stackImages(1.0, ([upperImg, filterImg, imgGray],
                                            [imgSharp, imgBlur, imgFP],
                                            [imgEdges, imgDil, imgFP])))

        return HTContours


    def threadProcess(self):
        while(self.runTargetProcess):

            if(self.mode == 'run'):     # Run with camera mode.
                img = self.imgSouce.getImageFrame()

            if(self.mode == 'test'):
                img = self.screemGrab()     # Grabing from screen.
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)     # Converting compatible format.

            #Setting the current target settings.
            height, width, channels = img.shape
            self.imgXPos = width / 2 + self.camCenterToShooterCenterOffset

            self.findTargets(img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            

            #Pausing to reduce CPU loading.
            time.sleep(0.05)
