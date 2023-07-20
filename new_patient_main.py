from Motor import Motor
from new_controller import Controller
from Subscriber import Subscriber
from Publisher import Publisher
from Constants import POSITION_OFFSET_DOC, POSITION_OFFSET_PAT, KP, KD, KI
import threading
import time
import queue
import sys
import os

# Protocol version
PROTOCOL_VERSION = 2.0

DXL_ID_PAT = 1

BAUDRATE = 57600
DEVICENAME_PAT = '/dev/ttyUSB0'

TORQUE_ENABLE = 1
TORQUE_DISABLE = 0

MODE_CURRENT = 0
MODE_VELOCITY = 1
MODE_POSITION = 4
MODE_PWM = 16

state = 0
current = 0
t0 = 0
t1 = 0

doc_pos_backup = POSITION_OFFSET_DOC
doc_vel_backup = 0
doc_torque_backup = 0

pat_pos_backup = POSITION_OFFSET_PAT
pat_vel_backup = 0


# Initialization State
def state_0(state, controllerPat, subscriberPat, publisherPat):
    controllerPat.motor.openPort()
    controllerPat.motor.setBaudRate()
    controllerPat.motor.setTorque(TORQUE_DISABLE)
    controllerPat.motor.setDriveMode(0)
    controllerPat.motor.setVelProf(0)

    controllerPat.motor.setMode(MODE_POSITION)
    controllerPat.motor.setTorque(TORQUE_ENABLE)
    controllerPat.motor.setPosition(POSITION_OFFSET_PAT)

    time.sleep(3)

    controllerPat.motor.setTorque(TORQUE_DISABLE)

    controllerPat.motor.setMode(MODE_PWM)
    controllerPat.motor.setTorque(TORQUE_ENABLE)
    # controllerPat.motor.setCurrent(0)

    os.system("gcloud pubsub subscriptions seek patient_motion-sub --time=2023-04-26T11:00:00Z")

    time.sleep(5)

    state = 1

    return state


def state_1(
        state,
        controllerPat,
        subscriberPat,
        publisherPat,
        subscribing_queue,
        publishing_queue):
    global t0
    global t1
    global doc_pos_backup
    global doc_vel_backup
    global doc_torque_backup
    global pat_pos_backup
    global pat_vel_backup

    t1 = time.time()*1000
    dt = t1 - t0
    t0 = t1

    pat_pos = controllerPat.motor.readPosition()
    pat_vel = controllerPat.motor.readVelocity()
    pat_torque = 0  # Set the torque to 0 since the sensor module is not used

    try:
        doc_pos = controllerPat.sensor.getDoctorPosition()
        doc_vel = controllerPat.sensor.getDoctorVelocity()
        doc_torque = controllerPat.sensor.getDoctorTorque()
    except:
        doc_pos = doc_pos_backup
        doc_vel = doc_vel_backup
        doc_torque = doc_torque_backup

    if not subscribing_queue.empty():
        sub_data = subscribing_queue.get()
        doc_pos = sub_data[0]
        doc_vel = sub_data[1]
        doc_torque = sub_data[2]

        doc_pos_backup = doc_pos
        doc_vel_backup = doc_vel
        doc_torque_backup = doc_torque
    else:
        doc_pos = doc_pos_backup
        doc_vel = doc_vel_backup
        doc_torque = doc_torque_backup

    if publishing_queue.empty():
        publishing_queue.put([pat_pos, pat_vel, pat_torque])

    controllerPat.piControl(
        doc_pos,
        doc_vel,
        doc_torque,
        pat_pos + abs(POSITION_OFFSET_DOC - POSITION_OFFSET_PAT),
        pat_vel,
    ) 

    state = 1
    return state


def state_2(state, controllerPat, subscriberPat, publisherPat):
    state = 2
    return state


def state_3(state, controllerPat, subscriberPat, publisherPat):
    # Returning Home and Shutting Down

    controllerPat.motor.setTorque(TORQUE_DISABLE)
    controllerPat.motor.setDriveMode(0)
    controllerPat.motor.setVelProf(30)

    controllerPat.motor.setMode(MODE_POSITION)
    controllerPat.motor.setTorque(TORQUE_ENABLE)
    controllerPat.motor.setPosition(POSITION_OFFSET_PAT)
    time.sleep(3)

    controllerPat.motor.setTorque(TORQUE_DISABLE)
    controllerPat.motor.setMode(MODE_PWM)
    controllerPat.motor.setVelProf(0)
    controllerPat.motor.setTorque(TORQUE_ENABLE)

    state = 1

    return state


def subscription_thread(subscriber):
    # pull doctor motion
    subscriber.pull_doctor_motion()


def publishing_thread(publisher):
    # push patient motion
    publisher.set_publish_interval(0)
    while True:
        publisher.publish_patient_motion()


def main(
        controllerPat,
        subscriberPat,
        publisherPat,
        subscribing_queue,
        publishing_queue):

    state = 0

    while True:

        if state == 0:
            state = state_0(state, controllerPat, subscriberPat, publisherPat)

        elif state == 1:
            state = state_1(state,
                            controllerPat,
                            subscriberPat,
                            publisherPat,
                            subscribing_queue,
                            publishing_queue)

        elif state == 2:
            state = state_2(state, controllerPat, subscriberPat, publisherPat)

        elif state == 3:
            state = state_3(state, controllerPat, subscriberPat, publisherPat)


if __name__ == "__main__":
    publishing_queue = queue.Queue(maxsize=1)
    subscribing_queue = queue.Queue(maxsize=1)

    motorPat = Motor(DXL_ID_PAT, BAUDRATE, DEVICENAME_PAT, PROTOCOL_VERSION)
    controllerPat = Controller(motorPat)
    controllerPat.kp = KP
    controllerPat.kd = KD
    controllerPat.ki = KI

    subscriberPat = Subscriber(subscribing_queue)
    publisherPat = Publisher(publishing_queue)

    pat_torque = 0

    subscriber = threading.Thread(
        target=subscription_thread,
        args=(subscriberPat,),
        daemon=True
    )

    publisher = threading.Thread(
        target=publishing_thread,
        args=(publisherPat,),
        daemon=True
    )

    subscriber.start()
    publisher.start()

    main(
        controllerPat,
        subscriberPat,
        publisherPat,
        subscribing_queue,
        publishing_queue
    )

    subscriber.join()
    publisher.join()