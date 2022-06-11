#Title: Fire Crew Management System - Crew Module
#Author: Matthew Murrell - 218296335
#Date: 03/05/2022
#Purpose: Contains functions used by the Fire Crew Management system to manage the active crew and trigger IFTTT notifications.

### LIBRARIES ###
from datetime import datetime
import requests

### MODULES ###
from FCMS_GUI import *
from FCMS_MQTT import *
### FUNCTIONS ###
def conv_hours_to_secs(hours):
    """
    Returns the passed number of hours in seconds.
    """
    return hours * 3600

def generate_active_mem(location, id_num):
    """
    Returns a  entry for the 'active member' basd on the passed information.
    """
    newmem = {"id":id_num,
          "time_started":datetime.now(),
          "last_active":datetime.now(),
          "location":location,
          "alerted":False
          }
    return newmem

def test_loc_against_act(location, crewlist, active_crew):
    """
    Tests each member of the passed 'local' crew against the active crew and creates new entries for each member not in the active crew. Returns the active crew.
    """ 
    for i in crewlist:
        not_in_act = True
        for j in active_crew:
            if j["id"] == i:
                not_in_act = False
                break
        if not_in_act:
            #If a member of the local crew is not 
            active_crew.append(generate_active_mem(location, i))
    return active_crew



def update_last_active(crew_member):
    """
    Updates the 'Last Active' value for the passed active crew member to the current time.
    """
    if crew_member["active"]:
        crew_member["last_active"] = datetime.now()
    return crew_member

def test_crew_times(active_crew, warning, reset):
    """
    Tests the time that each member of the active crew has been active or inactive for, handles them and returns the updated crew
    """
    for i in active_crew:
        i = update_last_active(i)
        #If the member has been active for more that the specified amount of time and has not already been alerted, an IFTTT event is triggered. 
        if ((datetime.now() - i["time_started"]).seconds > conv_hours_to_secs(warning)) and not i["alerted"]:
            i["alerted"] = True
            payload = { "value1":member_name(i["id"]),
                        "value2":str(warning)
                }
            requests.post('https://maker.ifttt.com/trigger/fireground_limit_reached/with/key/crLEMJDGkHWBjQ_6NO12Ez', payload)
        #If the member has been inactive for more that the specified amount of time, they are removed from the list.
        elif (datetime.now() - i["last_active"]).seconds > conv_hours_to_secs(reset):
            active_crew.remove(i)
    return active_crew
