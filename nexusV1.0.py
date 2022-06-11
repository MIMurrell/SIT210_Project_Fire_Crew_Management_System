#Title: Fire Crew Management System - Nexus V1.0
#Author: Matthew Murrell - 218296335
#Date: 03/05/2022
#Purpose: The main file of the Fire Crew Management System Nexus

### LIBRARIES ###
from tkinter import *
import time
import threading
from datetime import datetime

### MODULES ###
from FCMS_RFID import *
from FCMS_MQTT import *
from FCMS_GUI import *
from FCMS_CREW import *

###CONSTANTS###
NEXUS_NAME = "In Station"
DEVICE_LIST = [NEXUS_NAME, "Tanker 1"]
SAVE_FILE_NAME = "In_Station_save.txt"
ACTIVE_HOURS_WARNING = 0.001
HOURS_RESET = 24
REFRESH_RATE = 2

###GLOBAL VARIABLES###
RUNNING = True
active_crew = [] #type:list
sta_crew_ids = read_save_file(SAVE_FILE_NAME)

###ACTIVE CREW FUNCTIONS###
def test_act_against_loc(location, loc_crew, act_crew, new_id):
    """
    Updates the active crew list with the passed local crew list
    """
    #Tests if each member of the active crew is in the passedlocal crew
    for i in act_crew:
        if i["id"] in loc_crew:
            #If a member is, and they are the new ID being scanned on, their location is updated to that of the local crew
            if i["location"] != location:
                if (new_id == i["id"]) or (not i["active"]):
                    #The ID is removed from its prior local crew
                    remove_from_loc_crew(client, i["location"] , i["id"])
                    #The location and active status of the ID in the active crew is updated
                    i["location"] = location
                else:
                    remove_from_loc_crew(client, location , i["id"])
                    
            i["active"] = True
        else:
            #If an ID is not in the local list and it's location is the passed location, it is set to inactive
            if i["location"] == location:
                i["active"] = False
                
def clean_crewlist(crewlist, location):
    for i in crewlist:
        if not is_member_id(i):
            if i:
                print ("Unregistered card scanned:", i)
            remove_from_loc_crew(client, location, i)                
def update_active_crew(location, crewlist, new_id):
    """
    Updates the active crew list with the passed local crew list and updates the GUI
    """
    global active_crew
    clean_crewlist(crewlist, location)
    active_crew = test_loc_against_act(location, crewlist, active_crew)
    test_act_against_loc(location, crewlist, active_crew, new_id)
    #Updates the GUI frames for the crew
    update_crew_frames(active_crew)

def check_crew_loop():
    """
    Tests the time that each member of the 'active' crew has been active for, and handles any that have been active/inactive for too long
    """
    while RUNNING:
        try:
            global active_crew
            active_crew = test_crew_times(active_crew, ACTIVE_HOURS_WARNING, HOURS_RESET)
            time.sleep(REFRESH_RATE)
        except KeyboardInterrupt:
            close()           

### RFID FUNCTIONS ###
def rfid_loop():
    """
    Creates a list of crew members scanned into the station and updates the GUI accordingly
    """
    global sta_crew_ids   
    while RUNNING:
        try:
            card_id = str(read_id())
            sta_crew_ids = handle_id(card_id, sta_crew_ids)
            update_active_crew(NEXUS_NAME, sta_crew_ids, card_id)
            save_crew_to_file(SAVE_FILE_NAME, sta_crew_ids)
            time.sleep(2)          
        except KeyboardInterrupt:
            close()

### GUI FUNCTIONS ###        
def update_crew_frames(act_crew):
    """
    Updates the GUI frames for each device/location
    """
    #Clears the current list of frames
    crew_frame_list = []
    #For each location, creates a new frame, populates it with the relevant members and generates it
    for i in range(len(DEVICE_LIST)):
        crew_frame_list.append(Frame(win))
        loc_crew = [j["id"] for j in act_crew if j["location"] == DEVICE_LIST[i] and j["active"]]
        generate_crew_frame(DEVICE_LIST[i], i*2+2, loc_crew, crew_frame_list[i]) 

def add_or_rem_from_loc_crew():
    """
    Publishes a message that causes the passed node to remove the passed ID from its local crew list
    """
    node_name = selected_dev.get()
    id_to_pub = selected_id.get()
    client.publish("FCMS_Crew/Add/"+node_name, id_to_pub, qos=1)
    
    
def close():
    """
    Turns all LEDs off, cleans up the GPIO pins and closes the GUI window.
    """
    global RUNNING
    RUNNING = False
    #Turns off the lights
    all_lights(0)
    #Cleans up the GPIO pins
    GPIO.cleanup()
    #Closes the GUI window
    win.destroy()

### MQTT FUNCTIONS ###
def on_message(client, userdata, msg):
    """
    Handles subscribed-to MQTT messages. 
    """
    global sta_crew_ids
    #Removes the pre/postamble of the payload
    payload = str(msg.payload)[2:-1]
    #If message has the relevant topic & subtopic, the ID in the payload is removed from the local crew list.
    if (msg.topic == "FCMS_Crew/Remove/" + NEXUS_NAME):
        if payload in sta_crew_ids:
            sta_crew_ids.remove(payload)
            save_crew_to_file(SAVE_FILE_NAME, sta_crew_ids) 
    #If message has the relevant topic & subtopic, the ID in the payload treated as if it were scanned into the system.
    elif (msg.topic == "FCMS_Crew/Add/" + NEXUS_NAME):
            sta_crew_ids = handle_id(payload, sta_crew_ids)
            update_active_crew("In Station", sta_crew_ids, payload)
            save_crew_to_file(SAVE_FILE_NAME, sta_crew_ids)
    #If the message does not have a 'removal' or 'add' topic, the message is handled as a crew update from a node.
    elif (msg.topic[10:16] != "Remove"):
        node_name = msg.topic[10:]
        #Splits the message into the crew list and the new ID, if any
        splitload = payload.split(":")
        crew_ids = splitload[0].split(",")
        #Assigns the new_id variable using  the 'new id' section of the message (Anthing after the colon).
        if len(splitload) > 1:
            new_id = splitload[1]
        else:
            #If there is no new ID, it is given a null value
            new_id = ""
        #Updates the active crew with the local crew IDs of the message.
        update_active_crew(node_name, crew_ids, new_id)
            
def mqtt_loop():
    """
    Listens for MQTT messages. 
    """    
    client.loop_forever()


### GUI SETUP ###
win = setup_window()

button_frame, selected_dev, selected_id  = setup_manual_frame(win,DEVICE_LIST)

#Adding the Button to manually add/remove IDs to the manual frame.
AddRemoveButton = Button(button_frame, text = "Add/Remove", font = ("Helvetica", 13), command = add_or_rem_from_loc_crew, height = 1, width = 10)
AddRemoveButton.grid(row=2, column=2)

button_frame.grid(row=len(DEVICE_LIST)*2+4)

win.protocol("WM_DELETE_WINDOW", close)

#Initializing the crew frames.
update_active_crew(NEXUS_NAME, sta_crew_ids, "")

### MQTT SETUP ###
client = setup_client()
client.on_message = on_message

### RFID THREAD ###
rfid_thread = threading.Thread(target=rfid_loop, daemon=True)
rfid_thread.start()

### MQTT THREAD ###
mqtt_thread = threading.Thread(target=mqtt_loop, daemon=True)
mqtt_thread.start()

### ACTIVE CREW THREAD ###
active_thread = threading.Thread(target=check_crew_loop, daemon=True)
active_thread.start()

### GUI LOOP ###
win.mainloop()