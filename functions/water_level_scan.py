"""
Author: Adam Fong
Date: 2026-04-14
Description: This script is meant to provide a safe way to perform a water height scan with the camera cart.
"""

import CameraCart
import time     
from pathlib import Path
import sys
import csv
import matplotlib.pyplot as plt
import threading

BEDSCAN_DISTANCE_MM = 14400 # Distance to move the cart for a bed scan in mm. Max length is 14600
BEDSCAN_STEP_SIZE_MM = 140 # Distance to move the cart between each photo in mm. Suggested step size is 140

def time_elapsed(func):
    """
    Decorator to time the execution of a function.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Execution time: {end_time - start_time:.2f} seconds")
        return result
    return wrapper

class WaterLevelScanner:
    def __init__ (self,):
        self.bedscan_distance = BEDSCAN_DISTANCE_MM
        self.bedscan_step_size = BEDSCAN_STEP_SIZE_MM
        self.cart = CameraCart.CameraCart(sensor_offset_mm=794.5)
        self.heights = []
        self.positions = []
        self.stop_thread = threading.Event()

    def water_height_procedure_steps(self):
        """
        Perform a water height scan by moving the cart and measuring water height at each step.
        """
        if self.cart.get_home_status() == False:
            raise Exception("Camera cart has not been homed. Please home the cart before starting the water height scan.")
        
        locations = list(range(0, self.bedscan_distance, self.bedscan_step_size))
        locations.append(self.bedscan_distance) # Ensure the final position is included
        heights = []
        positions = []
        for location in locations:
            print(f"Moving to {location} mm\n")
            self.cart.jog_absolute(location, blocking=True)
            print(f"Measuring water height at {location} mm\n")
            water_height = self.cart.get_water_level()
            print(f"Water height at {location} mm: {water_height} mm\n")
            self.heights.append(water_height)
            self.positions.append(self.cart.get_position()[1])

        print("Water height scan complete. Returning to home position.")
        self.cart.jog_absolute(0, blocking=False) # return near home

        return self.heights, self.positions

    def water_height_procedure_rapid(self):
        # Ensure starting at home position
        self.cart.jog_absolute(0)

        # Start a thread to record the distance and height data 
        record_thread = threading.Thread(target=self.record_data_constant, args=(self.stop_thread,))
        record_thread.start()
        self.cart.jog_absolute(self.bedscan_distance, blocking=True)
        self.stop_thread.set() # signal the recording thread to stop after movement is complete
        record_thread.join()

        # Go back home after scan
        print("Water height scan complete.")
        time.sleep(1)
        print("Returning to home position.")
        self.cart.jog_absolute(0, blocking=False)

        return self.heights, self.positions

    def record_data_constant(self, stop_event):
        while stop_event.is_set() == False:
            pos = self.cart.get_position()[1]
            height = self.cart.get_water_level()

            if pos > self.bedscan_distance + 500: # if the cart goes too far, stop the scan to prevent damage to the cart and flume
                self.cart.kill_all_motions()
                print("Cart has seen an error which says it's past the maximum distance limit. Repeat the water scan.")
                sys.exit()

            self.positions.append(pos)
            self.heights.append(height)
            time.sleep(0.05)

    def write_csv(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        with open('water_height_scan_' + timestamp + '.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['water_height_mm', 'position_mm'])
            for height, pos in zip(self.heights, self.positions):
                writer.writerow([height, pos])

        print("Wrote data to water_height_scan_" + timestamp + ".csv")

    def graph_heights(self):
        plt.figure(figsize=(10, 5))
        plt.ylim((-10, max((max(self.heights) + 10, 500))))
        plt.plot(self.positions, self.heights, marker='o')
        plt.title('Water Height Scan')
        plt.xlabel('Cart Position (mm)')
        plt.ylabel('Water Height (mm)')
        plt.grid()
        plt.show()

@time_elapsed
def main():
    water_scanner = WaterLevelScanner()

    # Option 1: Scanning without stopping 
    heights, positions = water_scanner.water_height_procedure_rapid()

    # Option 2: Scanning with stopping at each step defined in the top of the file
    # heights, positions = water_scanner.water_height_procedure_steps()

    water_scanner.write_csv()
    water_scanner.graph_heights()

if __name__ == "__main__":
    main()
