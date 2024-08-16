import pandas as pd
import re
import warnings
warnings.filterwarnings("ignore")

# Function to determine the safety level based on counts
def get_safety_level(fatal_count, non_fatal_count):
    '''
    if fatal_count < 10:
        safety_message = "Your neighborhood is safe! There have been very few crimes reported this year -"
    elif 10 <= fatal_count < 30:
        safety_message = "Your neighborhood is moderately safe! There have been some crimes reported this year -"
    elif 30 <= fatal_count < 60:
        safety_message = "Your neighborhood is moderately unsafe! There have been some crimes reported this year -"
    else:
        safety_message = "Your neighborhood is unsafe! Try looking for another place!"
    return safety_message
    '''
    if fatal_count < 10:
        safety_message = "safe"
    elif 10 <= fatal_count < 30:
        safety_message = "moderately safe"
    elif 30 <= fatal_count < 60:
        safety_message = "moderately unsafe"
    else:
        safety_message = "unsafe"
    return safety_message

def find_safety_level(search_string):
    # Step 1: Read data from a CSV file
    # Replace 'CrimeDataPitt.csv' with the actual path to your CSV file
    data = pd.read_csv('CrimeDataPitt.csv')

    # Step 2: Define the search string (case-insensitive and partial matching)

    # Step 3: Perform case-insensitive and partial matching using regular expression
    pattern = re.compile(re.escape(search_string), re.IGNORECASE)
    filtered_df = data[data["LOCATION"].str.contains(pattern)]

    # Check if there is any data for the specified location
    if filtered_df.empty:
        safety_message = "NA"
        #print("No crime data available for the specified location. Try entering a nearby street.")
    else:
        # Step 4: Create a mapping of call types to categories
        call_type_mapping = {
            "Aggravated Assault": "Fatal",
            "Arson": "Fatal",
            "Homicide": "Fatal",
            "Shooting (Non Fatal)": "Fatal",
            "Theft": "Non-Fatal",
            "Theft from Vehicle": "Non-Fatal",
            "Vehicle Theft": "Non-Fatal",
            "Burglary": "Non-Fatal",
            "Robbery": "Non-Fatal"
        }

        # Step 5: Create a copy of the filtered DataFrame
        filtered_df_copy = filtered_df.copy()

        # Step 6: Add a new column "Category" to the copy based on the mapping
        filtered_df_copy["Category"] = filtered_df_copy["CALL_TYPE_FINAL"].map(call_type_mapping)

        # Step 7: Group by "Category" and count the rows
        result = filtered_df_copy.groupby("Category").size().reset_index(name="COUNT")

        # Step 8: Determine the safety level based on counts
        fatal_count = result[result["Category"] == "Fatal"]["COUNT"].values[0] if "Fatal" in result["Category"].values else 0
        non_fatal_count = result[result["Category"] == "Non-Fatal"]["COUNT"].values[0] if "Non-Fatal" in result["Category"].values else 0

        # Step 9: Determine the safety level and get the safety message
        safety_message = get_safety_level(fatal_count, non_fatal_count)

        # Step 10: Print the safety message with counts
        #print("\nSafety Message:")
        #print(f"{safety_message} {fatal_count} fatal and {non_fatal_count} non-fatal.")
        
        # Step 11: Provide information about what is considered fatal and non-fatal
        #print("\nDefinition:")
        #print("A 'fatal' incident includes Aggravated Assault, Arson, Homicide, and Shooting (Non Fatal).")
        #print("A 'non-fatal' incident includes Theft, Theft from Vehicle, Vehicle Theft, Burglary, and Robbery.")

        # Step 12: Get a count breakup   
        count_breakup = filtered_df_copy.groupby("CALL_TYPE_FINAL").size().reset_index(name="COUNT")
        #print(count_breakup)

        return safety_message

