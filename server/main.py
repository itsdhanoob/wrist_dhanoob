import os
import shutil
import subprocess
import cv2
from flask import Flask, Response, request, render_template
import json

video = cv2.VideoCapture(0,cv2.CAP_V4L)
app = Flask("__name__")


def video_stream():
    while True:
        ret, frame = video.read()
        if not ret:
            break
        else:
            ret, buffer = cv2.imencode(".jpeg", frame)
            frame = buffer.tobytes()
            yield (
                b" --frame\r\n" b"Content-type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )
    video.release()


@app.route("/video_feed")
def video_feed():
    return Response(
        video_stream(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/")
def information():
    return render_template("information.html")


@app.route("/patient", methods=["POST"])
def patient():
    try:
        shutil.rmtree("/var/www/html/State/")
    except FileNotFoundError as ve:
        print("An exception occurred" + str(ve))
    os.mkdir("State")
    with open("/var/www/html/State/recording.txt", "w") as recording:
        recording.write("RECORDING")
    user_info = request.form
    with open("/var/www/html/Patient_data/patient.json", "w") as f:
        f.write(list(user_info)[0])
    try:
        subprocess.run(["python", "DynamixelSDK/python/patient_clean.py"])
    except FileNotFoundError as ve:
        print("An exception occurred" + str(ve))
    return "200"


@app.route("/passive", methods=["POST"])
def passive():
    try:
        shutil.rmtree("/var/www/html/State/")
    except FileNotFoundError as ve:
        print("An exception occurred" + str(ve))
    os.mkdir("State")
    with open("/var/www/html/State/passive.txt", "w") as recording:
        recording.write("PASSIVE MODE")
    try:
        subprocess.run(["python", "DynamixelSDK/python/robot_clean.py"])
    except FileNotFoundError as ve:
        print("An exception occurred" + str(ve))
    return "200"


@app.route("/active", methods=["POST"])
def active():
    try:
        shutil.rmtree("/var/www/html/State/")
    except FileNotFoundError as ve:
        print("An exception occurred" + str(ve))
    os.mkdir("State")
    with open("/var/www/html/State/active.txt", "w") as recording:
        recording.write("ACTIVE MODE")
    try:
        subprocess.run(["python", "DynamixelSDK/python/robot_clean.py"])
    except FileNotFoundError as ve:
        print("An exception occurred" + str(ve))
    return "200"


@app.route("/slider", methods=["POST"])
def position_slider():
    slider = list(request.form.to_dict(flat=False))
    with open("/var/www/html/Slider_data/position_slider_data.txt", "w") as f:
        f.write(slider[0])
    return "200"


@app.route("/speed_slider", methods=["POST"])
def speed_slider():
    slider = list(request.form.to_dict(flat=False))
    with open("/var/www/html/Slider_data/speed_slider_data.txt", "w") as f:
        f.write(slider[0])
    return "200"


@app.route("/finish", methods=["POST"])
def close():
    try:
        shutil.rmtree("/var/www/html/State/")
    except FileNotFoundError as ve:
        print("An exception occurred" + str(ve))
    return "200"


app.run(host="0.0.0.0", port="5000", debug=False)
#app.run(host="localhost", port="5000", debug=False)
