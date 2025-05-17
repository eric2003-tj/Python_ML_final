import os
import time
import csv
import pickle
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ========== Step 1: 設定 Chrome WebDriver ==========
webdriver_path = "/opt/homebrew/bin/chromedriver"
service = Service(webdriver_path)
options = Options()
# options.add_argument('--headless')  # 若需背景執行可取消註解
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-infobars")
options.add_argument("--start-maximized")
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=service, options=options)

# ========== Step 2: Cookies 自動登入邏輯 ==========
COOKIES_FILE = "twitter_cookies.pkl"

def save_cookies():
    with open(COOKIES_FILE, "wb") as f:
        pickle.dump(driver.get_cookies(), f)

def load_cookies():
    if not os.path.exists(COOKIES_FILE):
        return False
    driver.get("https://x.com")
    with open(COOKIES_FILE, "rb") as f:
        cookies = pickle.load(f)
    for cookie in cookies:
        if "expiry" in cookie:
            del cookie["expiry"]
        driver.add_cookie(cookie)
    driver.refresh()
    return True

def login_and_save():
    driver.get("https://x.com/login")
    print("🔐 請手動登入 Twitter（輸入帳號、密碼、驗證碼）...")
    input("👉 登入成功後，請回到終端機按下 Enter 鍵儲存 cookie：")
    save_cookies()
    print("✅ Cookies 已儲存，下次將自動登入")

if not load_cookies():
    login_and_save()
else:
    print("✅ Cookies 已載入，自動登入成功")

# ========== Step 3: 抓取特定日期的推文 ==========
# 修改這裡的日期範圍
since = "2025-04-15"
until = "2025-04-16"
target_url = f"https://x.com/search?q=tariff%20until%3A{until}%20since%3A{since}&src=typed_query"
driver.get(target_url)
time.sleep(5)

# ========== Step 4: 滾動並擷取推文 ==========
scroll_pause_time = 3
all_tweet_data = []
processed_tweets = set()
count = -1

while len(processed_tweets) != count:
    count = len(processed_tweets)
    try:
        article_elements = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    except:
        break
    if not article_elements:
        print("❗ 沒有找到更多推文，停止抓取")
        break

    for article in article_elements:
        try:
            tweet_text_element = article.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
            tweet_text = tweet_text_element.text
            if tweet_text in processed_tweets:
                continue
            processed_tweets.add(tweet_text)

            time_element = article.find_element(By.XPATH, './/a/time')
            timestamp_str = time_element.get_attribute('datetime')

            all_tweet_data.append({
                'Timestamp': timestamp_str,
                'Tweet Content': tweet_text,
            })

        except Exception as e:
            print(f"⚠️ 抓取推文時發生錯誤: {e}")
            continue

    driver.execute_script("window.scrollBy(0, 3000);")
    time.sleep(scroll_pause_time)

# ========== Step 5: 儲存至 CSV ==========
date_str = since
csv_file_path = f'tariff_data{date_str.replace("-", "")}.csv'

try:
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Timestamp', 'Tweet Content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in all_tweet_data:
            writer.writerow(data)
    print(f"📁 已儲存推文至：{csv_file_path}（共 {len(all_tweet_data)} 則）")
except Exception as e:
    print(f"❌ 儲存失敗：{e}")

# ========== Step 6: 關閉瀏覽器 ==========
driver.quit()
