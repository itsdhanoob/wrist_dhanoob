import cv2
import numpy

video = cv2.VideoCapture(0)


def video_stream():
    while True:
        ret, frame = video.read()
        if not ret:
            break;
        else:
            ret, buffer = cv2.imencode('.jpeg',frame)
            frame = buffer.tobytes()
            yield (b' --frame\r\n' b'Content-type: image/jpeg\r\n\r\n' + frame +b'\r\n')


