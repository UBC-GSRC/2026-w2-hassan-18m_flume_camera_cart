# This controller needs to do a few things
# 1. Send serial messages packaged in a struct for the data_bridge ESP32 to read and relay to data_acquisition
# 2. Listen to the serial messages from the data_bridge and get the data 
# 3. Be used by another program to perform a bedscan by calling all the functions in this controller
# Resources on struct packing & serial in python: https://alknemeyer.github.io/embedded-comms-with-python/

# From a higher level this controller will allow for 
# 1. request camera trigger returning an acknowledgement
# 2. request distance measurement returning a distance value 

# This means the data_bridge will listen to a UART, decode the message into a struct, and act accordingly
import serial
import struct
import time

class ESP32SerialController:
    def __init__(self,com = "COM4"):
        self.node_id = 0 # see type_definition/data_packet.h for type definition
        self.struct_rule = '<B??H' # 1 + 1 + 1 + 2 = 5 bytes: 1 unsigned char, 2 bools, 1 unsigned short see format character table https://docs.python.org/3/library/struct.html#format-characters
        self.buffer_size = 1024 
        
        try:
            self.port = serial.Serial(com, baudrate=115200, timeout=1)
            self.port.open()
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")

    def trigger_camera(self)->bool:
        self.port.reset_input_buffer()

        msg = struct.pack(self.struct_rule, self.node_id, True, False, 0)
        self.port.write(msg)
        time.sleep(0.1)

        # wait for response from data_bridge for camera trigger acknowledgement
        res_bytes = self.port.read(5) # read 5 bytes for the response

        try:
            node_id, camera_triggered, distance_measured, distance = struct.unpack(self.struct_rule, res_bytes) 
            print(f"Received response - Node ID: {node_id}, Camera Triggered: {camera_triggered}, Distance Measured: {distance_measured}, Distance: {distance} mm")
        except struct.error as e :
            print(f"Error unpacking serial data: {e}")
            print(f"Received bytes: {res_bytes}")
            return -1
        
        time.sleep(0.1)

        return camera_triggered # return the camera trigger acknowledgement from the data_bridge
    
    def get_distance(self)->int:
        self.port.reset_input_buffer()

        msg = struct.pack(self.struct_rule, self.node_id, False, True, 0)
        self.port.write(msg)
        time.sleep(0.1)

        # Clear any garbage data in the input buffer before reading the response

        # wait for response from data_bridge for distance measurement
        res_bytes = self.port.read(5) # read 5 bytes for the response

        try:
            node_id, camera_triggered, distance_measured, distance = struct.unpack(self.struct_rule, res_bytes) 
            print(f"Received response - Node ID: {node_id}, Camera Triggered: {camera_triggered}, Distance Measured: {distance_measured}, Distance: {distance} mm")
        except struct.error as e :
            print(f"Error unpacking serial data: {e}")
            print(f"Received bytes: {res_bytes}")
            return -1

        time.sleep(0.1)

        if distance != 65535:
            return distance / 10 # decimal unpacking
        else:
            return -1 # error value for distance measurement failure
        
def main():
    try:
        controller = ESP32SerialController()
        # Example usage
        print("Press Enter to call function")
        while (1):
            input()
            distance = controller.get_distance()
            print(f"Distance measured: {distance} mm")
            time.sleep(0.5)
            camera_shutter = controller.trigger_camera()
            print(f"Camera shutter triggered: {camera_shutter}")
    except KeyboardInterrupt:
        if controller.port.is_open:
            controller.port.close()


if __name__ == "__main__":
    main()
