from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# similar to r6stats

def get_match_data():
    chrome_driver_path = "C:\\Users\\Kaan Keskindil\\OneDrive\\Masaüstü\\1020 Project Files\\r6system\\drivers\\chromedriver-win64\\chromedriver.exe"
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service)

    url = "https://r6.tracker.network/r6siege/profile/ubi/spacelordvoid/matches?playlist=ranked"
    driver.get(url)

    wait = WebDriverWait(driver, 10)

    # map name/time appears next to each other on site
    details = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.text-secondary.text-14.font-medium"))) # css selectors 
    map_info = details.text.strip().split("•")
    map_name = map_info[0].strip()
    timestamp = map_info[1].strip()

    # takes the score, green is mine red is opponent team's.
    score_element = driver.find_element(By.XPATH, "//div[contains(@class, 'p-stat') and contains(@class, 'grid')]//span[@class='text-green']")
    score_green = score_element.text.strip()
    score_red = score_element.find_element(By.XPATH, "following-sibling::span[@class='text-red']").text.strip()
    score = f"{score_green}:{score_red}"

    # take the kd of the match
    kd_element = driver.find_element(By.XPATH, "//span[text()='KD']/following-sibling::span")
    kd = kd_element.text.strip()

    # HS %
    hs_element = driver.find_element(By.XPATH, "//span[text()='HS %']/following-sibling::span")
    hs = hs_element.text.strip()

    driver.quit()

    # return the data as a dictionary
    return {
        "map_name": map_name,
        "timestamp": timestamp,
        "score": score,
        "kd": kd,
        "hs": hs
    }


# Example - used for discord
match_data = get_match_data()
print(f"Map Name: {match_data['map_name']}")
print(f"Timestamp: {match_data['timestamp']}")
print(f"Score: {match_data['score']}")
print(f"KD: {match_data['kd']}")
print(f"HS %: {match_data['hs']}")
