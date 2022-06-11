#Title: Fire Crew Management System - RFID Module
#Author: Matthew Murrell - 218296335
#Date: 03/05/2022
#Purpose: Contains functions used by the Fire Crew Management system to handle the connected MFRC522 Module and LED lights

### LIBRARIES ###
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()
import RPi.GPIO as GPIO
GPIO.setwarnings(False)

#LED PINS
RED_PIN = 36
GREEN_PIN = 38
BLUE_PIN = 40

#GPIO Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)

def all_lights(status):
    """
    Turns all LEDs either on or off, depending on whether the passed value is True or False
    """

    for light in [RED_PIN, BLUE_PIN, GREEN_PIN]:
        GPIO.output(light, status)

def handle_id(id_num, crew_list):
    """
    Either adds or removes the passed ID to or from  the passed crew list
    """
    if str(id_num) in crew_list:
        crew_list.remove(str(id_num))
        GPIO.output(BLUE_PIN, 1)
    else:
        GPIO.output(GREEN_PIN, 1)
        crew_list.append(str(id_num))
    return crew_list

def read_id():
    """
    Waits for an ID to be scanned with all lights on. When one is, turns all lights off and returns the scanned ID.
    """
    all_lights(1)
    scanned_id = reader.read()[0] #The read method returns a tuple with id, text. Only id is used
    all_lights(0)
    return str(scanned_id)
