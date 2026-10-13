# 18m Flume Camera Cart

## motion_scripts

- `move_cart.py`
    - Edit this file to move the cart using a relative or absolute position
- `camera_bedscan.py`
    - This file takes images at a given distance interval until the end position is reached. When you run this, make sure that the USB data ports are not on otherwise images cannot be triggered. You should be able to hear the shutter and see the red LED toggle on each camera.
- `surface_height_scan.py`
    - This file measures the height of the water surface if water is running, or the bed if there is no water running. 

## analysis_scripts
- `slope_summary.py`
    - Analyzes the slope in a specific region of interest. Regions of interest are defined in `config.toml`.