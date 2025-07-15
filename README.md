# Eye-Nose-Mouth-Screen-typing

This is a small python script which allows any person to write on computer without speaking anything, The way it works is it calibrates the person eyes and head movement and shows a virtual keyboard on screen, A green cursor follows with the gaze of the person, The person can move the cursor to his/her desired character by just moving his/her head such that their nose are pointing the character. 

To then type the character a person can easily open his mouth, This movement of opening his/her mouth is able to write the character on screen.

This script is designed mainly for ALS patients who have lost their ability to speak but have some control of head movement left, With only that they are able communicate with others easily.

## Installation
Before we move toward installation, for this script to work `python 3.11` is required. If it is installed on your computer no problem, But if it isn't there please download `miniconda` and create a virtual environment with `python 3.11` using miniconda(conda).
- Open `terminal` in the `Eye-Nose-Mouth-Screen-typing` folder
- To install libraries write `pip install -r requirements.txt`

## Running the Script
- After installation is completed, To run the script run `python nose and mouth.py`

## Initial Steps
- If this is your first time, It will open a pygame(full window), But it will not work currently(No calibration is done) get out of that window and there will be another window showing your face(webcam will be on). It will ask for calibration.
- For calibration, There are 4 steps as shown on the webcam window itself.
- Look to the left edge of your computer screen and press space.
- Look at the right edge of your computer screen and press space.
- Look at the above(up) edge of your computer screen and press space.
- Look at the bottom(down) edge of your computer screen and press space.
- After each calibration, a `nose_full_calibration.json` file is created, To redo the calibration at any moment, Just delete this file and run the script again.
## Using the application

- After Calibration is done, you will be able to use the application, 
- Go to the pygame window(full screen with virtual keyboard)
- The Green cursor(box) will follow with the nose of the person that calibrated this system.
- Move your nose to the desired character and to type that character open your mouth gently, This will type the said character on screen.



