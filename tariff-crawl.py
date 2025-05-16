from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv
from datetime import datetime, timezone

# ========== 步驟 1: 設定 Chrome WebDriver ==========
webdriver_path = "/opt/homebrew/bin/chromedriver"  # chrome driver 
service = Service(webdriver_path)
options = Options()
# options.add_argument('--headless')

driver = webdriver.Chrome(service=service, options=options)

# ========== 步驟 2: 設定你的 Twitter 帳號資訊 ==========
username = ''  # <--- 請填寫你的 Twitter 帳號
password = ''  # <--- 請填寫你的 Twitter 密碼

# ========== 步驟 3: 登入 Twitter (如果需要) ==========
def login_twitter():
    driver.get('https://x.com/login')
    time.sleep(2)

    username_input = driver.find_element(By.NAME, 'text')
    username_input.send_keys(username)
    time.sleep(1)

    try:
        next_button = driver.find_element(By.XPATH, '//button[@role="button"]//span[text()="下一步"]')
        next_button.click()
        time.sleep(2)
    except Exception as e:
        print(f"找不到 '下一步' 按鈕: {e}")
        return

    password_input = driver.find_element(By.NAME, 'password')
    password_input.send_keys(password)
    login_button = driver.find_element(By.XPATH, '//button[@role="button"]//span[text()="登入"]')
    login_button.click()
    time.sleep(5)
login_twitter() 

# ========== 步驟 4: 前往目標用戶的推特頁面 ==========
target_url = 'https://x.com/search?q=tariff%20until%3A2025-03-21%20since%3A2025-03-20&src=typed_query' #選擇日期
driver.get(target_url)
time.sleep(5)

# ========== 步驟 5: 滾動頁面並抓取推文資訊 (滾動到特定時間) ==========
scroll_pause_time = 3  # 每次滾動後等待的時間

all_tweet_data = []
processed_tweets = set()
count=-1

while len(processed_tweets)!=count:
    count=len(processed_tweets)
    try:
        # 定位每一則推文的容器
        article_elements = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    except:
        break
    if not article_elements:
        print("沒有找到更多推文，停止抓取。")
        break

    for article in article_elements:
        try:
            # 抓取推文內容
            tweet_text_element = article.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
            tweet_text = tweet_text_element.text
            processed_tweets.add(tweet_text)
            # 抓取發布時間
            time_element = article.find_element(By.XPATH, './/a/time')
            timestamp_str = time_element.get_attribute('datetime')
            tweet_datetime = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

            all_tweet_data.append({
                'Timestamp': timestamp_str,
                'Tweet Content': tweet_text,
            })

        except Exception as e:
            print(f"抓取推文資訊時發生錯誤: {e}")
            break

    # 滾動一小段距離
    driver.execute_script("window.scrollBy(0, 3000);")
    time.sleep(scroll_pause_time)

# ========== 步驟 6: 將抓取到的推文資訊儲存到 CSV 檔案 ==========
csv_file_path = 'tariff_data0320.csv'

try:
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Timestamp', 'Tweet Content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for data in all_tweet_data:
            writer.writerow(data)
    print(f"推文詳細資訊已儲存到: {csv_file_path}")
except Exception as e:
    print(f"儲存 CSV 檔案時發生錯誤: {e}")

# ========== 步驟 7: 關閉瀏覽器 ==========
driver.quit()

