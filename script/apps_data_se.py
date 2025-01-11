from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from script.utils import save_to_csv, extract_keywords, get_text_from_html

def create_driver():
    """
    Create and configure a Selenium WebDriver instance for headless Chrome.

    Returns:
    webdriver: A configured Selenium WebDriver instance.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scrape_play_store_app_details(driver, app_url, category):
    """
    Scrape app details from the Google Play Store.

    Parameters:
    driver (webdriver): Selenium WebDriver instance.
    app_url (str): URL of the app on the Play Store.
    category (str): Category of the app.

    Returns:
    dict: A dictionary containing app details such as category, title, downloads, last update,
          developer information, app URL, keywords, and summary.
    """
    driver.get(app_url)
    time.sleep(3)
    
    details = {
        "genre" : category,
    }

    try:
        details["title"] = driver.find_element(By.XPATH, '//div[contains(@class, "Fd93Bb")]//h1//span[@itemprop="name"]').text
    except:
        details["title"] = "N/A"

    try:
        outer_html = driver.find_element(By.XPATH, '//div[@class="wVqUob"]/div[contains(text(), "+")]').get_attribute('outerHTML')
        details["realInstalls"] = get_text_from_html(outer_html)
    except:
        details["realInstalls"] = "N/A"

    try:
        details["lastUpdatedOn"] = driver.find_element(By.XPATH, '//div[div[text()="Updated on"]]/div[@class="xg1aie"]').text
    except:
        details["lastUpdatedOn"] = "N/A"

    try:
        details["developerWebsite"] = driver.find_element(
            By.XPATH, '//a[contains(@href, "http") and contains(@aria-label, "Website")]'
            ).get_attribute("href")
    except:
        details["developerWebsite"] = "N/A"

    try:
        outer_html = driver.find_element(By.XPATH, '//div[@class="HhKIQc"]/div[contains(text(), "@")]').get_attribute('outerHTML')
        details["developerEmail"] = get_text_from_html(outer_html)
    except:
        details["developerEmail"] = "N/A"

    try:
        outer_html = driver.find_element(
                By.XPATH, '//div[@class="HhKIQc"]/div[starts-with(text(), "+")]'
            ).get_attribute('outerHTML')
        details["developerPhone"] = get_text_from_html(outer_html)
    except:
        details["developerPhone"] = "N/A"

    try:
        outer_html = driver.find_element(
                By.XPATH, '//div[@class="HhKIQc"]/div[@class="mHsyY"]'
            ).get_attribute('outerHTML')

        details['developer_address'] = get_text_from_html(outer_html)
    except:
        details["developerAddress"] = "N/A"

    details["url"] = app_url

    try:
        outer_html = driver.find_element(By.XPATH, '//div[contains(@class, "bARER")]').get_attribute('outerHTML')
        summary = get_text_from_html(outer_html)
    except:
        summary = ""

    details["keywords"] = extract_keywords(summary)

    try:
        outer_html = driver.find_element(By.XPATH, '//div[contains(@class, "bARER")]').get_attribute('outerHTML')
        details['summary'] = get_text_from_html(outer_html)
    except:
        details["summary"] = "N/A"
    
    # Return details in the required order
    return {
        "Category": details.get("genre", ""),
        "App name": details.get("title", ""),
        "Downloads no.": details.get("realInstalls", ""),
        "Last update": details.get("lastUpdatedOn", ""),
        "Developer website": details.get("developerWebsite", ""),
        "Developer email": details.get("developerEmail", ""),
        "Developer phone": details.get("developerPhone", ""),
        "Developer address": details.get("developerAddress", ""),
        "App URL": details.get("url", ""),
        "Keywords": details.get("keywords", ""),
        "Short Description": details.get("summary", "")
    }

def scrape_play_store(category, country_code):
    """
    Scrape app data from the Google Play Store for a given category and country.

    Parameters:
    category (str): The app category to scrape (e.g., "GAME", "EDUCATION").
    country_code (str): The country code for localized app data (e.g., "US", "IN").

    Returns:
    list of dict: A list of dictionaries, each containing app details.
    """
    driver = create_driver()
    category, country_code = category.upper(), country_code.upper()

    try:
        url = f"https://play.google.com/store/apps/category/{category}?gl={country_code}"
        driver.get(url)
        time.sleep(3)

        scroll_pause_time = 2
        app_links = set()
        for _ in range(20):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)

            apps = driver.find_elements(By.XPATH, '//a[@href and contains(@href, "/store/apps/details?id=")]')
            
            for app in apps:
                link = app.get_attribute("href")
                app_links.add(link)
            break

        app_details = [scrape_play_store_app_details(driver, link, category) for link in list(app_links)]
        return [details for details in app_details if details]

    finally:
        driver.quit()

def get_apps_data(category, country_code):
    """
    Retrieve app data from the Google Play Store and save it to a CSV file.

    Parameters:
    category (str): The app category to scrape (e.g., "GAME", "EDUCATION").
    country_code (str): The country code for localized app data (e.g., "US", "IN").

    Returns:
    str: The absolute file path of the saved CSV file.
    """
    apps_data = scrape_play_store(category, country_code)
    output_file = f"{category.replace(' ', '_').lower()}__{country_code}_file.csv"
    file_path = save_to_csv(output_file, apps_data)
    return file_path


if __name__ == "__main__":
    category = "MEDICAL" 
    country_code = "AE"
    
    file = get_apps_data(category, country_code)
    print("Data stored successfully in ", file)
    
