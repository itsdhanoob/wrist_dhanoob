from DynamixelSDK.python.src.dynamixel_sdk import *
from DynamixelSDK.python.src.dynamixel_sdk.port_handler import PortHandler
from DynamixelSDK.python.src.dynamixel_sdk.packet_handler import PacketHandler
from DynamixelSDK.python.src.dynamixel_sdk.robotis_def import *
from Tools import twosComplement, intToHex


class Motor:
    # Control table address
    ADDR_MX_TORQUE_ENABLE = 64
    ADDR_MX_GOAL_POSITION = 116
    ADDR_MX_PRESENT_POSITION = 132
    ADDR_MX_PRESENT_VELOCITY = 128
    ADDR_OPERATING_MODE = 11
    ADDR_GOAL_PWM = 100
    ADDR_GOAL_CURRENT = 102
    ADDR_GOAL_VELOCITY = 104
    ADDR_MX_PRESENT_CURRENT = 126
    ADDR_VEL_PROF = 112
    ADDR_DRIVE_MODE = 10

    def __init__(self, dxl_id, baud_rate, device_name, protocol_version):
        self.dxl_id = dxl_id
        self.baud_rate = baud_rate
        self.device_name = device_name
        self.protocol_version = protocol_version
        self.portHandler = PortHandler(device_name)
        self.packetHandler = PacketHandler(protocol_version)

    def openPort(self):
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")

    def setBaudRate(self):
        if self.portHandler.setBaudRate(self.baud_rate):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")

    def writeRegister(self, num_bytes, port_handler, motor_id, address, data):
        if num_bytes == 1:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
                port_handler,
                motor_id,
                address,
                data
            )

        elif num_bytes == 2:
            # print(f"DATA FROM PWM: {data}")
            if data <= (int("0xFFFF", 16)):
                dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
                    port_handler,
                    motor_id,
                    address,
                    data
                )
        elif num_bytes == 4:
            if data <= (int("0xFFFFFFFF", 16)):
                dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
                    port_handler,
                    motor_id,
                    address,
                    data
                )

        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))

    def readRegister(self, num_bytes, port_handler, motor_id, address):
        if num_bytes == 1:
            (dxl_read,
                dxl_comm_result,
                dxl_error) = self.packetHandler.read1ByteTxRx(
                            port_handler,
                            motor_id,
                            address
                        )

            return dxl_read

        elif num_bytes == 2:
            (dxl_read,
                dxl_comm_result,
                dxl_error) = self.packetHandler.read2ByteTxRx(
                            port_handler,
                            motor_id,
                            address
                        )

            return dxl_read

        elif num_bytes == 4:
            (dxl_read,
                dxl_comm_result,
                dxl_error) = self.packetHandler.read4ByteTxRx(
                            port_handler,
                            motor_id,
                            address
                        )

            return dxl_read

        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))

    def setMode(self, mode):
        self.writeRegister(
            1,
            self.portHandler,
            self.dxl_id,
            self.ADDR_OPERATING_MODE,
            mode
            )

    def setVelProf(self, limit):
        self.writeRegister(
            4,
            self.portHandler,
            self.dxl_id,
            self.ADDR_VEL_PROF,
            limit
            )

    def setDriveMode(self, mode):
        self.writeRegister(
            1,
            self.portHandler,
            self.dxl_id,
            self.ADDR_DRIVE_MODE,
            mode
            )

    def setTorque(self, enable_flag):
        self.writeRegister(
            1,
            self.portHandler,
            self.dxl_id,
            self.ADDR_MX_TORQUE_ENABLE,
            enable_flag
            )

    def setPosition(self, desired_position):
        desired_position = int((2048/3.14)*desired_position)
        self.writeRegister(
            4,
            self.portHandler,
            self.dxl_id,
            self.ADDR_MX_GOAL_POSITION,
            desired_position
        )

    def setVelocity(self, desired_velocity):
        factor = (128*60)/(29.31*2*3.14) # ticks-sec/rad
        desired_velocity = intToHex(4,int(desired_velocity*factor))
        self.writeRegister(
            4,
            self.portHandler,
            self.dxl_id,
            self.ADDR_GOAL_VELOCITY,
            desired_velocity
        )

    def setPWM(self, desired_pwm):
        new_desired_pwm = intToHex(2, desired_pwm)

        self.writeRegister(
            2,
            self.portHandler,
            self.dxl_id,
            self.ADDR_GOAL_PWM,
            new_desired_pwm
        )

    def setCurrent(self, desired_current):
        desired_current = intToHex(2, int(desired_current*(2047/5.5)))

        self.writeRegister(
            2,
            self.portHandler,
            self.dxl_id,
            self.ADDR_GOAL_CURRENT,
            desired_current
        )

    def readPosition(self):

        pos = self.readRegister(
            4,
            self.portHandler,
            self.dxl_id,
            self.ADDR_MX_PRESENT_POSITION
        )

        return round((3.14/2048)*(twosComplement(4, pos)), 2)  # radians

    def readVelocity(self):
        vel = self.readRegister(
            4,
            self.portHandler,
            self.dxl_id,
            self.ADDR_MX_PRESENT_VELOCITY
        )

        return round(
            (45.8*2*3.14/(200*60))*(twosComplement(4, vel)),
            2)  # rad/s

    def readVelocityRaw(self):
        vel = self.readRegister(
            4,
            self.portHandler,
            self.dxl_id,
            self.ADDR_MX_PRESENT_VELOCITY
        )

        return vel

    def readCurrent(self):
        current = self.readRegister(
            2,
            self.portHandler,
            self.dxl_id,
            self.ADDR_MX_PRESENT_CURRENT
        )

        current = twosComplement(2, current)

        return current
