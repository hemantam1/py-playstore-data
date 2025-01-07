from google_play_scraper import app, search
from sklearn.feature_extraction.text import CountVectorizer
import csv

def fetch_app_details(package_name):
    """
    Fetch details of an app given its package name.
    """
    try:
        details = app(package_name)
        description = details.get("description", "")
        return {
            "Cateory": details.get("genre", ""),
            "App name": details.get("title", ""),
            "Downloads no.": details.get("realInstalls", ""),
            "Last update": details.get("lastUpdatedOn", ""),
            "Developer website": details.get("developerWebsite", ""),
            "Developer email": details.get("developerEmail", ""),
            "Developer phone": details.get("developerPhone", ""), #Not available
            "App URL": details.get("url", ""),
            "Keywords": extract_keywords(description), #Not available
            "Short Description": details.get("summary", ""),
        }
    except Exception as e:
        print(f"Error fetching details for {package_name}: {e}")
        return None

def fetch_apps_by_category(category, country, num_results):
    """
    Fetch apps from the Play Store for a specific category and country.
    """
    try:
        apps = search(
            query=category,
            lang="en",
            country=country,
            n_hits=num_results,
        )
        app_details = [fetch_app_details(app["appId"]) for app in apps]
        return [details for details in app_details if details]
    except Exception as e:
        print(f"Error fetching apps by category: {e}")
        return []
    
def extract_keywords(text, top_n=5):
    """
    Extract top-n keywords from the given text using CountVectorizer.
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
    
def save_to_csv(file_name, data):
    """
    Save data to a CSV file.
    """
    if not data:
        print("No data to save.")
        return

    # Get the headers from the first data entry
    headers = data[0].keys()

    try:
        with open(file_name, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        print(f"Data saved to {file_name}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

if __name__ == "__main__":
    category = "Food & Drink"
    country = "qa"
    num_results = 5

    print(f"Fetching top {num_results} apps in category '{category}' for country code '{country}'...")
    apps_data = fetch_apps_by_category(category, country, num_results)

    output_file = "playstore_apps.csv"
    save_to_csv(output_file, apps_data)
