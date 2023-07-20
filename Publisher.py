from google.cloud import pubsub_v1
from Constants import POSITION_OFFSET_DOC, POSITION_OFFSET_PAT
import os
import time
import threading


class Publisher:
    def __init__(self, publishing_queue):
        os.environ[
            "GOOGLE_APPLICATION_CREDENTIALS"
            ] = "./authentication/hand-rehab-robot-.json"
        self.project_id = "hand-rehab-robot"
        self.topic_id_doc_mot = "doctor_motion"
        self.topic_id_pat_mot = "patient_motion"
        self.publisher = pubsub_v1.PublisherClient()
        self.doctor_pos = POSITION_OFFSET_DOC
        self.doctor_vel = 0
        self.patient_pos = POSITION_OFFSET_PAT
        self.patient_vel = 0
        self.patient_torque = 0
        self.doctor_torque = 0
        self._lock = threading.Lock()
        self.publishing_queue = publishing_queue
        self.message = []
        self.topic_path_pat = self.publisher.topic_path(
            self.project_id,
            self.topic_id_pat_mot)
        self.topic_path_doc = self.publisher.topic_path(
            self.project_id,
            self.topic_id_doc_mot)

        # default interval between publish events is 1 second
        self.interval = 0

    def set_publish_interval(self, interval):
        self.interval = interval

    def publish_doctor_motion(self):
        # if self.publishing_queue.empty():
        #     return
        # motion_doc = self.publishing_queue.get()
        try:
            motion_doc = self.publishing_queue.get_nowait()
        except:
            return

        # motion_doc = self.message
        # if not motion_doc:
        #     return

        if (
            (motion_doc[0] == self.doctor_pos)
                and
                (motion_doc[1] == self.doctor_vel)):
            #    and
            #    (motion_doc[2] == self.doctor_torque)):
            return

        else:
            topic_path = self.publisher.topic_path(
                self.project_id,
                self.topic_id_doc_mot)
            data = str(motion_doc).encode("utf-8")
            future = self.publisher.publish(topic_path, data)
            # print(future.result())
            # time.sleep(self.interval)

            self.doctor_pos = motion_doc[0]
            self.doctor_vel = motion_doc[1]
            self.doctor_torque = motion_doc[2]


    def publish_patient_motion(self):
        # if self.publishing_queue.empty():
        #     return
        # motion_pat = self.publishing_queue.get()

        try:
            motion_pat = self.publishing_queue.get_nowait()
        except:
            return

        # motion_pat = self.message
        # if not motion_pat:
        #     return

        if (
            (motion_pat[0] == self.patient_pos)
                and
                (motion_pat[1] == self.patient_vel)):
            #    and
            #    (motion_pat[2] == self.patient_torque)):
            return

        else:
            topic_path = self.publisher.topic_path(
                self.project_id,
                self.topic_id_pat_mot)
            data = str(motion_pat).encode("utf-8")
            future = self.publisher.publish(topic_path, data)
            # print(future.result())
            # time.sleep(self.interval)

            self.patient_pos = motion_pat[0]
            self.patient_vel = motion_pat[1]
            self.patient_torque = motion_pat[2]




if __name__ == "__main__":
    import queue
    q = queue.Queue()
    myPub = Publisher(q)
    myPub.set_publish_interval(0.1)
    i = 5
    while True:
        q.put_nowait([i, 0])
        myPub.publish_patient_motion()
        i -= 0.01
