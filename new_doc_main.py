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

DXL_ID_DOC = 1

BAUDRATE = 57600
DEVICENAME_DOC = '/dev/ttyUSB0'

TORQUE_ENABLE = 1
TORQUE_DISABLE = 0

# operating modes for the motor 
MODE_CURRENT = 0
MODE_VELOCITY = 1
MODE_POSITION = 4
MODE_PWM = 16

state = 0
current = 0

t0 = 0
t1 = 0

pat_pos_backup = POSITION_OFFSET_PAT
pat_vel_backup = 0
pat_torque_backup = 0

doc_pos_backup = POSITION_OFFSET_DOC
doc_vel_backup = 0


# Initialization State
def state_0(state, controllerDoc, subscriberDoc, publisherDoc):
    controllerDoc.motor.openPort()
    controllerDoc.motor.setBaudRate()
    controllerDoc.motor.setTorque(TORQUE_DISABLE)
    controllerDoc.motor.setDriveMode(0)
    controllerDoc.motor.setVelProf(0)

    controllerDoc.motor.setMode(MODE_POSITION)
    controllerDoc.motor.setTorque(TORQUE_ENABLE)
    controllerDoc.motor.setPosition(POSITION_OFFSET_DOC)

    time.sleep(3)

    controllerDoc.motor.setTorque(TORQUE_DISABLE)

    controllerDoc.motor.setMode(MODE_PWM)
    controllerDoc.motor.setTorque(TORQUE_ENABLE)
    # controllerDoc.motor.setCurrent(0)

    os.system("gcloud pubsub subscriptions seek doctor_motion-sub --time=2023-04-26T11:00:00Z")

    print("i am in state 0")
    time.sleep(5)

    state = 1
    print("i am in state 1 now")
    return state


def state_1(
        state,
        controllerDoc,
        subscriberDoc,
        publisherDoc,
        subscribing_queue,
        publishing_queue):

    global t0
    global t1
    global pat_pos_backup
    global pat_vel_backup
    global pat_torque_backup

    global doc_pos_backup
    global doc_vel_backup

    t1 = time.time()*1000
    dt = t1 - t0
    t0 = t1

    doc_pos = controllerDoc.motor.readPosition()
    doc_vel = controllerDoc.motor.readVelocity()
    doc_torque = 0  # Set the torque to 0 since the sensor module is not used

    print("current doc_postion is: {}".format(doc_pos),
          "current doc_torque is: {}\n".format(doc_torque),
          "current doc_velocity is: {}\n".format(doc_vel))

    if not subscribing_queue.empty():
        sub_data = subscribing_queue.get()
        pat_pos = sub_data[0]
        pat_vel = sub_data[1]
        pat_torque = sub_data[2]

        pat_pos_backup = pat_pos
        pat_vel_backup = pat_vel
        pat_torque_backup = pat_torque
    else:
        pat_pos = pat_pos_backup
        pat_vel = pat_vel_backup
        pat_torque = pat_torque_backup

        print(f"pat last position: {pat_pos}")
        print(f"pat last velocity: {pat_vel}")

    if publishing_queue.empty():
        publishing_queue.put([doc_pos, doc_vel, doc_torque])

    controllerDoc.piControl(
        pat_pos + POSITION_OFFSET_DOC - POSITION_OFFSET_PAT,
        pat_vel,
        pat_torque,
        doc_pos,
        doc_vel
    )

    state = 1
    return state


def state_2(state, controllerDoc, subscriberDoc, publisherDoc):
    state = 2
    return state


def state_3(state, controllerDoc, subscriberDoc, publisherDoc):
    # Returning Home and Shutting Down

    controllerDoc.motor.setTorque(TORQUE_DISABLE)
    controllerDoc.motor.setDriveMode(0)
    controllerDoc.motor.setVelProf(30)

    controllerDoc.motor.setMode(MODE_POSITION)
    controllerDoc.motor.setTorque(TORQUE_ENABLE)
    controllerDoc.motor.setPosition(POSITION_OFFSET_DOC)
    time.sleep(3)

    controllerDoc.motor.setTorque(TORQUE_DISABLE)
    controllerDoc.motor.setMode(MODE_PWM)
    controllerDoc.motor.setVelProf(0)
    controllerDoc.motor.setTorque(TORQUE_ENABLE)

    state = 1

    return state


def subscription_thread(subscriber):
    # pull patient motion
    subscriber.pull_patient_motion()


def publishing_thread(publisher):
    # push doctor motion
    publisher.set_publish_interval(0)

    while True:
        publisher.publish_doctor_motion()


def main(
        controllerDoc,
        subscriberDoc,
        publisherDoc,
        subscribing_queue,
        publishing_queue):

    state = 0

    while True:

        if state == 0:
            state = state_0(state, controllerDoc, subscriberDoc, publisherDoc)

        elif state == 1:
            state = state_1(
                state,
                controllerDoc,
                subscriberDoc,
                publisherDoc,
                subscribing_queue,
                publishing_queue)

        elif state == 2:
            state = state_2(state, controllerDoc, subscriberDoc, publisherDoc)

        elif state == 3:
            state = state_3(state, controllerDoc, subscriberDoc, publisherDoc)


if __name__ == "__main__":
    try:
        publishing_queue = queue.Queue(maxsize=1)
        subscribing_queue = queue.Queue(maxsize=1)

        motorDoc = Motor(DXL_ID_DOC, BAUDRATE, DEVICENAME_DOC, PROTOCOL_VERSION)
        controllerDoc = Controller(motorDoc)
        controllerDoc.kp = KP
        controllerDoc.kd = KD
        controllerDoc.ki = KI

        subscriberDoc = Subscriber(subscribing_queue)
        publisherDoc = Publisher(publishing_queue)

        subscriber = threading.Thread(
            target=subscription_thread,
            args=(subscriberDoc,),
            daemon=True
        )

        publisher = threading.Thread(
            target=publishing_thread,
            args=(publisherDoc,),
            daemon=True
        )

        subscriber.start()
        publisher.start()

        main(
            controllerDoc,
            subscriberDoc,
            publisherDoc,
            subscribing_queue,
            publishing_queue
        )

        subscriber.join()
        publisher.join()
    except KeyboardInterrupt:
        print("Keyboard Interrupted me")