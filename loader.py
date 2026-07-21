#Import JSON tools
import json

#Import the app configuration settings
from config import Config

#Import pandas for working with dataframes
import pandas as pd


#loads the JSON records from the specified source file
def load_json_records(source):

    #open the JSON file in read mode
    with open(source, mode="r", encoding="utf-8") as file:

        #load the JSON records into a Python object
        watch_history = json.load(file)

    #return the watch history records
    return watch_history


#cleans the watch records by removing records with missing fields or empty values
def clean_watch_records(records):

    #create an empty list to store the clean records
    clean_records = []

    #loop through each record in the list
    for record in records:

        #check if the record is not a dictionary
        if not isinstance(record, dict):

            #skip the record and move to the next one
            continue

        #check if the record has all the required fields
        if "title" in record and "titleUrl" in record and "time" in record:

            #check if the required fields are not empty
            if record["title"] and record["titleUrl"] and record["time"]:

                #get the original title from the record
                raw_title = record["title"]

                #remove Watched from the beginning of the title if it is there
                clean_title = (
                    raw_title[8:]
                    if raw_title.startswith("Watched ")
                    else raw_title
                )

                #create a new dictionary with the cleaned record values
                clean_record = {
                    "title": clean_title,
                    "titleUrl": record["titleUrl"],
                    "time": record["time"],
                }

                #append the clean record to the list of clean records
                clean_records.append(clean_record)

    #return the list of clean records
    return clean_records


#builds a Pandas DataFrame from the list of clean records
def build_dataframe(clean_records):

    #create a Pandas DataFrame from the clean records
    dataframe = pd.DataFrame(clean_records)

    #return the DataFrame
    return dataframe


#loads, cleans, and builds the watch history DataFrame
def load_watch_history(source):

    #load the raw records from the JSON file
    raw_records = load_json_records(source)

    #clean the raw watch history records
    clean_records = clean_watch_records(raw_records)

    #build a Pandas DataFrame using the clean records
    dataframe = build_dataframe(clean_records)

    #return the completed DataFrame
    return dataframe
