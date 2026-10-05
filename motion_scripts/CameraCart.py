"""
Author: Adam Fong
Date: 2025-08-20
Description: This module defines the CameraCart class, which provides simple abstractions to allow for the camera cart to be controlled.
"""
from parker_hannifin_binary_communication.BinaryCommunication import BinaryCommunication
from parker_hannifin_binary_communication.Network import Controller
from parker_hannifin_binary_communication.Network import Axis
import time
import subprocess
from data_bridge_controller import ESP32DataBridgeController
import threading
from URM14 import URM14

class CameraCart:
    def __init__(self, ip = '192.168.100.94'):
        # TODO: Add error handling for connection issues
        self.cartController = Controller(ip)
        self.cartAxle = Axis(ip, 0, "cart") 
        self.com = BinaryCommunication()
        self.path_images = None

        self.com.connect(self.cartController)
        self.com.enableDrive(self.cartAxle)
        
        # Check if camera cart has already been homed 
        self.homed = self.get_home_successful()
        print(f"Already homed: {self.homed}")
        
        # The conversion factor to get between encoder position and actual position scaled
        self.encoder_scale_factor = 0.0034

        self.esp32 = ESP32DataBridgeController('COM3')
        self.distance_sensors = []

    def add_urm14(self, urm14:URM14):
        self.distance_sensors.append(urm14)

    def read_all_urm14(self):
        ids = []
        distances = []
        for urm14 in self.distance_sensors:
            distance_mm = self.esp32.get_distance(urm14.sensor_id)

            ids.append(urm14.sensor_id)
            distances.append(distance_mm)

        return ids, distances

    def capture_images_wireless(self):
        return self.esp32.trigger_camera()

    def get_water_level(self, sensor_id = 1, z_offset_mm = 0.0):
        def thread_timeout(stop_flag, timeout_flag, max_time_s = 5):
            start_time = time.time()

            while stop_flag.is_set() == False:
                if time.time() - start_time > max_time_s:
                    timeout_flag.set()
                    stop_flag.set()
                
                time.sleep(0.01)


        stop_event = threading.Event()
        timeout_event = threading.Event()
        max_time_s = 1.5

        th = threading.Thread(target=thread_timeout, args=(stop_event, timeout_event, max_time_s))
        th.start()
        water_level = round(z_offset_mm - self.esp32.get_distance(sensor_id),1)
        stop_event.set()
        th.join()

        if timeout_event.is_set():
            return -1

        return water_level
    
    def get_home_successful(self):
        return self.com.requestBit(self.cartAxle, 4600, 7)
    
    def jog_relative(self, value: int, blocking = True):
        self.com.move(self.cartAxle, value, Movement='r')

        if blocking:
            while self.get_moving_status():
                time.sleep(1)

    def jog_absolute(self, value:int, blocking = True):
        if not self.homed:
            raise Exception("The cart has NOT been homed. Do not use absolute reference frame without successfully homing to ensure an expected coordinate system. \n Go into ACR-VIEW and move the cart home. After, open 'Terminal Emulator'. Send the commands in order without the commas: PROG0, REN, RES X1")
        
        self.com.move(self.cartAxle,value, Movement='a')
        time.sleep(2) # allow the controller to receive the message before moving forward. TODO: Involve a handshake here


        if blocking:
            while self.get_moving_status():
                time.sleep(1)

    def get_moving_status(self):
        # Commented code is from other script. Maybe that is the one that works... try this if blocking doesn't work
        # res = np.binary_repr(np.float32(self.com.requestParameter(self.cartAxle, 4120)[1]).view(np.int32), width=32)
        # is_moving = res[10]

        # return int(is_moving)

        return self.com.requestBit(self.cartAxle, 4112, 5)

    def get_home_status(self):
        pass

    ## Should not be homed via software as commanding the homing velocity has not been figured out.
    # def home(self):
    #     self.com.setBit(self.cartAxle, 17161) # home is in the negative direction
    #     self.com.setBit(self.cartAxle, 17160)                                   # jog home
    #     print("Homing the camera cart.\n")

    #     # Blocks until homed
    #     while self.get_home_successful() == 0:                                              # wait till card is in home position
    #         time.sleep(1)

    def kill_all_motions(self):
        print("Killing all motions.")

        self.com.setBit(self.cartAxle, 522)


    def get_position(self):
        """
        Get position of the cart in mm.
        """
        # encoder_position = self.com.requestParameter(self.cartAxle, 6144)[1] # parameter for 'Position Encoder'
        encoder_position = self.com.requestParameter(self.cartAxle, 12290)[1] # parameter for 'Actual position Axis0'
        query_time = self.com.requestParameter(self.cartAxle, 6916)[1]
        actual_position_scaled = round(encoder_position * self.encoder_scale_factor, 2)          # read out if cart is moving position

        return (query_time, actual_position_scaled)
    def set_images_path(self, path):
        self.path_images = path

        print(f"Images will save in {self.path_images}")

    def connect(self):
        pass
    
def main():
    cc = CameraCart()
    t1, position1 = cc.get_position()
    print(f'Time:{t1} Position:{position1}')
    time.sleep(2)
    t2, position2 = cc.get_position()
    print(f'Time:{t2 - t1} Position:{position2}')

    idx, val = cc.com.requestParameter(cc.cartAxle, 12290)
    print(f"Index: {idx} Value: {val}")
    
    idx, val = cc.com.requestParameter(cc.cartAxle, 12288)
    print(f"Index: {idx} Value: {val}")
if __name__ == "__main__":
    main()