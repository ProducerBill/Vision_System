#!/usr/bin/python
'''
  A Simple mjpg stream http server for the Raspberry Pi Camera
  inspired by https://gist.github.com/n3wtron/4624820
'''

from http.server import BaseHTTPRequestHandler,HTTPServer
from PIL import Image
import io
import time
import cv2
import numpy
#import picamera

capture=None


class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while True:
                try:
                    if capture:
                        # print('cam')
                        ret, img = capture.read()

                    else:
                        raise Exception('Error, camera not setup')

                    if not ret:
                        print('no image from camera')
                        time.sleep(1)
                        continue

                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                    cv2.imwrite('C:/capture/cash.jpg', img)

                    edge = cv2.Canny(gray, 50, 200)

                    #edge = edge.convert('1')

                    #ret, jpg = cv2.imencode('.jpg', img)

                    #ret, jpg = cv2.imencode('.jpg', edge)

                    image_file = Image.open("C:/capture/cash.jpg")
                    image_file = image_file.convert('L')

                    #image_file = cv2.Canny(image_file, 50, 200)

                    w, h = image_file.size

                    #area = (0, 300, 0, 480)
                    image_file = image_file.crop((0, 150, w, h-150))

                    ret, jpg = cv2.imencode('.jpg', cv2.Canny(numpy.array(image_file), 50, 200))

                    # print 'Compression ratio: %d4.0:1'%(compress(img.size,jpg.size))
                    self.wfile.write("--jpgboundary".encode('utf-8'))
                    self.send_header('Content-type', 'image/jpeg')
                    # self.send_header('Content-length',str(tmpFile.len))
                    self.send_header('Content-length', str(jpg.size))
                    self.end_headers()
                    self.wfile.write(jpg.tostring())
                    time.sleep(.1)
                except KeyboardInterrupt:
                    break
            return
        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body><h1>test</h1>'.encode('utf-8'))
            self.wfile.write('<img src="http://127.0.0.1:8080/cam.mjpg"/>'.encode('utf-8'))
            self.wfile.write('</body></html>'.encode('utf-8'))
            return


def main():
    global capture
    capture = cv2.VideoCapture(0)
    capture.set(3, 640)
    capture.set(4, 480)
    #capture.set(cv2.cv.CV_CAP_PROP_SATURATION, 0.2)
    global img
    try:
            server = HTTPServer(('',8080),CamHandler)
            print("server started")
            server.serve_forever()
    except KeyboardInterrupt:
            capture.release()
            server.socket.close()


if __name__ == '__main__':
    main()
