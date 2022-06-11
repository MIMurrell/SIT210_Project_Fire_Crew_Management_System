#Title: Fire Crew Management System - Nexus V1.0
#Author: Matthew Murrell - 218296335
#Date: 03/05/2022
#Purpose: The main file of the Fire Crew Management System Node.
import time
import threading
from FCMS_RFID import *
from FCMS_MQTT import *
from FCMS_FILES import *

### CONSTANTS ###
NODE_NAME = "Tanker 1"
SAVE_FILE_NAME = "Tanker_1_save.txt"
UPDATE_DELAY = 60

### GLOBAL VARIABLES ###
#Creates the list of local crew IDs based on the previously saved file (Information recovery method)
crew_ids = read_save_file(SAVE_FILE_NAME)

### FUNCTIONS ###

def on_message(client, userdata, msg):
    """
    Handles recieved MQTT Messages
    """
    global crew_ids
    payload = str(msg.payload)[2:-1]
    if msg.topic == "FCMS_Crew/Remove/"+NODE_NAME:
        if payload in crew_ids:
            crew_ids.remove (payload)
            save_crew_to_file(SAVE_FILE_NAME, crew_ids)
    elif (msg.topic == "FCMS_Crew/Add/" + NODE_NAME):
            crew_ids = handle_id(payload, crew_ids)
            message =",".join(crew_ids) + ":"+payload 
            client.publish("FCMS_Crew/"+NODE_NAME, message, qos=1)
            save_crew_to_file(SAVE_FILE_NAME, crew_ids)
    
def rfid_loop():
    """
    Updates the of crew members scanned into the station and publishes an MQTT message with the updated list.
    """
    global crew_ids
    while True:
        try:
            #print("Hold a tag near the reader")
            card_id = read_id()
            crew_ids = handle_id(card_id, crew_ids)
            message =",".join(crew_ids) + ":" + card_id
            client.publish("FCMS_Crew/"+NODE_NAME, message, qos=1)
            save_crew_to_file(SAVE_FILE_NAME, crew_ids)
            time.sleep(2)
        except KeyboardInterrupt:
            GPIO.cleanup()
        except:
            pass

def mqtt_loop():
    """
    Listens for MQTT messages until the program ends
    """
    client.loop_forever()

def update_loop():
    """
    Publishes MQTT messages with the current crew list at regular intervals.
    A fault-tolerance method to account for errors in publishing changes or 
    """
    while True:
        try:
            message =",".join(crew_ids) + ":"
            client.publish("FCMS_Crew/"+NODE_NAME, message, qos=1)
            time.sleep(UPDATE_DELAY)
        except KeyboardInterrupt:
            GPIO.cleanup()   
    
### MQTT SETUP ###
client=setup_client()
client.on_message = on_message

### MQTT THREAD ###
mqtt_thread = threading.Thread(target=mqtt_loop, daemon=True)
mqtt_thread.start()

### RFID THREAD ###
rfid_thread = threading.Thread(target=rfid_loop, daemon=True)
rfid_thread.start()

### UPDATE THREAD ###
update_thread = threading.Thread(target=update_loop, daemon=True)
update_thread.start()