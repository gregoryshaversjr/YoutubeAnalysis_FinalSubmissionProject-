# Import Python tools for working with JSON data
import json

# Import the Config class containing the app's file paths and modes
from config import Config


# Make sure the app's data folder exists
def ensure_data_folder():

    # Get the data folder path from the configuration
    data_folder = Config.DATA_DIR

    # Create the data folder and any missing parent folders
    data_folder.mkdir(parents=True, exist_ok=True)

    # Return the data folder path
    return data_folder


# Save a file uploaded by the user
def save_uploaded_file(uploaded_file):

    # Make sure the data folder exists before saving the file
    ensure_data_folder()

    # Check if the uploaded file has a getvalue method
    if hasattr(uploaded_file, "getvalue"):

        # Get all the uploaded file data as bytes
        uploaded_bytes = uploaded_file.getvalue()

    # Run this if the file does not have a getvalue method
    else:

        # Read the uploaded file data as bytes
        uploaded_bytes = uploaded_file.read()

    # Get the path where the uploaded file will be saved
    uploaded_data_path = Config.UPLOADED_DATA_PATH

    # Write the uploaded bytes to the file
    uploaded_data_path.write_bytes(uploaded_bytes)

    # Return the path of the saved file
    return uploaded_data_path


# Load the previously saved app state
def load_app_state():

    # Create the default state using demo mode
    default_state = {"mode": Config.DEMO_MODE}

    # Get the path of the app state file
    app_state_path = Config.APP_STATE_PATH

    # Check if the app state file does not exist
    if not app_state_path.exists():

        # Return the default state when there is no saved state
        return default_state

    # Try to read and convert the saved state
    try:

        # Read the app state file as text
        state_text = app_state_path.read_text(encoding="utf-8")

        # Convert the JSON text into a Python object
        app_state = json.loads(state_text)

    # Catch file errors or invalid JSON data
    except (OSError, json.JSONDecodeError):

        # Return the default state if the saved state cannot be loaded
        return default_state

    # Check that the saved app state is a dictionary
    if not isinstance(app_state, dict):

        # Return the default state if it is not a dictionary
        return default_state

    # Get the saved mode from the app state
    saved_mode = app_state.get("mode")

    # Create a list of modes that the app accepts
    valid_modes = [Config.DEMO_MODE, Config.UPLOADED_MODE]

    # Check whether the saved mode is invalid
    if saved_mode not in valid_modes:

        # Return the default state when the saved mode is invalid
        return default_state

    # Return a dictionary containing the valid saved mode
    return {"mode": saved_mode}


# Save the current app mode
def save_app_state(mode):

    # Get the demo mode value from the configuration
    demo_mode = Config.DEMO_MODE

    # Get the uploaded mode value from the configuration
    uploaded_mode = Config.UPLOADED_MODE

    # Create a list of modes that can be saved
    valid_modes = [demo_mode, uploaded_mode]

    # Check if the provided mode is not valid
    if mode not in valid_modes:

        # Stop the function and raise an error for an invalid mode
        raise ValueError("The app mode must be 'demo' or 'uploaded'.")

    # Make sure the data folder exists
    ensure_data_folder()

    # Store the selected mode in a dictionary
    app_state = {"mode": mode}

    # Convert the app state dictionary into formatted JSON text
    state_text = json.dumps(app_state, indent=2)

    # Get the path of the app state file
    app_state_path = Config.APP_STATE_PATH

    # Write the JSON text to the app state file
    app_state_path.write_text(state_text, encoding="utf-8")

    # Return the saved app state
    return app_state


# Delete the uploaded data and switch the app back to demo mode
def clear_uploaded_data():

    # Get the path of the uploaded data file
    uploaded_data_path = Config.UPLOADED_DATA_PATH

    # Check if the uploaded data file exists
    if uploaded_data_path.exists():

        # Delete the uploaded data file
        uploaded_data_path.unlink()

    # Save demo mode as the current app state
    app_state = save_app_state(Config.DEMO_MODE)

    # Return the updated app state
    return app_state


# Get the path of the data file the app should currently use
def get_active_data_path(app_state):

    # Check if the provided app state is a dictionary
    if isinstance(app_state, dict):

        # Get the saved mode from the app state
        saved_mode = app_state.get("mode")

    # Run this when the app state is not a dictionary
    else:

        # Use no saved mode when the app state is invalid
        saved_mode = None

    # Get the path of the uploaded data file
    uploaded_data_path = Config.UPLOADED_DATA_PATH

    # Get the path of the demo watch-history file
    demo_data_path = Config.WATCH_HISTORY_PATH

    # Check whether the uploaded data file exists
    upload_exists = uploaded_data_path.exists()

    # Check if uploaded mode is active and an uploaded file exists
    if saved_mode == Config.UPLOADED_MODE and upload_exists:

        # Return the uploaded data file path
        return uploaded_data_path

    # Return the demo data file path
    return demo_data_path


# Convert a dataframe into downloadable CSV bytes
def dataframe_to_csv_bytes(dataframe):

    # Convert the dataframe into CSV text without row indexes
    csv_text = dataframe.to_csv(index=False)

    # Convert the CSV text into UTF-8 bytes
    csv_bytes = csv_text.encode("utf-8")

    # Return the CSV data as bytes
    return csv_bytes