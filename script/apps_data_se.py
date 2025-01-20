from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from script.utils import save_to_csv, extract_keywords, get_text_from_html, append_to_csv
recursion_limit = 2
num = 0

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

def scrape_play_store_app_details(driver, app_url, category, country_code):
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
                By.XPATH, '//div[@class="HhKIQc"]/div[contains(text(), "+")]'
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

    try:
        details['rating'] = driver.find_element("xpath", '//div[@class="TT9eCd"]').text
    except:
        details["rating"] = "N/A"

    try:
        details['reviews'] = driver.find_element("xpath", '//div[@class="g1rdde" and text()[contains(., "reviews")]]').text
    except:
        details["reviews"] = "N/A"

    try:
        details['rated_for'] = driver.find_element("xpath", '//span[@itemprop="contentRating"]/span').text
    except:
        details["rated_for"] = "N/A"

    try:
        details['app_icon'] = driver.find_element("xpath", '//img[contains(@class, "T75of")]').get_attribute("src")
    except:
        details["app_icon"] = "N/A"
    
    # Return details in the required order
    data = {
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
        "Short Description": details.get("summary", ""),
        "Rating": details.get("rating", ""),
        "Review Count": details.get("reviews", ""),
        "Rated for": details.get("rated_for", ""),
        "App icon": details.get("app_icon", "")
    }
    global num
    print("num: ", num)
    num += 1
    file_name = f"{category}_{country_code}_file.csv"
    append_to_csv(file_name, data)
    return data

def get_similar_apps(driver, app_url, category, country_code):
    """
    Get the list of similar app URLs from the Play Store.

    Parameters:
    driver (webdriver): Selenium WebDriver instance.
    app_url (str): URL of the app on the Play Store.

    Returns:
    list: List of similar app URLs.
    """
    driver.get(app_url)
    time.sleep(2)
    similar_app_links = set()
    
    try:
        similar_apps = driver.find_elements(By.XPATH, '//a[@href and contains(@href, "/store/apps/details?id=")]')
        for app in similar_apps:
            link = app.get_attribute("href")
            if "details?id=" in link:
                    similar_app_links.add(link)
        
    except Exception as e:
        print(f"Error fetching similar apps for {app_url}: {e}")
    
    return list(similar_app_links)

def scrape_play_store_with_similar_apps(driver, app_url, category, visited_urls, country_code, count):
    """
    Recursively scrape app details and their similar apps.

    Parameters:
    driver (webdriver): Selenium WebDriver instance.
    app_url (str): URL of the app on the Play Store.
    category (str): Category of the app.
    visited_urls (set): Set of already visited app URLs to avoid duplicates.

    Returns:
    list: List of app details with their similar apps.
    """
    global recursion_limit
    
    app_details_list = []
    if recursion_limit <= 0:
        recursion_limit = 1
        return app_details_list
    recursion_limit -= 1
        
    if count > 1 and app_url in visited_urls:
        return app_details_list

    visited_urls.add(app_url)
    print(f"Scraping details for {app_url}...")
    print(f"Total visited urls: ", len(visited_urls))
    
    # Scrape app details
    app_details = scrape_play_store_app_details(driver, app_url, category, country_code)
    app_details_list.append(app_details)
    
    # Get similar apps
    similar_apps = get_similar_apps(driver, app_url, category, country_code)
    for similar_app_url in similar_apps:
        if similar_app_url not in visited_urls:
            # Recursive call for each similar app
            app_details_list.extend(scrape_play_store_with_similar_apps(driver, similar_app_url, category, visited_urls, country_code, count=count+1))
    
    return app_details_list

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
    visited_urls = set()
    visited_apps = set()
    try:
        url = f"https://play.google.com/store/apps/category/{category}?gl={country_code}"
        driver.get(url)
        time.sleep(2)

        tabs = driver.find_elements(By.XPATH, '//div[contains(@class, "Gggmbb")]')
        if len(tabs) != 3:
            raise Exception(f"Please check your category: {category} and country_code: {country_code}")
        # Map the tab names to their corresponding indices
        tab_mapping = {
            "top_free": 0,
            "top_grossing": 1,
            "top_paid": 2,
        }
        
        app_links = set()
        for tab_name, index in tab_mapping.items():
            driver.execute_script("arguments[0].click();", tabs[index])
            time.sleep(2)

            apps = driver.find_elements(By.XPATH, '//a[@href and contains(@href, "/store/apps/details?id=")]')
            for app in apps:
                app_links.add(app.get_attribute("href"))

        all_apps_details = []

        # here app_links contains all the apps-links of top-free, top-grossing and top-paid tab
        for app_url in app_links:
            app_details = scrape_play_store_app_details(driver, app_url, category, country_code)
            all_apps_details.append(app_details)
            # visited_apps.add(app_details.get("App name"))
            visited_urls.add(app_url)

        # here all_apps_details contains all the apps-details of top-free, top-grossing and top-paid tab
        for app_url in app_links:
            count = 1
            all_apps_details.extend(scrape_play_store_with_similar_apps(driver, app_url, category, visited_urls, country_code, count))
            # similar_apps = get_similar_apps(driver, app_url, category, country_code)
            # for similar_app_url in similar_apps:
            #     if similar_app_url not in visited_urls:
            #         # Recursive call for each similar app
            #         all_apps_details.extend(scrape_play_store_with_similar_apps(driver, similar_app_url, category, visited_urls, country_code, count))


            # all_apps_details.extend(scrape_play_store_with_similar_apps(driver, app_url, category, visited_urls, country_code))
        print("------ALL apps------", len(all_apps_details))
        return all_apps_details

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
    category = "health_and_fitness" 
    country_code = "ae"
    
    file = get_apps_data(category, country_code)
    print("Data stored successfully in ", file)
    
