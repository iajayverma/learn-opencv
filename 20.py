from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


class GoogleReviewsScraper:
    def __init__(self, hospital_name):
        self.hospital_name = hospital_name
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.wait = WebDriverWait(self.driver, 20)


    def navigate_to_reviews(self):
        search_url = f"https://www.google.com/search?q={self.hospital_name.replace('','+')}+reviews"
        self.driver.get(search_url)
        try:
            reviews_link = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-fid="0x3bcb947fdee4f5a1:0x2ca09b4d2e3a79f"][data-sort_by="qualityScore"][data-async-trigger="reviewDialog"]')))
            reviews_link.click()
            print("Successfully navigated to the reviews page.")
        except Exception as e:
            print("Could not navigate to the reviews page:", e)
            self.driver.quit()

    def load_all_reviews(self):
            try:
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                while True:
                    self.driver.execute_script("window.scrollBy(0, 1000000);")  # Scroll down by 1000 pixels
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.BgXiYe')))
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
            except Exception as e:
                print("Could not load more reviews:", e)


    def extract_reviews(self):
        self.reviews = []
        try:
            review_elements = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.gQfZge .BgXiYe .Jtu6Td')))
            print(f"Found {len(review_elements)} review elements.")
            for element in review_elements:
                try:
                    review_snippet = element.find_element(By.CSS_SELECTOR, '.Jtu6Td span').text
                    try:
                        more_link = element.find_element(By.CSS_SELECTOR, '.review-more-link')
                        more_link.click()
                        time.sleep(1)
                        review_text = element.find_element(By.CSS_SELECTOR, '.Jtu6Td').text
                    except Exception:
                        review_text = review_snippet
                    self.reviews.append({
                        'review': review_text
                    })
                except Exception as e:
                    print("Could not extract review,Error extracting details for one review:", e)
        except Exception as e:
            print("Could not extract reviews:", e)

    

    def save_reviews_to_json(self, filename='hospital_reviews_2.json'):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.reviews, file, ensure_ascii=False, indent=4)
        # print(f"Saved reviews to {filename}")

    def close_driver(self):
        self.driver.quit()
        # print("Driver closed.")

    def run_scraper(self):
        self.navigate_to_reviews()
        self.load_all_reviews()
        self.extract_reviews()
        # self.save_reviews_to_json()
        self.close_driver()
        return self.reviews


if __name__ == "__main__":
    # hospital_name = input("Enter the name of the hospital: ")
    scraper = GoogleReviewsScraper("Continental Hospital Hyderabad")
    reviews = scraper.run_scraper()
    scraper.save_reviews_to_json()
    print(f"Saved {len(reviews)} reviews to hospital_reviews.json")
