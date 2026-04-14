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

BEDSCAN_DISTANCE_MM = 14800 # Distance to move the cart for a bed scan in mm. Max length is 14800
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

def water_height_procedure(maximum_distance: int, step_size:int, cart:CameraCart.CameraCart):
    """
    Perform a water height scan by moving the cart and measuring water height at each step.
    
    Args:
    maximum_distance (int): The total distance to move the cart.
    step_size (int): The distance to move the cart between each measurement.
    cart (CameraCart.CameraCart): The camera cart instance.
    """
    if cart.get_home_status() == False:
        raise Exception("Camera cart has not been homed. Please home the cart before starting the water height scan.")
    
    locations = list(range(0, maximum_distance, step_size))
    locations.append(maximum_distance) # Ensure the final position is included
    heights = []
    get_position = []
    for location in locations:
        print(f"Moving to {location} mm\n")
        cart.jog_absolute(location, blocking=True)
        print(f"Measuring water height at {location} mm\n")
        water_height = cart.get_water_level()
        print(f"Water height at {location} mm: {water_height} mm\n")
        heights.append(water_height)
        get_position.append(cart.get_position()[1])

    print("Water height scan complete. Returning to home position.")
    cart.jog_absolute(0, blocking=False) # return near home

    return heights, get_position

def write_csv(heights, positions):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    with open('water_scan_' + timestamp + '.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['water_height', 'Cart Position (mm)'])
        for height, pos in zip(heights, positions):
            writer.writerow([height, pos])

def graph_heights(locations, heights):
    plt.figure(figsize=(10, 5))
    plt.plot(locations, heights / 1000, marker='o')
    plt.title('Water Height Scan')
    plt.xlabel('Cart Position (m)')
    plt.ylabel('Water Height (mm)')
    plt.grid()
    plt.show()

@time_elapsed
def main():
    cart = CameraCart.CameraCart(sensor_offset_mm=794.5)

    heights, positions = water_height_procedure(BEDSCAN_DISTANCE_MM, BEDSCAN_STEP_SIZE_MM, cart)
    print("Heights (mm): ", heights)
    print("Positions (mm): ", positions)

    graph_heights(positions, heights)

if __name__ == "__main__":
    main()
