
#Import JSON tools
import json

#Import pandas for working with dataframes
import pandas as pd

#Import Streamlit for building the app
import streamlit as st

#Import the analyzer functions
from analyzer import (filter_by_date, filter_by_title, get_monthly_activity, get_recent_records, get_repeat_watches, get_total_videos, parse_watch_times)

#Import the app configuration
from config import Config

#Import the data loading functions
from loader import clean_watch_records, load_watch_history

#Import the storage functions
from storage import ( clear_uploaded_data,dataframe_to_csv_bytes, get_active_data_path, load_app_state, save_app_state, save_uploaded_file)


#Get all valid dates from the dataframe
def get_valid_dates(dataframe):

    #Check if the dataframe does not have a time column
    if "time" not in dataframe.columns:

        #Create an empty datetime series
        empty_dates = pd.Series(dtype="datetime64[ns]")

        #Return the empty dates
        return empty_dates

    #Convert the time values into Pandas datetime values
    parsed_times = parse_watch_times(dataframe["time"])

    #Remove any missing date values
    valid_dates = parsed_times.dropna()

    #Return all the valid dates
    return valid_dates


#Process a JSON file uploaded by the user
def handle_upload(uploaded_file):

    #Try to read and check the uploaded file
    try:

        #Show a loading message while checking the file
        with st.spinner("Checking your JSON file..."):

            #Get the uploaded file as bytes
            uploaded_bytes = uploaded_file.getvalue()

            #Convert the uploaded bytes into text
            uploaded_text = uploaded_bytes.decode("utf-8")

            # onvert the JSON text into Python data
            uploaded_records = json.loads(uploaded_text)

            #Check if the uploaded data is not a list
            if not isinstance(uploaded_records, list):

                #Raise an error when the JSON does not contain a list
                raise ValueError("The JSON file must contain a list of records.")

            #Create an empty list for dictionary records
            dictionary_records = []

            #Go through every record in the uploaded data
            for record in uploaded_records:

                #Check if the record is a dictionary
                if isinstance(record, dict):

                    #dd the dictionary record to the list
                    dictionary_records.append(record)

            #Check if any uploaded records were not dictionaries
            if len(dictionary_records) != len(uploaded_records):

                #Raise an error if an item is not a record object
                raise ValueError("Every item in the JSON list must be a record object.")

            #Clean the uploaded YouTube records
            clean_records = clean_watch_records(dictionary_records)

            #Check if there are no valid records
            if len(clean_records) == 0:

                #Raise an error when no valid records were found
                raise ValueError("No valid YouTube watch records were found.")

            #Save the uploaded file
            save_uploaded_file(uploaded_file)

            #Change the app state to uploaded mode
            save_app_state(Config.UPLOADED_MODE)

        #Show a message with the number of valid records
        st.success(f"Upload complete. {len(clean_records):,} valid records found.")

        #Rerun the Streamlit app
        st.rerun()

    #Catch any errors caused by the uploaded file
    except (AttributeError, json.JSONDecodeError, OSError, TypeError, UnicodeDecodeError, ValueError) as error:

        # Show the upload error to the user
        st.error(f"Upload failed: {error}")


# Display all the sidebar controls
def render_sidebar(dataframe, app_state):

    # Add a Controls heading to the sidebar
    st.sidebar.header("Controls")

    # Get the current mode or use demo mode as the default
    current_mode = app_state.get("mode", Config.DEMO_MODE)

    # Check if the app is using uploaded data
    if current_mode == Config.UPLOADED_MODE:

        # Show that uploaded data is being used
        st.sidebar.success("Using uploaded data")

    # Run this when the app is not using uploaded data
    else:

        # Show that demo data is being used
        st.sidebar.info("Using demo data")

    # Add a JSON file uploader to the sidebar
    uploaded_file = st.sidebar.file_uploader( "Upload watch-history JSON", type=["json"],)

    # Add a button for using the uploaded file
    upload_button_clicked = st.sidebar.button("Use uploaded file", disabled=uploaded_file is None,width="stretch")

    # Check if the upload button was clicked
    if upload_button_clicked:

        # Process the uploaded file
        handle_upload(uploaded_file)

    # Add a button for returning to the demo data
    reset_button_clicked = st.sidebar.button("Reset to demo data", disabled=current_mode != Config.UPLOADED_MODE, width="stretch")

    # Check if the reset button was clicked
    if reset_button_clicked:

        # Delete the uploaded data and return to demo mode
        clear_uploaded_data()

        # Save a value so the reset message can be shown
        st.session_state["show_reset_message"] = True

        # Rerun the Streamlit app
        st.rerun()

    # Check if the reset message should be displayed
    if st.session_state.pop("show_reset_message", False):

        # Show that the demo data was restored
        st.sidebar.success("Demo data restored.")

    # Add a divider to the sidebar
    st.sidebar.divider()

    # Add a title search box to the sidebar
    search_text = st.sidebar.text_input("Search video titles", placeholder="Enter part of a title")

    # Get the valid dates from the dataframe
    valid_dates = get_valid_dates(dataframe)

    # Give the start date an empty value
    start_date = None

    # Give the end date an empty value
    end_date = None

    # Check if there are no valid dates
    if valid_dates.empty:

        # Show a warning that date filtering is not available
        st.sidebar.warning("No valid dates are available for filtering.")

    # Run this when valid dates are available
    else:

        # Get the earliest date in the data
        earliest_date = valid_dates.min().date()

        # Get the latest date in the data
        latest_date = valid_dates.max().date()

        # Add a start date input to the sidebar
        start_date = st.sidebar.date_input("Start date", value=earliest_date, min_value=earliest_date, max_value=latest_date)

        # Add an end date input to the sidebar
        end_date = st.sidebar.date_input("End date", value=latest_date, min_value=earliest_date, max_value=latest_date)

    # Add a slider for choosing the number of recent records
    recent_limit = st.sidebar.slider("Recent records", min_value=5, max_value=50, value=10, step=5)

    # Store all the sidebar control values in a dictionary
    controls = {"search_text": search_text, "start_date": start_date, "end_date": end_date, "recent_limit": recent_limit}

    # Return all the sidebar control values
    return controls


# Display the main record totals
def render_metrics(dataframe):

    # Get the total number of video records
    total_records = get_total_videos(dataframe)

    # Get the number of watches for repeated URLs
    repeat_counts = get_repeat_watches(dataframe)

    # Count how many URLs were watched more than once
    repeated_urls = len(repeat_counts)

    # Check if there are no repeated URLs
    if repeat_counts.empty:

        # Set the additional watches to zero
        additional_watches = 0

    # Run this when repeat watches were found
    else:

        # Remove the first watch from each repeat count
        watches_after_first = repeat_counts - 1

        # Add all the extra watches together
        additional_watches = int(watches_after_first.sum())

    # Create three columns for the totals
    total_column, repeats_column, additional_column = st.columns(3)

    # Display the total number of records
    total_column.metric(
        "Total records",f"{total_records:,}")

    # Display the number of repeated URLs
    repeats_column.metric( "Repeated URLs", f"{repeated_urls:,}")

    # Display the number of additional watches
    additional_column.metric("Additional watches", f"{additional_watches:}")


# Build a table containing repeat watches
def build_repeat_table(dataframe):

    # Get the watch counts for repeated URLs
    repeat_counts = get_repeat_watches(dataframe)

    # Convert the repeat counts into a dataframe
    repeat_table = repeat_counts.rename("watch_count").reset_index()

    # Check if the repeat table is empty
    if repeat_table.empty:

        # Return the empty repeat table
        return repeat_table

    # Keep one record for each video URL
    one_row_per_url = dataframe.drop_duplicates(subset=["titleUrl"])

    # Match each URL with its video title
    title_lookup = one_row_per_url.set_index("titleUrl")["title"]

    # Find the title for every repeated URL
    repeat_titles = repeat_table["titleUrl"].map(title_lookup)

    # Add the video titles to the beginning of the table
    repeat_table.insert(0, "title", repeat_titles)

    # Return the completed repeat table
    return repeat_table


# Build a table containing monthly activity
def build_monthly_table(dataframe):

    # Get the number of watches for each month
    monthly_counts = get_monthly_activity(dataframe)

    # Convert the monthly counts into a dataframe
    monthly_table = monthly_counts.rename("watch_count").reset_index()

    # Check if the monthly table has records
    if not monthly_table.empty:

        # Convert the month values into strings
        monthly_table["month"] = monthly_table["month"].astype(str)

    # Return the monthly activity table
    return monthly_table


# Display all the data tables in tabs
def render_tables(dataframe, recent_limit):

    # Get the most recent watch records
    recent_records = get_recent_records(dataframe, recent_limit)

    # Build the table of repeated watches
    repeat_table = build_repeat_table(dataframe)

    # Build the table of monthly activity
    monthly_table = build_monthly_table(dataframe)

    # Create the tabs used to display each table
    recent_tab, repeats_tab, monthly_tab, records_tab = st.tabs(["Recent records", "Repeat watches", "Monthly activity", "All records"])

    # Display content inside the recent records tab
    with recent_tab:

        # Check if there are no recent records
        if recent_records.empty:

            # Show a message when no recent records were found
            st.info("No recent records were found.")

        # Run this when recent records were found
        else:

            # Display the recent records dataframe
            st.dataframe(recent_records, width="stretch", hide_index=True)

    # Display content inside the repeat watches tab
    with repeats_tab:

        # Check if there are no repeated videos
        if repeat_table.empty:

            # Show a message when no repeated videos were found
            st.info("No repeated videos were found.")

        # Run this when repeated videos were found
        else:

            # Display the repeat watch table
            st.dataframe(repeat_table, width="stretch", hide_index=True)

    # Display content inside the monthly activity tab
    with monthly_tab:

        # Check if there is no monthly activity
        if monthly_table.empty:

            # Show a message when no monthly activity was found
            st.info("No monthly activity was found.")

        # Run this when monthly activity was found
        else:

            # Display the monthly activity table
            st.dataframe(monthly_table, width="stretch", hide_index=True)

    # Display content inside the all records tab
    with records_tab:

        # Display the complete dataframe
        st.dataframe(dataframe, width="stretch", hide_index=True, height=500)


# Run the main YouTube analyzer app
def main():

    # Set the Streamlit page settings
    st.set_page_config( page_title="YouTube Watch History Analyzer", page_icon="▶️", layout="wide")

    # Display the main app title
    st.title("YouTube Watch History Analyzer")

    # Try to load the app state and watch history
    try:

        # Load the saved app mode
        app_state = load_app_state()

        # Get the path of the data file that should be used
        active_data_path = get_active_data_path(app_state)

        # Check if uploaded mode is saved but the demo file is being used
        if (app_state.get("mode") == Config.UPLOADED_MODE and active_data_path == Config.WATCH_HISTORY_PATH):

            # Change the app back to demo mode
            app_state = save_app_state(Config.DEMO_MODE)

        # Show a moving spinner while the larger file is loading
        with st.spinner("Stand by... Loading your watch history."):

            # Load the watch-history data into a dataframe
            watch_dataframe = load_watch_history(active_data_path)

    # Catch an error if the watch-history file is missing
    except FileNotFoundError:

        # Show that the file could not be found
        st.error("The watch-history JSON file could not be found.")

        # Stop running the Streamlit app
        st.stop()

    # Catch other errors caused by loading the data
    except (json.JSONDecodeError, OSError, TypeError, UnicodeDecodeError, ValueError) as error:

        # Show the data loading error
        st.error(f"The watch-history data could not be loaded: {error}")

        # Stop running the Streamlit app
        st.stop()

    # Check if the watch-history dataframe is empty
    if watch_dataframe.empty:

        # Show a warning when no records were found
        st.warning("No valid watch-history records were found.")

        # Stop running the Streamlit app
        st.stop()

    # Display the sidebar and get the selected controls
    controls = render_sidebar(watch_dataframe, app_state)

    # Get the search text and remove extra spaces around it
    search_text = controls["search_text"].strip()

    # Get the selected start date
    start_date = controls["start_date"]

    # Get the selected end date
    end_date = controls["end_date"]

    # Check if the start date comes after the end date
    if (start_date is not None and end_date is not None and start_date > end_date):

        # Show an error about the incorrect date range
        st.sidebar.error("The start date must come before the end date.")

        # Stop running the Streamlit app
        st.stop()

    # Show a moving spinner while searching and filtering the records
    with st.spinner("Stand by... Filtering your records."):

        # Create a copy of the watch-history dataframe
        filtered_dataframe = watch_dataframe.copy()

        # Check if the user entered title search text
        if search_text != "":

            # Filter the dataframe using the title search
            filtered_dataframe = filter_by_title(filtered_dataframe, search_text)

        # Check if both dates are available
        if start_date is not None and end_date is not None:

            # Filter the dataframe using the date range
            filtered_dataframe = filter_by_date( filtered_dataframe, start_date, end_date)

    # Get the active app mode
    active_mode = app_state.get("mode", Config.DEMO_MODE)

    # Get the name of the active data file
    active_filename = active_data_path.name

    # Display the active mode and file name
    st.caption(
        f"Mode: {active_mode} | Data file: {active_filename}"
    )

    # Check if no records match the filters
    if filtered_dataframe.empty:

        # Show a warning when the filtered dataframe is empty
        st.warning("No records match the current filters.")

        # Stop running the Streamlit app
        st.stop()

    # Show a moving spinner while building the results and download file
    with st.spinner("Stand by... Preparing your results."):

        # Display the totals for the filtered data
        render_metrics(filtered_dataframe)

        # Add a divider under the totals
        st.divider()

        # Display the data tables
        render_tables(
            filtered_dataframe, controls["recent_limit"])

        # Add a divider under the tables
        st.divider()

        # Convert the filtered dataframe into CSV bytes
        csv_bytes = dataframe_to_csv_bytes(filtered_dataframe)

    # Add a button for downloading the filtered CSV file
    st.download_button( label="Download filtered CSV", data=csv_bytes, file_name="youtube_watch_history.csv", mime="text/csv", width="stretch")


# Check if this file is being run directly
if __name__ == "__main__":

    # Start the main app
    main()
