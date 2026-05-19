"""
Author: Adam Fong
Date: 2025-08-20
Description: This module defines the CameraCart class, which provides simple abstractions to allow for the camera cart to be controlled.
"""
from Network import Axis
from Network import Controller
from BinaryCommunication import BinaryCommunication
import time
import subprocess
import ESP32SerialController

class CameraCart:
    def __init__(self, ip = '192.168.100.94', sensor_offset_mm = 794.5):
        # TODO: Add error handling for connection issues
        self.cartController = Controller(ip)
        self.cartAxle = Axis(ip, 0, "cart") 
        self.com = BinaryCommunication()
        self.path_images = None

        self.com.connect(self.cartController)
        self.com.enableDrive(self.cartAxle)

        # Camera control variables
        # self.WMI = wmi.WMI() #establishes connection with "Windows Management Instrumentation" 
        # self.wql = "Select * From Win32_USBControllerDevice" #query to search for anything that is a USB device
        # self.digicam_path = "C:\Program Files (x86)\digiCamControl\CameraControlCmd.exe"  #Path to the CameraControlCmd.exe file needed to trigger photos
        # self.camera = cart_control.Cart('192.168.100.94', 5006) #sets the IP andy port needed to connect to the cart
        # self.camera_connect()
        
        # Check if camera cart has already been homed 
        self.homed = self.get_home_successful()
        print(f"Already homed: {self.homed}")
        
        # The conversion factor to get between encoder position and actual position scaled
        self.encoder_scale_factor = 0.0034

        self.esp32 = ESP32SerialController.ESP32SerialController('COM3')
        self.sensor_offset_mm = sensor_offset_mm # mm from the bedrock of the flume

    def capture_images_wireless(self):
        return self.esp32.trigger_camera()

    def get_water_level(self):
        return round(self.sensor_offset_mm - self.esp32.get_distance(),1)
    
    def get_home_successful(self):
        return self.com.requestBit(self.cartAxle, 4600, 7)
    
    def capture_images(self,path):
        out = subprocess.check_output(                      #sends code to windows command prompt
            [self.digicam_path, "/folder", path, "/captureall"], #command to take picture
            )
        decoded = out.decode('utf-8')
        responses_split = decoded.split('\r\n')
        
        for response in responses_split:
            print(response) #prints the output of the command to the terminal so user can see if photos were taken

    def get_camera_count(self):
        camera_count = 0 
        for item in self.WMI.query(self.wql):
            if item.Dependent.Name == 'Canon EOS Rebel T6': #if device with correct camera name exists it updates the counter
                camera_count += 1

        print("{} Cameras Found".format(camera_count))
        return camera_count
    
    def camera_connect(self):
        print("Connecting cameras.")
        self.camera.connect()
    
    def jog_relative(self, value: int, blocking = True):
        self.com.move(self.cartAxle, value, Movement='r')

        if blocking:
            while self.get_moving_status():
                time.sleep(1)

    def jog_absolute(self, value:int, blocking = True):
        if not self.get_home_successful():
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

    def home(self):
        self.com.setBit(self.cartAxle, 17161) # home is in the negative direction
        self.com.setBit(self.cartAxle, 17160)                                   # jog home
        print("Homing the camera cart.\n")

        # Blocks until homed
        while self.get_home_successful() == 0:                                              # wait till card is in home position
            time.sleep(1)

    def kill_all_motions(self):
        pass

    def get_position(self):
        """
        Get position of the cart in mm.
        """
        encoder_position = self.com.requestParameter(self.cartAxle, 6144)[1] 
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

if __name__ == "__main__":
    main()