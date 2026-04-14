"""
Author: Adam Fong
Date: 2025-08-20
Description: This script is meant to provide a safe way to perform a bed scan with the camera cart.
"""

import CameraCart
import time     
from pathlib import Path
import sys


BEDSCAN_DISTANCE_MM = 14600 # Distance to move the cart for a bed scan in mm. Max length is 14600
BEDSCAN_STEP_SIZE_MM = 140 # Distance to move the cart between each photo in mm. Suggested step size is 140

def prompt_directory()-> Path:
    """
    Prompts the user to select a directory for saving images.
    Returns:
    """
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()  # Hide the main window
    dir = filedialog.askdirectory(title="Select a directory")

    if not dir:
        raise Exception(f"The user must select a valid directory to proceed.")
    
    return Path(dir)

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

def bedscan_procedure(maximum_distance: int, step_size:int, cart:CameraCart.CameraCart):
    """
    Perform a bed scan by moving the cart and capturing images at each step.
    
    Args:
    maximum_distance (int): The total distance to move the cart.
    step_size (int): The distance to move the cart between each photo.
    cart (CameraCart.CameraCart): The camera cart instance.
    """
    if cart.get_home_status() == False:
        raise Exception("Camera cart has not been homed. Please home the cart before starting the bed scan.")
    
    # cart.get_camera_count()

    cart.jog_absolute(0) # Ensure starting at home position

    locations = list(range(0, maximum_distance, step_size))
    locations.append(maximum_distance) # Ensure the final position is included

    for location in locations:
        print(f"Moving to {location} mm\n")
        cart.jog_absolute(location, blocking=True)
        print(f"Capturing image at {location} mm\n")
        print(f"Image captured: {cart.capture_images_wireless()}")
        # cart.capture_images(cart.path_images) # TODO: confirm that this is blocking 

    print("Bed scan complete. Returning to home position.")
    cart.jog_absolute(0, blocking=False) # Return near home position after scan

@time_elapsed
def main():
    # dir = prompt_directory()
    cart = CameraCart.CameraCart()
    # cart.set_images_path(dir)

    # if not cart.get_home_successful():
    #     cart.home()
    # else:
    #     print("No need to explicitly home. Moving to first target location.")

    bedscan_procedure(BEDSCAN_DISTANCE_MM, BEDSCAN_STEP_SIZE_MM, cart)

if __name__ == "__main__":
    main()
