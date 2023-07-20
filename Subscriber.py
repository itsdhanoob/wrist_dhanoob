from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
from Constants import POSITION_OFFSET_DOC, POSITION_OFFSET_PAT
import os
import ast
import threading
import time


class Subscriber:
    NUM_MESSAGES = 1

    def __init__(self, subscribing_queue):
        os.environ[
            "GOOGLE_APPLICATION_CREDENTIALS"
            ] = "./authentication/hand-rehab-robot-.json"
        self.project_id = "hand-rehab-robot"
        self.subscription_id_doc_mot = "doctor_motion-sub"
        self.subscription_id_pat_mot = "patient_motion-sub"
        self.subscriber = pubsub_v1.SubscriberClient()
        self.doctor_pos = POSITION_OFFSET_DOC
        self.doctor_vel = 0
        self.doctor_torque = 0
        self.patient_pos = POSITION_OFFSET_PAT
        self.patient_vel = 0
        self.patient_torque = 0
        self._lock = threading.Lock()
        self.subscribing_queue = subscribing_queue

    def doc_callback(self, message):
        doctor_mot = ast.literal_eval(message.data.decode("utf-8"))

        try:
            self.subscribing_queue.put_nowait([float(doctor_mot[0]),
                                        float(doctor_mot[1]),
                                        float(doctor_mot[2])])
        except:
            pass

        message.ack()

    def pat_callback(self, message):
        patient_mot = ast.literal_eval(message.data.decode("utf-8"))

        try:
            self.subscribing_queue.put_nowait([float(patient_mot[0]),
                                        float(patient_mot[1]),
                                        float(patient_mot[2])])
        except:
            pass
        message.ack()

    def pull_doctor_motion(self):
        subscription_path = self.subscriber.subscription_path(
            self.project_id,
            self.subscription_id_doc_mot)

        streaming_pull_future = self.subscriber.subscribe(
            subscription_path,
            callback=self.doc_callback)
        print(f"Listening for messages on {subscription_path}..\n")

        with self.subscriber:
            try:
                # When `timeout` is not set, result() will block indefinitely,
                # unless an exception is encountered first.
                streaming_pull_future.result()
            except TimeoutError:
                streaming_pull_future.cancel()

    def pull_patient_motion(self):
        subscription_path = self.subscriber.subscription_path(
            self.project_id,
            self.subscription_id_pat_mot)

        streaming_pull_future = self.subscriber.subscribe(
            subscription_path,
            callback=self.pat_callback)
        print(f"Listening for messages on {subscription_path}..\n")

        with self.subscriber:
            try:
                # When `timeout` is not set, result() will block indefinitely,
                # unless an exception is encountered first.
                streaming_pull_future.result()
            except TimeoutError:
                streaming_pull_future.cancel()


if __name__ == "__main__":
    import queue
    my_queue = queue.Queue(maxsize=1)

    def get_fcn(a_queue):
        while True:
            print(a_queue.get()[2])

    main_loop = threading.Thread(
        target=get_fcn,
        args=(my_queue,),
        daemon=True)

    main_loop.start()

    mySub = Subscriber(my_queue)
    mySub.pull_doctor_motion()
