from Motor import Motor

import Constants as con



class Controller:

    def __init__(self, motor):

        self.motor = motor

        self.desired_position = 0

        self.desired_vel = 0

        self.kp = 0

        self.ki = 0

        self.kd = 0

        self.kf = 1

        self.integrator = 0



    def setKp(self, kp):

        self.kp = kp



    def setKi(self, ki):

        self.ki = ki



    def setKd(self, kd):

        self.kd = kd



    def piControl(self, remote_pos, remote_vel, remote_torque, local_pos, local_vel):

        current_position = local_pos

        position_error = remote_pos - current_position



        current_vel = local_vel

        velocity_error = current_vel - remote_vel



        torque = (1 + self.kf) * (self.kp * position_error + self.kd * velocity_error) + self.kf * remote_torque

        # current overload protection

        current = self.motor.readCurrent()

        if (current) > con.current_threshold:

            print('current excedded motor will be stopped')

            self.motor.setTorque(0)



        pwm = int(73.75 * (2.93 * torque + 2.49 * current_vel))



        if pwm >= 800:

            pwm = 800

        elif pwm <= -800:

            pwm = -800



        self.motor.setPWM(pwm)

        self.motor.setPosition(remote_pos)
