# Instructions
- bedscan is to capture overlapping images to create a 3D map of the bed using photogrammetry 
- surface water level is to capture the height of the water at multiple downstream distances

## Bedscan Instructions
- Make sure to turn off the main power strip (left) when you are done scanning! 

### Capturing Images
- Confirm the main power strip is turned on
- Confirm the data ports on the top USB hub are turned off for each of the cables (no lights showing)
- Confirm the cameras are on and show a preview of the image
    - If there is no preview, click the button on the right side of the viewfinder that looks like a cartoon camera
- open `bedscan.py` in VSCode
- click the 'play button' at the top right of the file in VSCode to run the script
    - if you get an error, change the Python interpeter to be the Python 3.14 
- The cart should move back to the downstream position, then start taking images in the upstream direction
- You can tell if the camera is taking a photo as a little red light flashes on the camera body 

### Accessing Images
- Turn the main power strip off, then back on. This is important as the data cables sometimes do not connect unless restarted
- Turn on power to each of the data USB cables on the top USB hub
- Look at the 'File Explorer' application on the computer and verify that there are 5 cameras showing on the sidebar near 'This PC', 'OneDrive' etc. 
- open each camera and drag and drop the images into a well named folder. Put the date and time into the folder name! (eg. bedscan_YYYYMMDD-HHMMSS or bedscan_20260414-143000)
- Delete the images on the cameras when you are done transferring the images. This prevents accidental inclusion of images from a different scan
- Turn off every data port in the top USB hub by clicking the little power buttons
- Turn off the main power strip

## Surface Water Level Instructions

### Capturing Height Data
- Turn on the main power strip
- Open `water_level_scan.py` in VSCode
- click the 'play button' at the top right of the file in VSCode to run the script
    - if you get an error, change the Python interpreter to be Python 3.14 
- The cart will move to the downstream position if it is not already there, then it will move in the upstream direction
- You should see in the terminal that new distance data is being recorded
- Once the cart reaches the end of the flume, it will open a quick graph of the data. When you close the graph, a csv file will be created with the data
- Turn off main power strip when you're done to give the electronics a break

### Accessing Height Data
- Open the corresponding data file (eg. water_height_scan_YYYYMMDD-HHMMSS.csv) as necessary