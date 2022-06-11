#Title: Fire Crew Management System - GUI Module
#Author: Matthew Murrell - 218296335
#Date: 03/05/2022
#Purpose: Contains functions used by the Fire Crew Management system to setup the Tkinter GUI and manage the firefighter information table

### LIBRARIES ###
from tkinter import *
from  tkinter import ttk

from FCMS_RFID import *
from FCMS_FILES import *

### CONSTANTS ###
FILENAME = "firefighterinfo.csv"

### CREW TABLE / INFO FUNCTIONS ###
def generate_crew_table(crew):
    """
    Returns table (2-dimensional list) based on the passed list of crew IDs in relation to the 
    """
    return [firefightertable[0], [i for i in firefightertable[1] if i[0] in crew]]

def is_member_id(crew_id):
    """
    Returns a Boolean value depending on whether passed ID is in the firefighter info CSV file.
    """
    for i in firefightertable[1]:
        if i[0] == crew_id:
            return True
    return False

def member_id_list():
    """
    Returns a list of all of the members in the firefighter info CSV file.
    """
    return [i[0] for i in firefightertable[1]]

def member_name(crew_id):
    """
    Returns the name attached to the passed ID.
    """
    for i in firefightertable[1]:       
        if i[0] == crew_id:
            return i[1] + " " + i[2]
    return "Name not found"



### GUI FUNCTIONS ###

def display_table(table,frame):
    """
    Displays the passed 2-dimensional list in the GUI as a table in the passed frame
    """
    fields=table[0]
    rows=table[1]
    active_table = ttk.Treeview(frame)
    active_table['columns'] = fields
    active_table.column("#0", width=0,  stretch=NO)
    active_table.heading("#0",text="",anchor=CENTER)
    for i in fields:
        active_table.column(i,anchor=CENTER, width=len(i*13))
        active_table.heading(i,text=i,anchor=CENTER)
    for i in range(len(rows)):
        active_table.insert(parent='',index='end',iid=i,text='',values=rows[i])
    active_table.pack()
    
def generate_crew_label(name, rownum):
    """
    Displays a label with the passed text on the passed row number
    """
    t1_label = Label(text = name, font = ("Helvetica", 13), bg = "white smoke")
    t1_label.grid(row=rownum, column=0)
    
def generate_crew_frame(name, rownum, id_list, frame):
    """
    Populates the passed frame with the passed information
    """
    generate_crew_label(name, rownum)
    crew_table = generate_crew_table(id_list)
    frame.grid(row=rownum+1, column=0)
    display_table(crew_table, frame)

def setup_window():
    """
    Sets up and returns the window of the GUI
    """
    win = Tk()
    win.geometry('1920x1080')
    win.configure(bg='white')
    win.title=("Firefighting Crew Monitor")
    title = Label(text = "Firefighting Crew Monitor", font = ("Helvetica", 25), bg = "firebrick1")
    title.grid(row=0, column=0) 
    return win

def setup_manual_frame(win, DEVICE_LIST):
    """
    Sets up and returns the frame of the GUI with the drop-down menus for manually entering crew members.
    """
    button_frame = Frame(win, bg="white")
    manual_label = Label(button_frame, text = "\nManual Crew Entry\n", font = ("Helvetica", 15), bg = "white")
    manual_label.grid(row=0, column=1)
    
    selected_id = StringVar()
    selected_id.set(member_id_list()[0])

    id_label = Label(button_frame, text = "ID", font = ("Helvetica", 13), bg = "white smoke")
    id_label.grid(row=1, column=0)
    id_input = OptionMenu(button_frame, selected_id, *member_id_list())
    id_input.grid(row=2, column=0)

    device_label = Label(button_frame, text = "Device", font = ("Helvetica", 13), bg = "white smoke")
    device_label.grid(row=1, column=1)

    selected_dev = StringVar()
    selected_dev.set(DEVICE_LIST[0])

    device_input = OptionMenu(button_frame, selected_dev, *DEVICE_LIST)
    device_input.grid(row=2, column=1)

    return button_frame, selected_dev, selected_id

#Reads the firefighter information table from the CSV file.
firefightertable = readcsv(FILENAME)