from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re  # imported specifically to check for numeric values
from selenium.common.exceptions import StaleElementReferenceException

# rest of the imports are selenium additions I found while struggling with my list of long stack errors and searching up fixes for particular situations like mine
# i will add comments on parts i think are worth explaning
def scrape_r6_tracker():
    USERNAME = "spacelordvoid"
    PLATFORM = "ubi"
    url = f"https://r6.tracker.network/r6siege/profile/{PLATFORM}/{USERNAME}/overview"

    chrome_driver_path = r"C:\Users\Kaan Keskindil\OneDrive\Masaüstü\1020 Project Files\r6system\drivers\chromedriver-win64\chromedriver.exe"

    service = Service(chrome_driver_path) 
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Runs without opening a browser window/ works since url not dynamic
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36") # header to mimic actual search

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url) # load url

    try:
        wait = WebDriverWait(driver, 20)  # wait time

        # functions that look for a specific css selector; got these from inspect element and tried a bunch of different spans near what I wanted until it worked - the rank part was way easier
        try:
            rank_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".rank-image")))
            rank = rank_element.get_attribute("alt").strip()
        except:
            rank = "Unranked"

        # extracts kd value using this try and except loop, 
        try:
            # wait for the specific span containing the KD value to load / had issues with it extracking the playlist 'ranked' and not the 'ranked KD' so tried excluding it, these spans were nested together.
            kd_value_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//span[contains(@class, 'stat-value--text')]/span[not(contains(text(), 'Ranked'))]"))
            )

            # take the kd +  removes leading/trailing spaces
            kd_value = kd_value_element.text.strip()

            # ensure it's a numeric value that matches the site format like '.59' <- my kd
            if re.match(r'^\d+\.\d+$', kd_value):
                kd = float(kd_value)
            else:
                kd = 0.0

        except Exception as e:
            print(f"KD extraction error: {e}")
            kd = 0.0

        driver.quit() # and then stop

        return {
            "rank": rank,
            "kd": kd # returns as dict
        }

    except Exception as e:
        driver.quit()
        print(f"Error: {str(e)}")
        return None


def get_stats(output_format='dict', return_format=None): # dict for website string for arduino function - i know i could've stayed consistent but i got lazy
    format_type = return_format if return_format is not None else output_format # in either case i call out the function specifically with dict/string so it knows which one to use
    
    try:
        raw_stats = scrape_r6_tracker() or {} # empty dict if it fails
        print("Raw stats:", raw_stats)  # Debug
        
        # ensure kd is always float
        kd = float(raw_stats.get('kd', 0.0))
        
        # format output
        if format_type == 'string':
            return f"Rank: {raw_stats.get('rank', 'Unknown')}\nKD: {kd:.2f}"
        #dict version
        return {
            'rank': str(raw_stats.get('rank', 'Unknown')),
            'kd': kd,
            'kd_ratio': kd  # a secret third option that i accidentally put down in another function and added here to match it- got lazy again ooops
        }
        
    except Exception as e:
        print(f"Error: {e}")
        if format_type == 'string':
            return "Rank: Error\nKD: 0.00"
        return {'rank': 'Error', 'kd': 0.0, 'kd_ratio': 0.0}
