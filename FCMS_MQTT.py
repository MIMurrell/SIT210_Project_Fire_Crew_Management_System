#Title: Fire Crew Management System - MQTT Module
#Author: Matthew Murrell - 218296335
#Date: 03/06/2022
#Purpose: Contains functions used by the Fire Crew Management system to publish and listen to MQTT messages

### LIBRARIES ###
import time
import paho.mqtt.client as paho
from paho import mqtt
from FCMS_RFID import *


### CONSTANTS ###
USERNAME = "RFID_FCMS"
PASSWORD = "RFID_FCMS_p@55"
URL = "f7df984e430849e88dd2e91b9ca56964.s1.eu.hivemq.cloud"

### FUNCTIONS ###
def remove_from_loc_crew(client, node_name, id_to_remove):
    """
    Publishes a message that causes the passed node to remove the passed ID from its local crew list
    """
    client.publish("FCMS_Crew/Remove/"+node_name, id_to_remove, qos=1)

def on_connect(client, userdata, flags, rc, properties=None):
    """
    Blinks all LEDs three times to inform users that the client has successfully connected
    """
    for i in range(3):
        all_lights(0)
        time.sleep(0.25)
        all_lights(1)
        time.sleep(0.25)

    
def setup_client():
    """
    Returns the set up and connected client object, based on the USERNAME, PASSWORD and URL constants.
    """
    while True:
        try:
            #Creates the client object
            client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
            client.on_connect = on_connect
            #Enables the TLS Protocol
            client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
            #Sets the username and password
            client.username_pw_set(USERNAME, PASSWORD)
            #Connects the client to the cloud
            client.connect(URL, 8883)
            client.subscribe("FCMS_Crew/#", qos=1)
            break
        except:
            #When there is an error, the red LED light up before the process is attempted again
            GPIO.output(RED_PIN, 1)
            time.sleep(1.5)
            GPIO.output(RED_PIN, 0)
            time.sleep(1.5)
    return client
            