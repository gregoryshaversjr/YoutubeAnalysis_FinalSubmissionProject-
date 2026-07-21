#import the Pandas library for data manipulation and analysis
import pandas as pd


#converts timestamp text into Pandas datetime values
def parse_watch_times(time_values):
    
    #Convert date type object into string type object
    time_text = time_values.astype("string")

    #removed all spaces in time stamp text and replaced with a single space
    time_text = time_text.str.replace("\u202f", " ", regex=False)

    #removes timezone abbreviations at the end of timestamp 
    time_text = time_text.str.replace( r"\s+[A-Z]{3,4}$","", regex=True)

    #convert timestamp to Pandas datetime 
    readable_times = pd.to_datetime(time_text, format="%b %d, %Y, %I:%M:%S %p", errors="coerce")

    #ISO 8601 timestamp to Pandas datetime 
    iso_times = pd.to_datetime(time_text, format="ISO8601", errors="coerce", utc=True,)

    
    #remove all timezone info and convert to Pandas datetime
    iso_times = iso_times.dt.tz_localize(None)

    #Use the converted ISO 8601 if text is not readable
    parsed_times = readable_times.fillna(iso_times)

    #return the parsed timestamp values as Pandas datetime values
    return parsed_times


#returns the total number of videos 
def get_total_videos(watch_dataframe):
    #get the total number of videos in the dataframe and return the value
    total_videos = len(watch_dataframe)
    return total_videos

#count the number of unique video titles
def get_repeat_watches(watch_dataframe):
    #count the number of times each video title appears 
    url_counts = watch_dataframe["titleUrl"].value_counts()
    #return only the video titles that appear more than once and return the results 
    repeat_watches = url_counts[url_counts > 1]
    return repeat_watches


#get the number of videos watched each month
def get_monthly_activity(watch_dataframe):
    #copy the dataframe
    dataframe_copy = watch_dataframe.copy()

    #parse the timestamp values in the "time" column and convert them to Pandas datetime values
    dataframe_copy["time"] = parse_watch_times(dataframe_copy["time"])

    #remove any rows with missing timestamp values
    dataframe_copy = dataframe_copy.dropna(subset=["time"])

    #create a new column called "month" that contains the month and year of each video watch
    dataframe_copy["month"] = dataframe_copy["time"].dt.to_period("M")

    #count the number of videos watched in each month and return the results
    monthly_activity = dataframe_copy["month"].value_counts()

    #sort the results by month in ascending order
    monthly_activity = monthly_activity.sort_index()

    #return the monthly activity counts in Pandas 
    return monthly_activity



#filter the dataframe by video title
def filter_by_title(watch_dataframe, search_text):

    #if the search text is None, return a copy of the original dataframe
    if search_text is None:
        return watch_dataframe.copy()

    #clean the search text by stripping any leading or trailing whitespace
    cleaned_search_text = str(search_text).strip()

    #if the cleaned search text is empty, return a copy of the original dataframe
    if cleaned_search_text == "":
        return watch_dataframe.copy()

    #filter the dataframe to include only rows where the "title" column contains the cleaned search text (case-insensitive)
    matching_rows = watch_dataframe["title"].str.contains(cleaned_search_text, case=False, na=False, regex=False,)

    #create a new dataframe containing only the matching rows and return it
    filtered_dataframe = watch_dataframe.loc[matching_rows].copy()


    #return the filtered dataframe sorted by timestamp in descending order
    return filtered_dataframe


#filter the dataframe by date range
def filter_by_date(watch_dataframe, start_date, end_date):

#create a copy of the original dataframe to avoid modifying it
    dataframe_copy = watch_dataframe.copy()

#parse the timestamp values in the "time" column and convert them to Pandas datetime values
    dataframe_copy["time"] = parse_watch_times(dataframe_copy["time"])

#remove any rows with missing timestamp values
    start_timestamp = pd.Timestamp(start_date)

#Convert the end date into a pandas timestamp
    end_timestamp = pd.Timestamp(end_date)

# Add one day so the entire end date is included
    day_after_end = end_timestamp + pd.Timedelta(days=1)

# Check which timestamps are on or after the start date
    after_start = dataframe_copy["time"] >= start_timestamp

# Check which timestamps are before the day after the end date
    before_day_after_end = dataframe_copy["time"] < day_after_end

# Combine both date conditions
    rows_in_date_range = after_start & before_day_after_end

# Keep only the rows that are within the date range
    filtered_dataframe = dataframe_copy.loc[rows_in_date_range].copy()

# Sort the filtered dataframe from newest to oldest
    filtered_dataframe = filtered_dataframe.sort_values( by="time", ascending=False)

# Return the filtered dataframe
    return filtered_dataframe


# Get the most recent records from the dataframe
def get_recent_records(watch_dataframe, limit=10):

# Create a copy to avoid changing the original dataframe
    dataframe_copy = watch_dataframe.copy()

# Convert the time column into pandas datetime values
    dataframe_copy["time"] = parse_watch_times(dataframe_copy["time"])

# Remove rows that have missing timestamp values
    dataframe_copy = dataframe_copy.dropna(subset=["time"])

# Sort the dataframe from newest to oldest
    sorted_dataframe = dataframe_copy.sort_values( by="time", ascending=False)

# Keep only the number of records specified by the limit
    recent_records = sorted_dataframe.head(limit).copy()

# Return the most recent records
    return recent_records
