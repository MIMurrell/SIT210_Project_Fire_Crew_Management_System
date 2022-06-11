#Title: Fire Crew Management System - Files Module
#Author: Matthew Murrell - 218296335
#Date: 03/05/2022
#Purpose: Contains functions used by the Fire Crew Management system to read and write to files.

### LIBRARIES ###
import csv

### FUNCTIONS ###
def readcsv(filename):
    """
    Reads the passed CSV file and returns it as a list containing a list of fields and a 2D list of rows
    """
    with open(filename, 'r') as csvfile:
        fields = [] #type: list
        rows = []
        csv_reader = csv.reader(csvfile)
        #Assign the table fields from the first row of the CSV file
        fields = next(csv_reader)
        #Assign the rows of the table from the remaining rows of the CSV file
        for row in csv_reader:
            rows.append(row)
        return [fields, rows]

def read_save_file(file_name):
    """
    Reads the crew list save file with the passed name and returns a crew list based on the contents.
    """
    crew_list = []
    try:
        with open(file_name) as save_file:
            for crew_id in save_file:
                crew_id = crew_id.strip("\n")
                crew_list.append(crew_id)
    except FileNotFoundError:
        pass
    return crew_list

def save_crew_to_file(file_name, crew_list):
    """
    Writes the passed crew list to the 
    """
    with open(file_name, 'w') as save_file:
        for crew_id in crew_list:
            save_file.write(crew_id)
            save_file.write("\n")
        
