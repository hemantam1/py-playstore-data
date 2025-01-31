import csv
import os
from sklearn.feature_extraction.text import CountVectorizer

def get_text_from_html(html):
    """
    Extract text content from an HTML string.

    Parameters:
    html (str): The HTML string to extract text from.

    Returns:
    str: The extracted text content, with leading and trailing whitespace removed.
    """
    start = html.find('>') + 1
    end = html.rfind('</div>')
    return html[start:end].strip()

def save_to_csv(file_name, data):
    """
    Save a list of dictionaries to a CSV file.

    Parameters:
    file_name (str): The name of the CSV file to save data to.
    data (list of dict): The data to save, where each dictionary represents a row in the CSV file.

    Returns:
    str: The absolute file path of the saved CSV file, or None if an error occurs.
    """
    if not data:
        print("No data to save.")
        return None
    
    # Ensure the 'data' folder exists
    folder_name = "data"
    os.makedirs(folder_name, exist_ok=True)

    # Construct the full file path
    file_name = os.path.join(folder_name, file_name)
    full_file_path = os.path.abspath(file_name)
    # Get the headers from the first data entry
    headers = data[0].keys()

    try:
        with open(file_name, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        print(f"Data saved to {file_name}")
        return full_file_path
    except Exception as e:
        print(f"Error saving data to CSV: {e}")
        return None
    
def append_to_csv(file_name, data):
    """
    Append a list of dictionaries or a single dictionary to a CSV file.

    Parameters:
    file_name (str): The name of the CSV file to append data to.
    data (dict or list of dict): The data to append. Can be a single dictionary or a list of dictionaries.

    Returns:
    None
    """
    if not data:
        print("No data to append.")
        return

    # Ensure the 'temp_data' folder exists
    folder_name = "temp_data"
    os.makedirs(folder_name, exist_ok=True)

    # Construct the full file path
    file_name = os.path.join(folder_name, file_name)

    # Normalize data to a list of dictionaries
    if isinstance(data, dict):
        data = [data]  # Wrap single dictionary in a list
    
    # Get the headers from the first dictionary in the list
    headers = data[0].keys()

    try:
        # Check if the file already exists
        file_exists = os.path.isfile(file_name)
        
        with open(file_name, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            
            # Write the header only if the file is being created
            if not file_exists:
                writer.writeheader()
            
            # Append the data rows
            writer.writerows(data)
    except Exception as e:
        print(f"Error appending data to CSV: {e}")
    
def extract_keywords(text, top_n=15):
    """
    Extract the top-n keywords from a given text using CountVectorizer.

    Parameters:
    text (str): The text to extract keywords from.
    top_n (int): The maximum number of keywords to extract (default is 15).

    Returns:
    str: A comma-separated string of the top-n keywords, or an empty string if an error occurs.
    """
    if not text:
        return ""
    try:
        vectorizer = CountVectorizer(max_features=top_n, stop_words="english")
        X = vectorizer.fit_transform([text])
        keywords = vectorizer.get_feature_names_out()
        return ", ".join(keywords)
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return ""